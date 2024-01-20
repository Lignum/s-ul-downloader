import json
import sys

from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Any
from flask import Flask, send_file
from pathlib import Path
from urllib.parse import urlparse
from datetime import date, datetime


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

image_index: Optional[Dict[str, IndexEntry]] = None
images_path: Optional[Path] = None


@app.route("/<string:path>")
def view_screenshot(path: str):
  assert image_index is not None
  assert images_path is not None
  
  entry = image_index[path]
  file_path = entry.file_path(images_path)
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


def parse_arguments(args: List[str]) -> Tuple[Path, Path]:
  if len(args) < 2:
    app.logger.error(f"Usage: {args[0]} [images directory]")
    exit(1)
  
  try:
    images_path = Path(args[1])
  except:
    app.logger.error("Specified path to images directory is invalid!")
    exit(1)
  
  if not images_path.is_dir():
    app.logger.error(f"Specified path does not point to a directory!")
    exit(1)
  
  index_path = images_path.joinpath("index.json")
  if not index_path.is_file():
    app.logger.error(f"Directory '{images_path}' does not contain an index.json file!")
    exit(1)
    
  return images_path, index_path


if __name__ == "__main__":
  images_path, index_path = parse_arguments(sys.argv)
  image_index = parse_index(index_path)
  
  if image_index is None:
    app.logger.error("Failed to parse index.json")
    exit(1)
    
  app.logger.info("Successfully parsed index.json")
  app.run()