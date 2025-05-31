package com.example.medapp.controller;

import com.example.medapp.dto.AnalysisResultDto;
import com.example.medapp.service.AnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

@RestController
@RequestMapping("/api/analysis")
@RequiredArgsConstructor
public class AnalysisController {

    private final AnalysisService analysisService;

    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<AnalysisResultDto> analyzeImages(
            @RequestParam("files") List<MultipartFile> files
    ) throws IOException {

        if (files.isEmpty() || files.size() > 3) {
            return ResponseEntity.badRequest().build();
        }

        AnalysisResultDto result = analysisService.processAnalysis(files);
        return ResponseEntity.ok(result);
    }
}
