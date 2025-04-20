package com.manhwa.downloader.utils;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.net.URL;
import java.util.List;

public class ImageDownloadTask implements Runnable {

    private static final Logger logger = LoggerFactory.getLogger(ImageDownloadTask.class);
    private final String imageUrl;
    private final List<BufferedImage> resultList;

    public ImageDownloadTask(String imageUrl, List<BufferedImage> resultList) {
        this.imageUrl = imageUrl;
        this.resultList = resultList;
    }

    @Override
    public void run() {
        try {
            BufferedImage image = ImageIO.read(new URL(imageUrl));
            synchronized (resultList) {
                resultList.add(image);
            }
        } catch (Exception e) {
            logger.error("Failed to download image: " + imageUrl);
            e.printStackTrace();
        }
    }
}
