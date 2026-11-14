package com.rollingstone.turfclub.academy.content;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.stereotype.Component;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.rollingstone.turfclub.academy.AcademyProperties;

/** Loads every page from {@code classpath:content/<folder>/*.json} once at start-up. */
@Component
public class ContentRepository {

    private static final Logger log = LoggerFactory.getLogger(ContentRepository.class);

    private final Map<Kind, List<ContentPage>> pages = new EnumMap<>(Kind.class);
    private final Map<Kind, Map<String, ContentPage>> bySlug = new EnumMap<>(Kind.class);
    private final Map<Kind, List<NavGroup>> navigation = new EnumMap<>(Kind.class);

    public ContentRepository(ObjectMapper objectMapper, AcademyProperties properties) throws IOException {
        ContentLoader loader = new ContentLoader(objectMapper, properties.erpHost(), properties.keycloakUrl());
        PathMatchingResourcePatternResolver resolver = new PathMatchingResourcePatternResolver();
        for (Kind kind : Kind.values()) {
            List<ContentPage> loaded = new ArrayList<>();
            for (Resource resource : resolver.getResources("classpath*:content/" + kind.folder() + "/*.json")) {
                try (InputStream in = resource.getInputStream()) {
                    ContentPage page = loader.parse(new String(in.readAllBytes(), StandardCharsets.UTF_8), resource.getDescription());
                    if (Kind.of(page.kind()) != kind) {
                        throw new IllegalStateException(resource.getDescription() + " has kind '" + page.kind() + "' but sits in " + kind.folder());
                    }
                    loaded.add(page);
                }
            }
            List<ContentPage> sorted = ContentLoader.sorted(loaded, kind);
            Map<String, ContentPage> index = new LinkedHashMap<>();
            sorted.forEach(p -> index.put(p.slug(), p));
            pages.put(kind, sorted);
            bySlug.put(kind, index);
            navigation.put(kind, ContentLoader.navigation(sorted));
            log.info("Loaded {} {} pages", sorted.size(), kind.code());
        }
    }

    public List<ContentPage> pages(Kind kind) {
        return pages.get(kind);
    }

    public Optional<ContentPage> page(Kind kind, String slug) {
        return Optional.ofNullable(bySlug.get(kind).get(slug));
    }

    public List<NavGroup> navigation(Kind kind) {
        return navigation.get(kind);
    }

    /** Previous and next page of the same kind, for the pager at the bottom of a page. */
    public ContentPage[] neighbours(ContentPage page) {
        List<ContentPage> list = pages(Kind.of(page.kind()));
        int i = list.indexOf(page);
        return new ContentPage[] {i > 0 ? list.get(i - 1) : null, i >= 0 && i < list.size() - 1 ? list.get(i + 1) : null};
    }

    /** Every page with a video plan, in series order: domains, security, schemas. */
    public List<ContentPage> series() {
        List<ContentPage> all = new ArrayList<>();
        for (Kind kind : Kind.values()) {
            pages(kind).stream().filter(p -> p.episode() != null).forEach(all::add);
        }
        return all;
    }

    public int totalMinutes(Kind kind) {
        return pages(kind).stream().filter(p -> p.episode() != null).mapToInt(p -> p.episode().minutes()).sum();
    }
}
