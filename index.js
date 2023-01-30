require("dotenv").config();
const axios = require("axios");
const cheerio = require("cheerio");
const fs = require("fs-extra");
const path = require("path");
const util = require("util");
const stream = require("stream");
const pipeline = util.promisify(stream.pipeline);
const { default: PQueue } = require("p-queue");
const sanitizeFilename = require("sanitize-filename");
const dayjs = require("dayjs");

const metadata = {};

const sul = axios.create({
  baseURL: "https://s-ul.eu",
  headers: {
    Cookie: process.env.COOKIE,
  }
});

const queue = new PQueue({ 
  concurrency: parseInt(process.env.CONCURRENCY || "8")
});

async function fetchPage(n) {
  console.log(`Fetching page ${n}...`)
  const { data } = await sul.get(`files?page=${n}`);
  const $ = cheerio.load(data);

  const links = $("div.row.tr[data-file-id]");

  for (const link of links) {
    const $link = $(link);
    const id = $link.attr("data-file-id");
    const url = $link.attr("data-url");

    const $nameCol = $link.find("div.col-9 div.col-md-6.no-wrap a");
    const name = ($nameCol.text() || null)?.trim();
    const title = $nameCol.attr("title");

    const date = $link.find("div.col-9 div.col-md-4").text();
    const size = $link.find("div.col-9 div.col-md-2.text-md-right").text();

    metadata[id] = {
      id,
      url,
      name,
      title,
      date,
      size
    };

    // Add the download to the queue
    const dateDir = path.join("images", dayjs(date).format("YYYY-MM"));
    await fs.mkdirp(dateDir);
    const destination = path.join(dateDir, sanitizeFilename(name) || id);
    queue.add(() => downloadFile(url, destination));
  }

  // Flush the metadata at the end of each page
  await flushMetadata();

  const $pagination = $("div.row + div.text-center.p-3.mb-3.mb-lg-0.d-flex");
  const $next = $pagination.find("a.btn.btn-secondary:last-child:not(.disabled)");
  if ($next.length) {
    const pageUrl = $next.attr("href");
    return parseInt(pageUrl.match(/page=(\d+)/)[1]);
  } else {
    return -1;
  }
}

async function downloadFile(url, destination) {
  try {
    const res = await sul.get(url, { responseType: "stream" });
    await pipeline(res.data, fs.createWriteStream(destination));
    console.log(`Downloaded ${url} to ${destination}`);
  } catch (err) {
    console.error(`Failed to download ${url} to ${destination}`, err);
  }
}

async function flushMetadata() {
  await fs.writeJSON("images/index.json", metadata);
}

async function main() {
  await fs.mkdirp("images");

  let page = 1;
  do {
    page = await fetchPage(page);
  } while (page !== -1);

  console.log("Finished fetching pages");

  await queue.onIdle();
  console.log("Finished downloading files");
}

main()
  .then(flushMetadata)
  .catch(console.error);
