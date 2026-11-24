package com.rollingstone.turfclub.academy.web;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

/**
 * Audience-facing professional-development lesson; rendered by the existing
 * Turf Club Academy Thymeleaf application and shared layout fragments.
 */
@Controller
public class CareerResilienceController {

    @GetMapping("/career-resilience")
    public String careerResilience(Model model) {
        model.addAttribute("currentPath", "/career-resilience");
        return "career-resilience";
    }
}
