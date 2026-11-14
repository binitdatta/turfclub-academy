package com.rollingstone.turfclub.academy.content;

/** Tiny helpers for the trusted HTML snippets in the content files. */
public final class Html {

    private Html() {
    }

    /** Strips tags and decodes the few entities the content uses. */
    public static String toText(String html) {
        if (html == null) {
            return "";
        }
        return html.replaceAll("<[^>]+>", "")
                   .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", "\"").replace("&#39;", "'")
                   .replace("&amp;", "&");
    }
}
