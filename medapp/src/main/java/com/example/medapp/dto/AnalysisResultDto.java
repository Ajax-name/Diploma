package com.example.medapp.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class AnalysisResultDto {
    private Long analysisId;
    private String result;
}
