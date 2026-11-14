package com.rollingstone.turfclub.academy.content;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.junit.jupiter.api.Test;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;

import com.fasterxml.jackson.databind.ObjectMapper;

/** Every content file parses, uses known section types and links only to pages that exist. */
class ContentLoaderTest {

    private static final Set<String> TYPES = Set.of("text", "bullets", "terms", "table", "code", "mermaid", "dbtables");
    private static final Pattern INTERNAL_LINK = Pattern.compile("(?:href=\"|click \\w+ \")(/(?:domains|security|schemas)/[a-z_-]+)");

    private final ContentLoader loader = new ContentLoader(new ObjectMapper(), "localhost", "http://localhost:8080");

    private List<ContentPage> load(Kind kind) throws IOException {
        List<ContentPage> pages = new ArrayList<>();
        for (Resource r : new PathMatchingResourcePatternResolver().getResources("classpath*:content/" + kind.folder() + "/*.json")) {
            try (InputStream in = r.getInputStream()) {
                pages.add(loader.parse(new String(in.readAllBytes(), StandardCharsets.UTF_8), r.getDescription()));
            }
        }
        return ContentLoader.sorted(pages, kind);
    }

    @Test
    void everyPageLoadsWithKnownSectionsAndAVideoPlan() throws IOException {
        List<ContentPage> domains = load(Kind.DOMAIN);
        List<ContentPage> security = load(Kind.SECURITY);
        List<ContentPage> schemas = load(Kind.SCHEMA);
        assertThat(domains).hasSize(15);
        assertThat(security).hasSize(8);
        assertThat(schemas).hasSize(19);

        Set<String> hrefs = new HashSet<>();
        List<ContentPage> all = new ArrayList<>(domains);
        all.addAll(security);
        all.addAll(schemas);
        all.forEach(p -> hrefs.add(p.href()));

        for (ContentPage page : all) {
            assertThat(page.episode()).as(page.href()).isNotNull();
            assertThat(page.episode().outline()).contains(page.episode().title());
            Set<String> ids = new HashSet<>();
            for (ContentPage.Section s : page.sections()) {
                assertThat(TYPES).as(page.href() + " " + s.id()).contains(s.type());
                assertThat(ids.add(s.id())).as("duplicate section id " + s.id() + " on " + page.href()).isTrue();
                String text = String.join(" ", s.paragraphs()) + String.join(" ", s.items())
                        + s.rows().toString() + (s.diagram() == null ? "" : s.diagram()) + (s.intro() == null ? "" : s.intro());
                Matcher m = INTERNAL_LINK.matcher(text);
                while (m.find()) {
                    assertThat(hrefs).as("link " + m.group(1) + " on " + page.href()).contains(m.group(1));
                }
            }
        }
    }

    @Test
    void navigationKeepsGroupOrder() throws IOException {
        List<NavGroup> nav = ContentLoader.navigation(load(Kind.DOMAIN));
        assertThat(nav).extracting(NavGroup::key).containsExactly("core", "racing", "betting", "club", "supply", "finance", "ai");
        assertThat(nav.get(1).links()).extracting(NavGroup.NavLink::title)
                                      .containsExactly("Horse Registry", "Jockeys, Owners & Trainers", "Race Operations");
    }

    @Test
    void localhostLinksFollowTheConfiguredHost() {
        ContentLoader remote = new ContentLoader(new ObjectMapper(), "erp.lab", "http://kc.lab:8080");
        ContentPage page = remote.parse("{\"kind\":\"domain\",\"slug\":\"x\",\"title\":\"X\",\"summary\":\"<a href=\\\"http://localhost:8103/\\\">a</a> http://localhost:8080/admin\"}", "inline");
        assertThat(page.summary()).contains("http://erp.lab:8103/").contains("http://kc.lab:8080/admin");
    }
}
