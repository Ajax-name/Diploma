package com.example.medapp.service;

import com.example.medapp.dto.AnalysisResultDto;
import com.example.medapp.model.AnalysisRequest;
import com.example.medapp.model.ImageData;
import com.example.medapp.repository.AnalysisRequestRepository;
import com.example.medapp.repository.ImageDataRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AnalysisService {

    private final AnalysisRequestRepository analysisRepo;
    private final ImageDataRepository imageRepo;
    private final ModelService modelService;

    private final Path uploadDir = Paths.get("uploads");

    public AnalysisResultDto processAnalysis(List<MultipartFile> files) throws IOException {
        AnalysisRequest analysis = AnalysisRequest.builder()
                .resultText("Анализ...") // временно
                .status("PROCESSING")
                .createdAt(LocalDateTime.now())
                .build();
        analysis = analysisRepo.save(analysis);

        Files.createDirectories(uploadDir);

        List<String> savedPaths = new ArrayList<>();

        for (MultipartFile file : files) {
            String filename = UUID.randomUUID() + "_" + file.getOriginalFilename();
            Path path = uploadDir.resolve(filename);
            Files.copy(file.getInputStream(), path, StandardCopyOption.REPLACE_EXISTING);
            savedPaths.add(path.toAbsolutePath().toString().trim());

            // Сохраняем в БД
            ImageData img = ImageData.builder()
                    .filePath(path.toString())
                    .uploadedAt(LocalDateTime.now())
                    .analysis(analysis)
                    .build();
            imageRepo.save(img);
        }

        String result = modelService.predictModel(savedPaths);

        analysis.setResultText(result);
        analysis.setStatus("DONE");
        analysisRepo.save(analysis);

        return new AnalysisResultDto(analysis.getId(), result);
    }
}
