package com.example.medapp.repository;

import com.example.medapp.model.MedicalStaff;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface MedicalStaffRepository extends JpaRepository<MedicalStaff, Long> {

    Optional<MedicalStaff> findByEmailOrFullName(String emailOrName, String emailOrName1);
}
