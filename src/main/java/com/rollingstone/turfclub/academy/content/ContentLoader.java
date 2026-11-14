package com.rollingstone.turfclub.academy.content;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Parses content JSON into {@link ContentPage}s and builds the navigation. Free of Spring so it can be unit tested.
 */
public class ContentLoader {

    private static final Map<String, Integer> DOMAIN_GROUP_ORDER = order("core", "racing", "betting", "club", "supply", "finance", "ai");
    private static final Map<String, Integer> SCHEMA_GROUP_ORDER = order("shared", "racing", "betting", "club", "supply", "finance", "ai");

    private static final String KEYCLOAK_TOKEN = "\u0000keycloak\u0000";

    private final ObjectMapper mapper;
    private final String erpHost;
    private final String keycloakUrl;

    public ContentLoader(ObjectMapper mapper, String erpHost, String keycloakUrl) {
        this.mapper = mapper.copy().configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        this.erpHost = erpHost;
        this.keycloakUrl = keycloakUrl;
    }

    /** Parses one page; links to the lab ERP and Keycloak are pointed at the configured hosts. */
    public ContentPage parse(String json, String origin) {
        String text = json.replace("http://localhost:8080", KEYCLOAK_TOKEN)
                          .replace("http://localhost:", "http://" + erpHost + ":")
                          .replace(KEYCLOAK_TOKEN, keycloakUrl);
        try {
            ContentPage page = mapper.readValue(text, ContentPage.class);
            if (page.slug() == null || page.title() == null || page.kind() == null) {
                throw new IllegalStateException("Content file " + origin + " needs kind, slug and title");
            }
            Kind.of(page.kind());
            return page;
        } catch (IOException ex) {
            throw new IllegalStateException("Content file " + origin + " is not valid: " + ex.getMessage(), ex);
        }
    }

    /** Pages of a kind in menu order: group, then order, then title. */
    public static List<ContentPage> sorted(List<ContentPage> pages, Kind kind) {
        Map<String, Integer> groups = kind == Kind.SCHEMA ? SCHEMA_GROUP_ORDER : DOMAIN_GROUP_ORDER;
        return pages.stream()
                    .sorted(Comparator.<ContentPage>comparingInt(p -> groups.getOrDefault(p.group(), 99))
                                      .thenComparingInt(ContentPage::order)
                                      .thenComparing(ContentPage::title))
                    .toList();
    }

    /** Groups sorted pages into navbar columns, keeping the order. */
    public static List<NavGroup> navigation(List<ContentPage> sortedPages) {
        Map<String, List<NavGroup.NavLink>> links = new LinkedHashMap<>();
        Map<String, String> labels = new LinkedHashMap<>();
        for (ContentPage p : sortedPages) {
            labels.putIfAbsent(p.group(), p.groupLabel());
            links.computeIfAbsent(p.group(), g -> new ArrayList<>())
                 .add(new NavGroup.NavLink(p.title(), p.href(), p.icon(), meta(p)));
        }
        List<NavGroup> groups = new ArrayList<>();
        links.forEach((key, list) -> groups.add(new NavGroup(key, labels.get(key), List.copyOf(list))));
        return List.copyOf(groups);
    }

    private static String meta(ContentPage p) {
        if (p.facts().isEmpty()) {
            return null;
        }
        if ("schema".equals(p.kind())) {
            return p.facts().stream().filter(f -> "Tables".equals(f.label())).map(f -> f.value() + " tables").findFirst().orElse(null);
        }
        if ("domain".equals(p.kind())) {
            return p.facts().stream().filter(f -> "Port".equals(f.label())).map(ContentPage.Fact::value).findFirst().orElse(null);
        }
        return null;
    }

    private static Map<String, Integer> order(String... keys) {
        Map<String, Integer> map = new LinkedHashMap<>();
        for (int i = 0; i < keys.length; i++) {
            map.put(keys[i], i);
        }
        return map;
    }
}
