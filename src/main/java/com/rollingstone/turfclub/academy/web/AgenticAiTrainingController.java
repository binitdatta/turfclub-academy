// IMPORTANT: Change this package declaration to match the package containing
// your @SpringBootApplication class (or a subpackage) before copying.
package com.rollingstone.turfclub.academy.web;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import java.util.Set;

@Controller
public class AgenticAiTrainingController {
    private static final Set<String> PAGES = Set.of(
        "overview", "turfbot", "turfbot-security", "turfbot-walkthrough",
        "workforce", "rex", "cleo", "governance", "demo"
    );

    @GetMapping("/agentic-ai")
    public String home() { return "redirect:/agentic-ai/overview"; }

    @GetMapping("/agentic-ai/{page}")
    public String page(@PathVariable String page) {
        if (!PAGES.contains(page)) {
            throw new org.springframework.web.server.ResponseStatusException(
                org.springframework.http.HttpStatus.NOT_FOUND, "Unknown Agentic AI lesson");
        }
        return "agentic-ai/" + page;
    }
}
