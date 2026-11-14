package com.rollingstone.turfclub.academy.content;

import java.util.List;

/** A titled group of navigation links (a column in a navbar dropdown). */
public record NavGroup(String key, String label, List<NavLink> links) {

    /** A navigation entry. {@code meta} is a short hint shown next to the title (port, table count ...). */
    public record NavLink(String title, String href, String icon, String meta) {
    }
}
