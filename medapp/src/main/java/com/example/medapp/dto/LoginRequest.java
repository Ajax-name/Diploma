package com.example.medapp.dto;

public class LoginRequest {
    private String emailOrName;
    private String password;

    public String getEmailOrName() {
        return emailOrName;
    }

    public void setEmailOrName(String emailOrName) {
        this.emailOrName = emailOrName;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}
