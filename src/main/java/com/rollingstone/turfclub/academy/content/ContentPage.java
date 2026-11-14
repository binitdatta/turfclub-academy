package com.rollingstone.turfclub.academy.content;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

/**
 * One teaching page (a business domain, a security topic or a database schema) as stored in
 * {@code src/main/resources/content/<kind>/<slug>.json}. The JSON is generated from the ERP's source code and
 * database by the content generator, so facts such as ports, endpoints, posting rules and columns match the code.
 * HTML inside text fields is trusted content written for this site.
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record ContentPage(
        String kind,
        String slug,
        String title,
        String group,
        String groupLabel,
        int order,
        String icon,
        String subtitle,
        String summary,
        List<Fact> facts,
        List<Section> sections,
        Episode episode) {

    public ContentPage {
        facts = facts == null ? List.of() : List.copyOf(facts);
        sections = sections == null ? List.of() : List.copyOf(sections);
    }

    /** URL of this page inside the Academy. */
    public String href() {
        return Kind.of(kind).path() + "/" + slug;
    }

    /** A label / value pair for the side card; href is optional. */
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Fact(String label, String value, String href) {
    }

    /**
     * A block of content. {@code type} decides which fields are used:
     * text (paragraphs), bullets (items), terms (terms), table (columns + rows), code (code + language + source),
     * mermaid (diagram), dbtables (tables).
     */
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Section(
            String id,
            String title,
            String type,
            String intro,
            List<String> paragraphs,
            List<String> items,
            List<Term> terms,
            List<String> columns,
            List<List<String>> rows,
            String code,
            String language,
            String source,
            String diagram,
            List<DbTable> tables,
            boolean collapsed) {

        public Section {
            paragraphs = paragraphs == null ? List.of() : paragraphs;
            items = items == null ? List.of() : items;
            terms = terms == null ? List.of() : terms;
            columns = columns == null ? List.of() : columns;
            rows = rows == null ? List.of() : rows;
            tables = tables == null ? List.of() : tables;
        }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Term(String term, String definition) {
    }

    /** A database table with its columns ([name, type, nullable, key, default, extra]) and constraints. */
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record DbTable(
            String name,
            String description,
            int rows,
            List<List<String>> columns,
            List<String> foreignKeys,
            List<String> indexes,
            List<String> checks,
            List<String> guards,
            List<String> triggers) {

        public DbTable {
            columns = columns == null ? List.of() : columns;
            foreignKeys = foreignKeys == null ? List.of() : foreignKeys;
            indexes = indexes == null ? List.of() : indexes;
            checks = checks == null ? List.of() : checks;
            guards = guards == null ? List.of() : guards;
            triggers = triggers == null ? List.of() : triggers;
        }
    }

    /** The video plan of a page. */
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Episode(
            String title,
            int minutes,
            String audience,
            String hook,
            List<String> objectives,
            List<String> talkingPoints,
            List<DemoStep> demo,
            List<String> recap) {

        public Episode {
            objectives = objectives == null ? List.of() : objectives;
            talkingPoints = talkingPoints == null ? List.of() : talkingPoints;
            demo = demo == null ? List.of() : demo;
            recap = recap == null ? List.of() : recap;
        }

        /** The outline as plain text, for the "Copy outline" button (script notes, video description). */
        public String outline() {
            StringBuilder sb = new StringBuilder();
            sb.append(title).append(" (").append(minutes).append(" min)\n");
            if (audience != null) {
                sb.append("Audience: ").append(audience).append('\n');
            }
            sb.append("\nHook: ").append(Html.toText(hook)).append("\n\nObjectives\n");
            objectives.forEach(o -> sb.append("- ").append(Html.toText(o)).append('\n'));
            sb.append("\nTalking points\n");
            for (int i = 0; i < talkingPoints.size(); i++) {
                sb.append(i + 1).append(". ").append(Html.toText(talkingPoints.get(i))).append('\n');
            }
            sb.append("\nDemo\n");
            for (int i = 0; i < demo.size(); i++) {
                DemoStep d = demo.get(i);
                sb.append(i + 1).append(". [").append(d.user()).append("] ").append(Html.toText(d.title()))
                  .append(": ").append(Html.toText(d.text())).append('\n');
            }
            sb.append("\nRecap\n");
            recap.forEach(r -> sb.append("- ").append(Html.toText(r)).append('\n'));
            return sb.toString();
        }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record DemoStep(String user, String title, String text) {
    }
}
