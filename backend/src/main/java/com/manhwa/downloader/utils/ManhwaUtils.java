package com.manhwa.downloader.utils;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.util.*;
import java.util.List;
import java.util.regex.*;
import java.util.stream.Collectors;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

public class ManhwaUtils {

    private static final Logger logger = LoggerFactory.getLogger(ManhwaUtils.class);

    // Method to delete a directory and all its contents recursively
    public static boolean deleteDirectoryRecursively(File dir) {
        logger.info("Deleting the file under the directory", dir.getName());
        if (dir == null || !dir.exists()) {
            return false; // Directory does not exist
        }

        // First, delete all files and subdirectories
        File[] files = dir.listFiles();
        if (files != null) {
            for (File file : files) {
                if (file.isDirectory()) {
                    // Recursively delete subdirectories
                    deleteDirectoryRecursively(file);
                } else {
                    // Delete file
                    file.delete();
                }
            }
        }

        // Now delete the directory itself
        return dir.delete();
    }


    public static List<File> combineFilesInBatches(List<File> input, int batchSize, File outputDir) throws IOException {
        List<File> combinedFiles = new ArrayList<>();

        for (int i = 0; i < input.size(); i += batchSize) {
            List<File> batch = input.subList(i, Math.min(i + batchSize, input.size()));

            List<BufferedImage> loadedImages = new ArrayList<>();
            int minWidth = Integer.MAX_VALUE;

            for (File file : batch) {
                BufferedImage img = ImageIO.read(file);
                if (img != null) {
                    loadedImages.add(img);
                    minWidth = Math.min(minWidth, img.getWidth());
                }
            }

            if (loadedImages.isEmpty() || minWidth == Integer.MAX_VALUE) continue;

            // Resize and stack vertically
            List<BufferedImage> resized = new ArrayList<>();
            for (BufferedImage img : loadedImages) {
                int newHeight = img.getHeight() * minWidth / img.getWidth();
                Image tmp = img.getScaledInstance(minWidth, newHeight, Image.SCALE_SMOOTH);
                BufferedImage resizedImg = new BufferedImage(minWidth, newHeight, BufferedImage.TYPE_INT_RGB);
                resizedImg.getGraphics().drawImage(tmp, 0, 0, null);
                resized.add(resizedImg);
            }

            int totalHeight = resized.stream().mapToInt(BufferedImage::getHeight).sum();
            BufferedImage finalImg = new BufferedImage(minWidth, totalHeight, BufferedImage.TYPE_INT_RGB);

            Graphics g = finalImg.getGraphics();
            int y = 0;
            for (BufferedImage img : resized) {
                g.drawImage(img, 0, y, null);
                y += img.getHeight();
            }

            // Save to output file
            File outFile = new File(outputDir, String.format("page_%02d.jpg", combinedFiles.size()));
            ImageIO.write(finalImg, "jpg", outFile);
            combinedFiles.add(outFile);

            // Delete original batch
            for (File file : batch) {
                if (!file.delete()) {
                    System.err.println("Warning: Failed to delete file " + file.getAbsolutePath());
                }
            }
        }

        return combinedFiles;
    }

    public static Comparator<String> naturalChapterComparator() {
        return (a, b) -> {
            double numA = extractChapterDecimal(a);
            double numB = extractChapterDecimal(b);
            if (Double.compare(numA, numB) != 0) {
                return Double.compare(numA, numB);
            }
            // Fallback to lexicographic comparison (e.g. Chapter 11A vs Chapter 11B)
            return a.compareToIgnoreCase(b);
        };
    }

    public static double extractChapterDecimal(String title) {
        Matcher matcher = Pattern.compile("(\\d+(\\.\\d+)?)").matcher(title);
        return matcher.find() ? Double.parseDouble(matcher.group(1)) : 0.0;
    }}
