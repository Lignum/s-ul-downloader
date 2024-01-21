import json
import sys
import logging
import traceback

from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Any
from flask import Flask, Blueprint, send_file, jsonify, abort
from werkzeug.exceptions import HTTPException, InternalServerError
from pathlib import Path
from urllib.parse import urlparse
from datetime import date, datetime

ROUTE_PREFIX = "/archive"
IMAGES_PATH = Path("images")
INDEX_PATH = IMAGES_PATH.joinpath("index.json")


@dataclass
class IndexEntry:
  id: str
  url: str
  path: str
  name: str
  date: date
  
  def file_path(self, images_path: Path) -> Path:
    subdir_name = self.date.strftime("%Y-%m")
    return images_path.joinpath(subdir_name).joinpath(self.name)


app = Flask(__name__)
archive_bp = Blueprint("archive", __name__)

image_index: Optional[Dict[str, IndexEntry]] = None

@app.route("/favicon.ico")
def favicon():
  return "404 No favicon", 404


@archive_bp.route("/years")
def list_archived_years():
  global image_index
  
  if image_index is None:
    image_index = parse_index(INDEX_PATH)
  
  years = {entry.date.year for entry in image_index.values()}
  return jsonify(list(years))


@archive_bp.route("/years/<int:year>/months")
def list_archived_months_for_year(year: int):
  global image_index
  
  if image_index is None:
    image_index = parse_index(INDEX_PATH)

  months = {entry.date.month for entry in image_index.values()
                             if  entry.date.year == year}
  return jsonify(list(months))


@archive_bp.route("/years/<int:year>/months/<int:month>")
def list_archived_paths_for_year_and_month(year: int, month: int):
  global image_index
  
  if image_index is None:
    image_index = parse_index(INDEX_PATH)

  paths = [entry.path for entry in image_index.values()
                      if  entry.date.year == year
                      and entry.date.month == month]
  return jsonify(paths)


@archive_bp.route("/<string:path>")
def view_screenshot(path: str):
  global image_index
  
  if image_index is None:
    image_index = parse_index(INDEX_PATH)
  
  entry = image_index[path]
  file_path = entry.file_path(IMAGES_PATH)
  return send_file(file_path)


def parse_index(index_path: Path) -> Optional[Dict[str, IndexEntry]]:
  with index_path.open(encoding="utf8") as index_file:
    try:
      index = json.load(index_file)
    except:
      app.logger.error("index.json is malformed!")
      return None

  if not isinstance(index, dict):
    app.logger.error("index.json is not a JSON object!")
    return None

  output_index: Dict[str, IndexEntry] = {}

  for id in index:
    obj = index[id]

    try:
      try:
        url = str(obj["url"])
        path = urlparse(url).path[1:]
      except ValueError:
        app.logger.warning(f"Could not parse URL '{url}' of entry with ID {id}, skipping...")
        continue
      
      try:
        date_str = str(obj["date"])
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").date()
      except ValueError:
        app.logger.warning(f"Could not parse date '{date_str}' of entry with ID {id}, skipping...")
        continue
      
      name = str(obj["name"])
    except KeyError:
      app.logger.warning(f"Index entry with id {id} is malformed, skipping...")
      continue
    
    output_index[path] = IndexEntry(id, url, path, name, date)
  
  return output_index


@app.errorhandler(HTTPException)
def http_error(error: HTTPException):
  response = f"{error.code} {error.description}"

  if isinstance(error, InternalServerError):
    response += f"\n{error.original_exception}\n"
    response += traceback.format_exc()
    
  return response, error.code


if __name__ == "__main__":
  app.logger.addHandler(logging.StreamHandler())
  app.register_blueprint(archive_bp, url_prefix=ROUTE_PREFIX)
  app.run()