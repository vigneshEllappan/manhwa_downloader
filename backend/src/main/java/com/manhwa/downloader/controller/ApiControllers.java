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
import java.util.*;
@RestController
@RequestMapping("/api")
public class ApiControllers {

    private static final Logger logger = LoggerFactory.getLogger(ApiControllers.class);

    @Autowired
    private ManhwaService manhwaService; // This is where you will handle the logic for CBZ generation


    @GetMapping("/health")
    public String health() {
        return "{\"status\": \"ok\"}";
    }
 
    @GetMapping("/chapters")
    public ResponseEntity<?> getChapters(@RequestParam String title) {
        try {
            Map<String, String> chapters = manhwaService.getChapters(title);
            return ResponseEntity.ok(chapters);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @PostMapping("/download")
    public ResponseEntity<?> download(@RequestBody Map<String, String> body) {
        try {

            byte[] cbzBytes = manhwaService.downloadAsCbz(body.get("url")); // Your method that generates the CBZ

            ByteArrayResource resource = new ByteArrayResource(cbzBytes);
            logger.info("Successful File Processing");

            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"filename.cbz\"")
                    .contentLength(cbzBytes.length)
                    .contentType(MediaType.APPLICATION_OCTET_STREAM)
                    .body(resource);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(e.getMessage());
        }
    }

}
