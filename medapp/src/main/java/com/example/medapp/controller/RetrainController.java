package com.example.medapp.controller;

import com.example.medapp.service.ModelService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class RetrainController {

    private final ModelService modelService;

    @PostMapping("/retrain")
    public ResponseEntity<String> retrainModel(
            @RequestParam("file") MultipartFile file,
            @RequestParam("className") String className) {
        try {
            modelService.retrainModel(file, className);
            return ResponseEntity.ok("Retraining started successfully");
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Retraining failed");
        }
    }
}
