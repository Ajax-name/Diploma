package com.example.medapp.service;

import com.example.medapp.dto.LoginRequest;
import com.example.medapp.model.MedicalStaff;
import com.example.medapp.repository.MedicalStaffRepository;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class AuthService {

    private final MedicalStaffRepository repository;

    public AuthService(MedicalStaffRepository repository) {
        this.repository = repository;
    }

    public Optional<MedicalStaff> authenticate(LoginRequest request) {
        return repository.findByEmailOrFullName(request.getEmailOrName(), request.getEmailOrName())
                .filter(staff -> staff.getPasswordHash().equals(request.getPassword()));
    }
}
