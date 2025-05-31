package com.example.medapp.repository;

import com.example.medapp.model.ImageData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ImageDataRepository extends JpaRepository<ImageData, Long> {
    List<ImageData> findByAnalysisId(Long analysisId);
}