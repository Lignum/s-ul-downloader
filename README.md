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
`images/2023-01`).

## License

This project is licensed under the MIT license. See the [LICENSE](LICENSE) file for more details.
