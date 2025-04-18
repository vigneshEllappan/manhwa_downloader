import threading
import requests
from bs4 import BeautifulSoup
import os
import zipfile
import shutil
from PIL import Image
import re

# --- Downloader Class ---
class ManwaDownloader:
    def __init__(self, url, folder_name, cbz_filename, base_dir):
        self.url = url
        self.base_dir = base_dir
        self.folder_name = os.path.join(base_dir, folder_name)
        if os.path.exists(self.folder_name):
            shutil.rmtree(self.folder_name)
        os.makedirs(self.folder_name)
        self.cbz_filename = os.path.join(base_dir, cbz_filename)

    def download_images(self, index, image):  
        img_name = os.path.join(self.folder_name, f"image_{index}.jpg")    
        try:
            response = requests.get(image, stream=True)
            if response.status_code == 200:
                with open(img_name, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"Downloaded: {img_name}")
                self.image_names.append(img_name)
        except Exception as e:
            print(f"Failed to download {image}: {e}") 
    

    def combine_images_in_batches(self):

        def natural_sort_key(path):
            match = re.search(r'image_(\d+)\.jpg', os.path.basename(path))
            return int(match.group(1)) if match else float('inf')

        self.image_names.sort(key=natural_sort_key)

        combined_images = []
        batch_size = 3
        batches = [self.image_names[i:i+batch_size] for i in range(0, len(self.image_names), batch_size)]

        for idx, batch in enumerate(batches):
            imgs = []
            for img_path in batch:
                try:
                    img = Image.open(img_path).convert("RGB")  # Ensure RGB for saving
                    imgs.append(img)
                except Exception as e:
                    print(f"Error loading image {img_path}: {e}")

            if not imgs:
                print(f"Skipping batch {idx} — no valid images")
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
            combined_path = os.path.abspath(os.path.join(self.folder_name, combined_name))

            try:
                combined_img.save(combined_path)
                print(f"Saved combined image: {combined_path}")
                combined_images.append(combined_path)
            except Exception as e:
                print(f"Error saving {combined_path}: {e}")

            for img in imgs:
                img.close()
            for img_path in batch:
                try:
                    os.remove(img_path)
                except Exception as e:
                    print(f"Could not delete {img_path}: {e}")

        self.image_names = combined_images



    def spawn_threads(self):
        self.image_names = []
        threads = []
        for index, image in enumerate(self.image_paths):
            thread = threading.Thread(target=self.download_images, args=(index, image))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

        # 🔀 Combine if more than 20
        if len(self.image_names) > 20:
            print("Combining images in batches of 3...")
            self.combine_images_in_batches()

    def create_cbz(self):
        with zipfile.ZipFile(self.cbz_filename, 'w', zipfile.ZIP_DEFLATED) as cbz:
            for image in self.image_names:
                cbz.write(image, os.path.basename(image))
        print(f"CBZ file created: {self.cbz_filename}")

        # Delete image folder after CBZ creation
        shutil.rmtree(self.folder_name)

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
        print(f"Found {len(self.image_paths)} images to download")
        return True



def handle_download(data):
    url = data["url"]
    folder = data["folder"]
    cbz = data["cbz"]
    base_dir = "downloads"
    os.makedirs(base_dir, exist_ok=True)

    downloader = ManwaDownloader(url, folder, cbz, base_dir)
    if downloader.make_request() and downloader.parse_response():
        downloader.spawn_threads()
        downloader.create_cbz()
        return {"status": "success", "cbz": cbz}
    return {"status": "failed"}
