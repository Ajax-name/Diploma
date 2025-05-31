package com.example.medapp.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "medical_staff")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MedicalStaff {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String fullName;

    @Column(unique = true, nullable = false)
    private String email;


    private String passwordHash;

    private LocalDateTime createdAt = LocalDateTime.now();

    @OneToMany(mappedBy = "staff", cascade = CascadeType.ALL)
    private List<AnalysisRequest> requests = new ArrayList<>();

}
