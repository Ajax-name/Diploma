package com.example.medapp.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "analysis_request")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AnalysisRequest {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "staff_id")
    private MedicalStaff staff;

    @Column(name = "result_text", length = 1500)
    private String resultText;

    private String status = "NEW";

    private LocalDateTime createdAt = LocalDateTime.now();

    @OneToMany(mappedBy = "analysis", cascade = CascadeType.ALL)
    private List<ImageData> images = new ArrayList<>();

}
