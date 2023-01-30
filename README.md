# s-ul-downloader

Primitive s-ul.eu scraper for downloading an archive of your files from s-ul.eu.

This is a HTML-based scraper and is sensitive to changes in the HTML structure of the site. It is not guaranteed to work 
in the future.

Only does the root directory.

## Usage

Requires Node.js v16 or higher.

```shell
git clone https://github.com/Lemmmy/s-ul-downloader.git
cd s-ul-downloader
yarn install

COOKIE="your s-ul.eu cookie" CONCURRENCY=8 node .
```

- The `COOKIE` environment variable is required. It begins with `s-ul=`.
- The `CONCURRENCY` environment variable is optional, and defaults to 8.

Files will be downloaded to the `images` directory, with sub-directories for each year and month (e.g. 
`images/2023-01`). The files' modification date will be set to the time the file was originally uploaded to s-ul.

An `images/index.json` file will also be created, containing a map of numeric file IDs to objects like follows:

```json
{
  "55230": {
    "id": "55230",
    "url": "https://lemmmy.s-ul.eu/pdqiLns4",
    "name": "Untitled-1_@_3200%_(RGB16)__2015-08-18_02-50-34.png",
    "title": "2015-08-18 01:50:34<br />Hits: 3",
    "date": "2015-08-18 01:50:34",
    "size": "97.04 KB"
  }
}
```

## License

This project is licensed under the MIT license. See the [LICENSE](LICENSE) file for more details.
