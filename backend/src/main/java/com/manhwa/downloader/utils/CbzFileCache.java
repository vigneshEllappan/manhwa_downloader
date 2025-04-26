package com.manhwa.downloader.utils;

import java.io.File;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class CbzFileCache {

    // Nested structure: Map<title, Map<chapter, filePath>>
    private static final Map<String, Map<String, String>> cache = new ConcurrentHashMap<>();

    private static List<String> supportedTitles = new ArrayList<>();

    public static void processCacheDirectory(Path rootPath){
        supportedTitles.add("Regressor of the Fallen Family");
        supportedTitles.add("Release That Witch");
        supportedTitles.add("Magic Emperor");
        supportedTitles.add("Descended From Divinity");
        supportedTitles.add("Regressed Life of The Sword Clan's Ignoble Reincarnator");
        supportedTitles.add("The Greatest Estate Developer");
        supportedTitles.add("Reincarnated Murim Lord");
        System.out.println("Processing Directory "+ rootPath);
        File rootDir = new File(String.valueOf(rootPath));
        if (!rootDir.exists() || !rootDir.isDirectory()) {
            rootDir.mkdirs();
        }

        for (File titleDir : rootDir.listFiles()) {
            System.out.println(titleDir);
            if (titleDir.isDirectory() && supportedTitles.contains(titleDir.getName())) {
                String titleName = titleDir.getName();
                Map<String, String> chapterMap = new ConcurrentHashMap<>();

                for (File chapterDir : titleDir.listFiles()) {
                    System.out.println(chapterDir);
                    if (chapterDir.isFile()) {
                        String chapterName = chapterDir.getName();
                        String nameWithoutExt = chapterName.contains(".")
                                ? chapterName.substring(0, chapterName.lastIndexOf('.'))
                                : chapterName;
                        String chapterPath = chapterDir.getAbsolutePath();
                        chapterMap.put(nameWithoutExt, chapterPath);
                    }
                }

                cache.put(titleName, chapterMap);
            }
        }
        System.out.println(cache);
    }

    public static void saveFilePath(String title, String chapter, String path) {
        cache.computeIfAbsent(title, k -> new ConcurrentHashMap<>()).put(chapter, path);
    }

    public static String getFilePath(String title, String chapter) {
        return cache.getOrDefault(title, Map.of()).get(chapter);
    }

    public static boolean hasFile(String title, String chapter) {
        return getFilePath(title, chapter) != null;
    }

    public static void clear() {
        cache.clear();
    }

    public static void remove(String title, String chapter) {
        Map<String, String> chapterMap = cache.get(title);
        if (chapterMap != null) {
            chapterMap.remove(chapter);
            if (chapterMap.isEmpty()) {
                cache.remove(title);
            }
        }
    }
}
