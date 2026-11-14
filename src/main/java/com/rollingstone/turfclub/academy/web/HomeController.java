package com.rollingstone.turfclub.academy.web;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import com.rollingstone.turfclub.academy.content.ContentRepository;
import com.rollingstone.turfclub.academy.content.Kind;

/** The home page: the architecture of the whole application and the video series. */
@Controller
public class HomeController {

    private final ContentRepository content;

    public HomeController(ContentRepository content) {
        this.content = content;
    }

    @GetMapping("/")
    public String home(Model model) {
        model.addAttribute("domains", content.pages(Kind.DOMAIN));
        model.addAttribute("domainGroups", content.navigation(Kind.DOMAIN));
        model.addAttribute("securityPages", content.pages(Kind.SECURITY));
        model.addAttribute("schemaPages", content.pages(Kind.SCHEMA));
        model.addAttribute("series", content.series());
        model.addAttribute("domainMinutes", content.totalMinutes(Kind.DOMAIN));
        model.addAttribute("securityMinutes", content.totalMinutes(Kind.SECURITY));
        model.addAttribute("schemaMinutes", content.totalMinutes(Kind.SCHEMA));
        model.addAttribute("tableCount", content.pages(Kind.SCHEMA).stream()
                .flatMap(p -> p.facts().stream())
                .filter(f -> "Tables".equals(f.label()))
                .mapToInt(f -> Integer.parseInt(f.value()))
                .sum());
        model.addAttribute("serviceCount", content.pages(Kind.DOMAIN).stream()
                .filter(p -> !"ai".equals(p.group()))
                .count());
        return "index";
    }
}
