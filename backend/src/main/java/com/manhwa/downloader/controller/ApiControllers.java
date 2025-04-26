package com.manhwa.downloader.controller;

import com.manhwa.downloader.service.ManhwaService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.beans.factory.annotation.Autowired;

import java.io.File;
import java.nio.file.Files;
import java.util.*;
@RestController
@RequestMapping("/api")
public class ApiControllers {

    private static final Logger logger = LoggerFactory.getLogger(ApiControllers.class);

    @Autowired
    private ManhwaService manhwaService;

    @GetMapping("/health")
    public String health() {
        return "{\"status\": \"ok\"}";
    }
 
    @GetMapping("/chapters")
    public ResponseEntity<?> getChapters(@RequestParam String title) {
        if (title == null) {
            return ResponseEntity.badRequest().body("Missing 'title' parameter");
        }
        try {
            Map<String, String> chapters = manhwaService.getChapters(title);
            System.out.println(chapters);
            return ResponseEntity.ok(chapters);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @PostMapping("/download")
    public ResponseEntity<?> download(@RequestBody Map<String, String> body) {
        String title = body.get("title");
        String chapter = body.get("chapter");
        String url = body.get("url");
        logger.info("Request Received");
        logger.info(title + " "+ chapter + " " + url);

        try {
            File file = new File(manhwaService.downloadAsCbzToFile(title, chapter, url));

            logger.info("Serving file: {}", file.getName());

            ByteArrayResource resource = new ByteArrayResource(Files.readAllBytes(file.toPath()));
            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + file.getName() + "\"")
                    .contentLength(file.length())
                    .contentType(MediaType.APPLICATION_OCTET_STREAM)
                    .body(resource);

        } catch (Exception e) {
            logger.error("Error during CBZ processing: ", e);
            return ResponseEntity.status(500).body("Failed to process CBZ: " + e.getMessage());
        }
    }

}
