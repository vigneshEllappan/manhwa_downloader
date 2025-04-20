package com.manhwa.downloader.utils;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.*;
import java.util.List;
import java.util.regex.*;
import java.util.stream.Collectors;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

public class ManhwaUtils {

    public static byte[] createCbz(List<BufferedImage> images) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ZipOutputStream zos = new ZipOutputStream(baos);

        for (int i = 0; i < images.size(); i++) {
            ByteArrayOutputStream imgOut = new ByteArrayOutputStream();
            ImageIO.write(images.get(i), "jpg", imgOut);
            zos.putNextEntry(new ZipEntry(String.format("page_%02d.jpg", i + 1)));
            zos.write(imgOut.toByteArray());
            zos.closeEntry();
        }

        zos.close();
        return baos.toByteArray();
    }

    public static List<BufferedImage> combineInBatches(List<BufferedImage> input, int batchSize) {
        List<BufferedImage> combined = new ArrayList<>();
        for (int i = 0; i < input.size(); i += batchSize) {
            List<BufferedImage> batch = input.subList(i, Math.min(i + batchSize, input.size()));
            int width = batch.stream().mapToInt(BufferedImage::getWidth).min().orElse(500);
            List<BufferedImage> resized = batch.stream().map(img -> {
                int newHeight = img.getHeight() * width / img.getWidth();
                Image tmp = img.getScaledInstance(width, newHeight, Image.SCALE_SMOOTH);
                BufferedImage resizedImg = new BufferedImage(width, newHeight, BufferedImage.TYPE_INT_RGB);
                resizedImg.getGraphics().drawImage(tmp, 0, 0, null);
                return resizedImg;
            }).collect(Collectors.toList());

            int height = resized.stream().mapToInt(BufferedImage::getHeight).sum();
            BufferedImage finalImg = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
            Graphics g = finalImg.getGraphics();
            int y = 0;
            for (BufferedImage img : resized) {
                g.drawImage(img, 0, y, null);
                y += img.getHeight();
            }

            combined.add(finalImg);
        }
        return combined;
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
