package com.example.medapp.controller;

import com.example.medapp.dto.LoginDto;
import com.example.medapp.dto.LoginRequest;
import com.example.medapp.dto.RegistrationDto;
import com.example.medapp.model.MedicalStaff;
import com.example.medapp.repository.MedicalStaffRepository;
import com.example.medapp.service.AuthService;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Optional;

@RestController
@RequestMapping("/auth")
public class AuthController {
    private final MedicalStaffRepository repository;
    private final AuthService authService;

    @Value("${app.secret-code}")
    private String secretCode;

    public AuthController(MedicalStaffRepository repository, AuthService authService) {
        this.repository = repository;
        this.authService = authService;
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody RegistrationDto dto) {
        if (!dto.password.equals(dto.confirmPassword)) {
            return ResponseEntity.badRequest().body("Пароли не совпадают");
        }

        if (!dto.secretCode.equals(secretCode)) {
            return ResponseEntity.badRequest().body("Неверный код");
        }

        MedicalStaff staff = new MedicalStaff();
        staff.setFullName(dto.fullName);
        staff.setEmail(dto.email);
        staff.setPasswordHash(dto.password); // Для безопасности желательно шифровать

        repository.save(staff);

        return ResponseEntity.ok().build();
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request, HttpSession session) {
        Optional<MedicalStaff> staff = authService.authenticate(request);
        if (staff.isPresent()) {
            session.setAttribute("user", staff.get());
            return ResponseEntity.ok().build();
        } else {
            return ResponseEntity.status(401).body("Неверный логин или пароль");
        }
    }

    @PostMapping("/logout")
    public ResponseEntity<?> logout(HttpSession session) {
        session.invalidate();
        return ResponseEntity.ok().build();
    }
}
