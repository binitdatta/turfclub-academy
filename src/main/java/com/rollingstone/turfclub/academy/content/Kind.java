package com.rollingstone.turfclub.academy.content;

import java.util.Arrays;

/** The three kinds of teaching page, their content folder and their URL prefix. */
public enum Kind {
    DOMAIN("domain", "domains", "/domains", "Business domains"),
    SECURITY("security", "security", "/security", "Security"),
    SCHEMA("schema", "schemas", "/schemas", "Database schemas");

    private final String code;
    private final String folder;
    private final String path;
    private final String label;

    Kind(String code, String folder, String path, String label) {
        this.code = code;
        this.folder = folder;
        this.path = path;
        this.label = label;
    }

    public String code() {
        return code;
    }

    public String folder() {
        return folder;
    }

    public String path() {
        return path;
    }

    public String label() {
        return label;
    }

    public static Kind of(String code) {
        return Arrays.stream(values()).filter(k -> k.code.equals(code)).findFirst()
                     .orElseThrow(() -> new IllegalArgumentException("Unknown page kind '" + code + "'"));
    }
}
