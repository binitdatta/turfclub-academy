package com.rollingstone.turfclub.academy;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

/**
 * Turf Club ERP Academy - the companion site for making education videos about the Rollingstone Turf Club ERP:
 * the architecture, every business domain, the Keycloak / OAuth2 / OIDC security model and every database schema,
 * each with a ready-to-record video plan.
 */
@SpringBootApplication
@ConfigurationPropertiesScan
public class AcademyApplication {

    public static void main(String[] args) {
        SpringApplication.run(AcademyApplication.class, args);
    }
}
