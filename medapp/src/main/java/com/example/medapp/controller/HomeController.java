package com.example.medapp.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class HomeController {

    @GetMapping("/")
    public String redirectToFrontend() {
        return "redirect:/frontend/login.html";
    }
}
