package com.rollingstone.turfclub.academy.web;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class ArchitectureAiEraController {
    @GetMapping("/architecture-ai-era")
    public String architectureAiEra(Model model) {
        model.addAttribute("currentPath", "/architecture-ai-era");
        return "architecture-ai-era";
    }
}
