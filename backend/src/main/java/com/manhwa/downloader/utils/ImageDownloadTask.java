package com.manhwa.downloader.utils;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.net.URL;
import java.util.concurrent.Callable;

public class ImageDownloadTask implements Callable<File> {

    private static final Logger logger = LoggerFactory.getLogger(ImageDownloadTask.class);
    private final String imageUrl;
    private final File targetDir;
    private final int index;

    public ImageDownloadTask(String imageUrl, File targetDir, int index) {
        this.imageUrl = imageUrl;
        this.targetDir = targetDir;
        this.index = index;
    }

    public static String getImageExtension(String url) {
        try {
            String cleanUrl = url.split("\\?")[0];
            String ext = cleanUrl.substring(cleanUrl.lastIndexOf('.') + 1).toLowerCase();
            if (ext.equals("jpeg")) ext = "jpg";
            if (ext.matches("jpg|png|webp|bmp")) return ext;
        } catch (Exception ignored) {}
        return null;
    }

    @Override
    public File call() {
        try {
            // Download the image
            BufferedImage image = ImageIO.read(new URL(imageUrl));
            if (image == null) {
                logger.error("ImageIO.read returned null for: {}", imageUrl);
                return null;
            }

            // Extract the file extension
            String extension = getImageExtension(imageUrl);
            if (extension == null || !ImageIO.getImageWritersByFormatName(extension).hasNext()) {
                logger.warn("Unsupported image format '{}', defaulting to 'jpg'", extension);
                extension = "jpg"; // fallback
            }

            // Determine output file path
            File imgFile = new File(targetDir, String.format("images_%02d.%s", index, extension));

            // Convert image if necessary (e.g., JPG needs RGB)
            BufferedImage finalImage = image;
            if (extension.equalsIgnoreCase("jpg") || extension.equalsIgnoreCase("jpeg")) {
                BufferedImage rgbImage = new BufferedImage(
                        image.getWidth(), image.getHeight(), BufferedImage.TYPE_INT_RGB
                );
                rgbImage.getGraphics().drawImage(image, 0, 0, null);
                finalImage = rgbImage;
            }

            // Write the image to file
            boolean written = ImageIO.write(finalImage, extension, imgFile);
            if (!written) {
                logger.error("ImageIO.write failed for file: {}", imgFile.getAbsolutePath());
                return null;
            }

            logger.info("Image {} saved successfully.", imgFile.getName());
            return imgFile;

        } catch (Exception e) {
            logger.error("Failed to download or save image: {}", imageUrl, e);
            return null;
        }
    }

}
