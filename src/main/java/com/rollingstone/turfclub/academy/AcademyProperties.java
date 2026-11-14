package com.rollingstone.turfclub.academy;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * @param erpHost     host name of the running ERP; "localhost" links in the content are rewritten to it
 * @param keycloakUrl base URL of Keycloak, used by the navbar link to the admin console
 */
@ConfigurationProperties(prefix = "academy")
public record AcademyProperties(String erpHost, String keycloakUrl) {

    public AcademyProperties {
        erpHost = (erpHost == null || erpHost.isBlank()) ? "localhost" : erpHost.trim();
        keycloakUrl = (keycloakUrl == null || keycloakUrl.isBlank()) ? "http://localhost:8080" : keycloakUrl.trim();
    }
}
