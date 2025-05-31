package com.example.medapp.repository;

import com.example.medapp.model.AnalysisRequest;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AnalysisRequestRepository extends JpaRepository<AnalysisRequest, Long> {
    List<AnalysisRequest> findByStaffId(Long staffId);
}
