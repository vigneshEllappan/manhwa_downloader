package com.manhwa.downloader.service;

import com.manhwa.downloader.utils.CbzFileCache;
import com.manhwa.downloader.utils.ImageDownloadTask;
import com.manhwa.downloader.utils.ManhwaUtils;
import org.jsoup.Connection;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.concurrent.*;
import java.io.IOException;
import java.util.*;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;


@Service
public class ManhwaService {

    private static final Logger logger = LoggerFactory.getLogger(ManhwaService.class);

    private final Map<String, String> titleUrlMap = Map.of(
        "Regressor of the Fallen Family", "https://manhuaus.org/manga/regressor-of-the-fallen-family/",
        "Release That Witch", "https://manhuaus.org/manga/release-that-witch-1/",
        "Magic Emperor", "https://manhuaus.org/manga/magic-emperor-0/",
        "Descended From Divinity", "https://manhuaus.org/manga/the-heavenly-demon-cant-live-a-normal-life/",
        "Regressed Life of The Sword Clan's Ignoble Reincarnator", "https://manhuaus.org/manga/regressed-life-of-the-sword-clans-ignoble-reincarnator/",
        "The Greatest Estate Developer", "https://manhuaus.org/manga/the-worlds-best-engineer/",
        "Reincarnated Murim Lord", "https://manhuaplus.me/manhua/reincarnated-murim-lord/ajax/chapters/"
    );

    public Map<String, String> getChapters(String title) throws IOException {
        String siteUrl = titleUrlMap.getOrDefault(title, "");
        if (siteUrl.isEmpty()) throw new IllegalArgumentException("Unknown title");

        Document doc;
        if (title.equals("Reincarnated Murim Lord")) {
            Connection.Response response = Jsoup.connect(siteUrl)
                .header("Content-Type", "application/x-www-form-urlencoded")
                .header("User-Agent", "Mozilla/5.0")
                .data("action", "manga_get_chapters")
                .data("manga", "4498")
                .method(Connection.Method.POST)
                .execute();
            doc = Jsoup.parse(response.body());
        } else {
            doc = Jsoup.connect(siteUrl).get();
        }

        Elements links = doc.select("li.wp-manga-chapter a");
        Map<String, String> chapters = new TreeMap<>(ManhwaUtils.naturalChapterComparator());
        for (Element link : links) {
            String href = link.attr("href");
            String text = link.text().trim();
            if (href.toLowerCase().contains("chapter")) {
                chapters.put(text, href);
            }
        }
        return chapters;
    }

    public String downloadAsCbzToFile(String title, String chapter, String url) throws IOException, InterruptedException, ExecutionException {
        String cbzFilePath = CbzFileCache.getFilePath(title, chapter);
        if (cbzFilePath != null) {
            logger.info("Found File in Cache");
            return cbzFilePath;
        }

        Document doc = Jsoup.connect(url).get();
        Elements imgTags = doc.select(url.contains("reincarnated-murim-lord") ? "div.page-break img" : "div.page-break.no-gaps img");
        logger.info("Found {} images to download",imgTags.size());
        // Directory Setup
        File chapterDir = Paths.get("tmp", title , chapter).toFile();
        chapterDir.mkdirs();

        ExecutorService executor = Executors.newFixedThreadPool(3);
        List<Future<File>> futures = new ArrayList<>();

        int[] counter = {1};
        for (Element img : imgTags) {
            final int index = counter[0]++;
            String imgUrl = url.contains("reincarnated-murim-lord") ? img.attr("src") : img.attr("data-src");

            futures.add(executor.submit(new ImageDownloadTask(imgUrl, chapterDir, index)));
        }

        executor.shutdown();
        executor.awaitTermination(2, TimeUnit.MINUTES);

        List<File> imageFiles = new ArrayList<>();
        for (Future<File> future : futures) {
            imageFiles.add(future.get());
        }

        if(imageFiles.size() > 20){
            imageFiles = ManhwaUtils.combineFilesInBatches(imageFiles, 3, chapterDir);
        }
        // Create CBZ
        File cbzFile = Paths.get("tmp", title , chapter + ".cbz").toFile();
        System.out.println(cbzFile.getAbsolutePath());

        try (FileOutputStream fos = new FileOutputStream(cbzFile);
             ZipOutputStream zos = new ZipOutputStream(fos)) {

            imageFiles.sort(Comparator.comparing(File::getName));
            for (File imgFile : imageFiles) {
                zos.putNextEntry(new ZipEntry(imgFile.getName()));
                Files.copy(imgFile.toPath(), zos);
                zos.closeEntry();
            }
        }

        // Cleanup chapter directory
        ManhwaUtils.deleteDirectoryRecursively(chapterDir);

        CbzFileCache.saveFilePath(title, chapter, cbzFile.getAbsolutePath());

        return cbzFile.getAbsolutePath();
    }

}
