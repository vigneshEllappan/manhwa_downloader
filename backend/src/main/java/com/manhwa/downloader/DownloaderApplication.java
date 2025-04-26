package com.manhwa.downloader;
import com.manhwa.downloader.utils.CbzFileCache;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.nio.file.Paths;

@SpringBootApplication
public class DownloaderApplication {

	public static void main(String[] args) {
		SpringApplication.run(DownloaderApplication.class, args);
		startCacheProcessing();
	}

	public static void startCacheProcessing() {
		// Your additional service logic
		System.out.println("Starting Caching service...");
		CbzFileCache.processCacheDirectory(Paths.get("tmp").toAbsolutePath());
	}

}
