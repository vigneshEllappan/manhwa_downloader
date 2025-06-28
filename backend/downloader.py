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
    def __init__(self, url, title, chapter):
        self.url = url
        self.folder_name = (CACHE_DIR / title / chapter).resolve()
        self.folder_name.mkdir(parents=True, exist_ok=True)
        self.cbz_file_name = (CACHE_DIR / title / (chapter + '.cbz')).resolve() 
        self.images = []

    def download_images(self, index, image_url):
        response = requests.get(image_url, stream=True)
        file_name = f"image_{index:03d}.jpg"
        file_path = (self.folder_name / file_name).resolve()
        logger.info(file_path)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        self.images.append(file_path)  # Store the file path for later
        logger.info(f"Downloaded and saved: {file_path}")
    

    def combine_images_in_batches(self):
        def natural_sort_key(image_dict):
            match = re.search(r'image_(\d+)\.jpg', image_dict.name)
            return int(match.group(1)) if match else float('inf')

        self.images.sort(key=natural_sort_key)

        combined_images = []
        batch_size = 2
        batches = [self.images[i:i+batch_size] for i in range(0, len(self.images), batch_size)]

        for idx, batch in enumerate(batches):
            imgs = []
            logger.info(f"IDX: {idx}")
            for img_path in batch:
                logger.info(f"Image Path: {img_path}")
                img = Image.open(img_path).convert("RGB")  # Ensure RGB for saving
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

            combined_name = f"page_{idx+1:02d}.jpg"
            combined_path = Path(os.path.abspath(os.path.join(self.folder_name, combined_name)))

            combined_img.save(combined_path)
            logger.info(f"Saved combined image: {combined_path}")
            combined_images.append(combined_path)

            for img in imgs:
                img.close()
            for img_path in batch:
                logger.info(img_path)
                os.remove(str(img_path))
                logger.info(f"Removed {img_path}")

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
            logger.info("Combining images in batches of 4 ...")
            self.combine_images_in_batches()


    def create_cbz(self):
        """Create a CBZ file from saved image files on disk"""

        with zipfile.ZipFile(self.cbz_file_name, 'w', zipfile.ZIP_DEFLATED) as cbz:
            for img_path in sorted(self.images, key=lambda p: p.name):
                img_path = Path(img_path)  # Ensure it's a Path object
                if not img_path.exists():
                    raise Exception("Downloaded Images Missing")
                cbz.write(img_path, arcname=img_path.name)

        logger.info(f"CBZ successfully created at: {self.cbz_file_name}")# Get the chapter directory from the file path

        logger.info(f"Chapter Directory: {self.folder_name}")
        # Now only delete the chapter directory
        if os.path.exists(self.folder_name):
            shutil.rmtree(self.folder_name)
            print(f"Deleted {self.folder_name}")
        else:
            print(f"{self.folder_name} does not exist.")

    def make_request(self):
        response = requests.get(self.url)
        self.soup = BeautifulSoup(response.text, "html.parser")
        return True

    def parse_response(self):
        xScrollContent = "div.page-break.no-gaps img"
        srcTag = "data-src"
        if 'mangaread' in self.url:
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
            "Reincarnated Murim Lord":"https://www.mangaread.org/manga/reincarnated-heavenly-demon/",
            "SwordMaster's Youngest Son": "https://manhuaus.org/manga/swordmasters-youngest-son/",
            "The Regressed Mercenary's Machinations": "https://manhuaus.org/manga/the-regressed-mercenarys-machinations/",
            "Duke's Eldest Son is a Regressed Hero": "https://manhuaus.org/manga/dukes-eldest-son-is-a-regressed-hero/",
            "Eternally Regressing Knight": "https://manhuaus.org/manga/eternally-regressing-knight/",
            "Legend of The Northern Blade": "https://www.mangaread.org/manga/legend-of-the-northern-blade/",
            "Legendary Youngest Son of the Marquis House": "https://manhuaus.org/manga/legendary-youngest-son-of-the-marquis-house/",
            "Top Tier Providence: Secretly Cultivate for a Thousand Years": "https://manhuaus.org/manga/top-tier-providence-secretly-cultivate-for-a-thousand-years/",
            "A Villain's Will to Survive": "https://manhuaus.org/manga/a-villains-will-to-survive/"
        }

# Function to extract the numbers from the string
def natural_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def sanitize_filename(name):
    """Remove illegal characters for file paths"""
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-', '.')).strip()

def loadExistingCache():
    """Scans cache folder and rebuilds cbz_cache on startup"""
    cbz_cache.clear()
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

    downloader = ManwaDownloader(url, title, chapter)
    if downloader.make_request() and downloader.parse_response():
        downloader.spawn_threads()
        downloader.create_cbz()

        loadExistingCache()
        if cache_key in cbz_cache:
            return cbz_cache[cache_key]
    return None

def handleChaptersGeneration(title):
    site_url = titleUrlMap.get(title, '')
    if not site_url:
        return None
    try:
        response = requests.get(site_url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.select("li.wp-manga-chapter")
        data = {}
        for link in links:
            temp = {}
            anchor = link.select_one("a")
            span = link.select_one("span")
            releaseDate = ''
            if span:
                releaseDate = span.text.strip()
            if anchor:
                href = anchor.get("href")
                text = anchor.text.strip()
                if "chapter" in href.lower():
                    temp['url'] = href
                    temp['release_date'] = releaseDate
                    data[text] = temp
 
        sorted_dict = {k: data[k] for k in sorted(data.keys(), key=natural_key)}
        return json.dumps(sorted_dict)
    except Exception as e:
        return None
            