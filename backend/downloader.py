import threading
import requests
from bs4 import BeautifulSoup
import os
import zipfile
import shutil
from PIL import Image
import re
import json
import io
from io import BytesIO
from pathlib import Path
import logging

# Configure the logging system
logging.basicConfig(
    level=logging.INFO,  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log to console
    ]
)

logger = logging.getLogger(__name__)

# Directory to store CBZ files
CACHE_DIR = Path("tmp")
CACHE_DIR.mkdir(exist_ok=True)

cbz_cache = {}  # Maps a cache key to CBZ file path

# --- Downloader Class ---
class ManwaDownloader:
    def __init__(self, url):
        self.url = url

    def download_images(self, index, image_url):
        response = requests.get(image_url, stream=True)
        img_data = io.BytesIO(response.content)
        self.images.append({
            "name": f"image_{index}.jpg",
            "data": img_data
        })
        logger.info(f"Downloaded: image_{index}.jpg")
        if not img_data:
            raise Exception(f"Failed to Download : {image_url}")
    

    def combine_images_in_batches(self):
        def natural_sort_key(image_dict):
            match = re.search(r'image_(\d+)\.jpg', image_dict["name"])
            return int(match.group(1)) if match else float('inf')

        self.images.sort(key=natural_sort_key)
        
        combined_images = []
        batch_size = 4
        batches = [self.images[i:i+batch_size] for i in range(0, len(self.images), batch_size)]

        for idx, batch in enumerate(batches):
            imgs = []
            for img_dict in batch:
                img = Image.open(img_dict["data"]).convert("RGB")
                imgs.append(img)

            if not imgs:
                logger.info(f"Skipping batch {idx} — no valid images")
                continue

            min_width = min(img.width for img in imgs)
            imgs = [img.resize((min_width, int(img.height * min_width / img.width))) for img in imgs]

            total_height = sum(img.height for img in imgs)
            combined_img = Image.new("RGB", (min_width, total_height))

            y_offset = 0
            for img in imgs:
                combined_img.paste(img, (0, y_offset))
                y_offset += img.height

            combined_io = io.BytesIO()
            combined_img.save(combined_io, format='JPEG')
            combined_io.seek(0)

            combined_images.append({
                "name": f"page_{idx+1:02d}.jpg",
                "data": combined_io
            })

            # Close individual image objects
            for img in imgs:
                img.close()

        self.images = combined_images



    def spawn_threads(self):
        self.images = []
        threads = []

        for index, image_url in enumerate(self.image_paths):
            thread = threading.Thread(target=self.download_images, args=(index, image_url))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        if len(self.images) > 20:
            logger.info("Combining images in batches of 4 (in memory)...")
            self.combine_images_in_batches()


    def create_cbz(self):
        cbz_buffer = io.BytesIO()
        with zipfile.ZipFile(cbz_buffer, 'w', zipfile.ZIP_DEFLATED) as cbz:
            for img in self.images:
                cbz.writestr(img["name"], img["data"].getvalue())
        cbz_buffer.seek(0)
        logger.info("CBZ created fully in memory.")
        return cbz_buffer.getvalue()

    def make_request(self):
        response = requests.get(self.url)
        self.soup = BeautifulSoup(response.text, "html.parser")
        return True

    def parse_response(self):
        xScrollContent = "div.page-break.no-gaps img"
        srcTag = "data-src"
        if "reincarnated-murim-lord/" in self.url:
            xScrollContent = "div.page-break img"
            srcTag = "src"
        self.image_paths = [] 
        img_tags = self.soup.select(xScrollContent)
        for img in img_tags:
            img_url = img.get(srcTag)
            self.image_paths.append(img_url)
        logger.info(f"Found {len(self.image_paths)} images to download")
        return True


titleUrlMap = {
            "Regressor of the Fallen Family": "https://manhuaus.org/manga/regressor-of-the-fallen-family/",
            "Release That Witch": "https://manhuaus.org/manga/release-that-witch-1/",
            "Magic Emperor":"https://manhuaus.org/manga/magic-emperor-0/",
            "Descended From Divinity": "https://manhuaus.org/manga/the-heavenly-demon-cant-live-a-normal-life/",
            "Regressed Life of The Sword Clan's Ignoble Reincarnator":"https://manhuaus.org/manga/regressed-life-of-the-sword-clans-ignoble-reincarnator/",
            "The Greatest Estate Developer":"https://manhuaus.org/manga/the-worlds-best-engineer/",
            "Reincarnated Murim Lord":"https://manhuaplus.me/manhua/reincarnated-murim-lord/ajax/chapters/"
        }

# Function to extract the numbers from the string
def natural_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def sanitize_filename(name):
    """Remove illegal characters for file paths"""
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-', '.')).strip()

def loadExistingCache():
    """Scans cache folder and rebuilds cbz_cache on startup"""
    for title_dir in CACHE_DIR.iterdir():
        if title_dir.is_dir():
            title = title_dir.name
            for file in title_dir.glob("*.cbz"):
                chapter = file.stem  # filename without extension
                cache_key = f"{title}_{chapter}"
                cbz_cache[cache_key] = file.resolve()
    logger.info(f"Loaded {len(cbz_cache)} cached CBZ files.")
    logger.info(cbz_cache)

def handleDownload(data):
    url = data["url"]
    title = sanitize_filename(data.get("title", "Unknown Title"))
    chapter = sanitize_filename(data.get("chapter", "Unknown Chapter"))

    cache_key = f"{title}_{chapter}"

    if cache_key in cbz_cache:
        return cbz_cache[cache_key]

    downloader = ManwaDownloader(url)
    if downloader.make_request() and downloader.parse_response():
        downloader.spawn_threads()
        cbz_bytes = downloader.create_cbz()

         # Path: cache/Title/Chapter - 1.cbz
        title_dir = CACHE_DIR / title
        title_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"{chapter}.cbz" if chapter.lower().startswith("chapter") else f"Chapter - {chapter}.cbz"
        file_path = (title_dir / file_name).resolve()
        # Assume downloader creates the file
        # file_path = (CACHE_DIR / title / f"{chapter}.cbz").resolve()
        logger.info(file_path)

        with open(file_path, "wb") as f:
            f.write(cbz_bytes)

        loadExistingCache()
        return file_path
    return None

def handleChaptersGeneration(title):
    site_url = titleUrlMap.get(title, '')
    if not site_url:
        return None
    try:
        if title == 'Reincarnated Murim Lord':
            data = {
                "action": "manga_get_chapters",
                "manga": "4498"
            }

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0"
            }

            response = requests.post(site_url, data=data, headers=headers)
        else:
            response = requests.get(site_url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.select("li.wp-manga-chapter a")
        data = {}
        for link in links:
            href = link.get("href")
            text = link.text.strip()
            if "chapter" in href.lower():
                data[text] = href
        sorted_dict = {k: data[k] for k in sorted(data.keys(), key=natural_key)}
        return json.dumps(sorted_dict)
    except Exception as e:
        return None
            