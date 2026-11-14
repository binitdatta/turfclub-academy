package com.rollingstone.turfclub.academy.web;

import java.util.List;

import jakarta.servlet.http.HttpServletRequest;

import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ModelAttribute;

import com.rollingstone.turfclub.academy.AcademyProperties;
import com.rollingstone.turfclub.academy.content.ContentRepository;
import com.rollingstone.turfclub.academy.content.Kind;
import com.rollingstone.turfclub.academy.content.NavGroup;

/** Puts the navbar menus and the current path into every page's model. */
@ControllerAdvice
public class NavigationAdvice {

    private final ContentRepository content;
    private final AcademyProperties properties;

    public NavigationAdvice(ContentRepository content, AcademyProperties properties) {
        this.content = content;
        this.properties = properties;
    }

    @ModelAttribute("navDomains")
    public List<NavGroup> navDomains() {
        return content.navigation(Kind.DOMAIN);
    }

    @ModelAttribute("navSecurity")
    public List<NavGroup> navSecurity() {
        return content.navigation(Kind.SECURITY);
    }

    @ModelAttribute("navSchemas")
    public List<NavGroup> navSchemas() {
        return content.navigation(Kind.SCHEMA);
    }

    @ModelAttribute("currentPath")
    public String currentPath(HttpServletRequest request) {
        return request.getRequestURI();
    }

    @ModelAttribute("erpPortalUrl")
    public String erpPortalUrl() {
        return "http://" + properties.erpHost() + ":8101/";
    }

    @ModelAttribute("keycloakAdminUrl")
    public String keycloakAdminUrl() {
        return properties.keycloakUrl() + "/admin/master/console/#/turfclub";
    }
}
