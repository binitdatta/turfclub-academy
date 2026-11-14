package com.rollingstone.turfclub.academy.web;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

import com.rollingstone.turfclub.academy.content.ContentPage;
import com.rollingstone.turfclub.academy.content.ContentRepository;
import com.rollingstone.turfclub.academy.content.Kind;

/** Business domain, security and database schema pages - all rendered by the same template. */
@Controller
public class PageController {

    private final ContentRepository content;

    public PageController(ContentRepository content) {
        this.content = content;
    }

    @GetMapping("/domains/{slug}")
    public String domain(@PathVariable String slug, Model model) {
        return render(Kind.DOMAIN, slug, model);
    }

    @GetMapping("/security/{slug}")
    public String security(@PathVariable String slug, Model model) {
        return render(Kind.SECURITY, slug, model);
    }

    @GetMapping("/schemas/{slug}")
    public String schema(@PathVariable String slug, Model model) {
        return render(Kind.SCHEMA, slug, model);
    }

    @GetMapping({"/domains", "/security", "/schemas"})
    public String firstOfKind(jakarta.servlet.http.HttpServletRequest request) {
        Kind kind = switch (request.getRequestURI()) {
            case "/security" -> Kind.SECURITY;
            case "/schemas" -> Kind.SCHEMA;
            default -> Kind.DOMAIN;
        };
        return "redirect:" + content.pages(kind).get(0).href();
    }

    private String render(Kind kind, String slug, Model model) {
        ContentPage page = content.page(kind, slug)
                                  .orElseThrow(() -> new PageNotFoundException("No " + kind.code() + " page '" + slug + "'"));
        ContentPage[] neighbours = content.neighbours(page);
        model.addAttribute("page", page);
        model.addAttribute("kind", kind);
        model.addAttribute("previous", neighbours[0]);
        model.addAttribute("next", neighbours[1]);
        return "page";
    }
}
