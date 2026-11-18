# Turf Club Academy — Agentic AI pages repair

This patch contains **nine** existing Academy Thymeleaf training pages. Four pages additionally embed real source code, using the original uploaded application snapshot:
- `turfbot-walkthrough.html`: 16 source files
- `workforce.html`: 5 source files
- `rex.html`: 3 source files
- `cleo.html`: 3 source files

The source listings are expandable under **Read the real source code**; a **View actual Python source code** jump link near the top leads directly there.

## Why the dropdown appeared to fail

The shared navbar uses Bootstrap 5 `data-bs-toggle="dropdown"`, which needs Bootstrap's JavaScript bundle. On these pages the JavaScript is injected by the Thymeleaf `fragments/layout :: scripts` fragment. If the CDN bundle is unavailable or fails to load, the anchor defaults to `href="#"` and the menu does not open.

This patch keeps the shared navbar and its scripts, adds desktop hover/focus fallback, and installs a lightweight native click/keyboard fallback **only when the Bootstrap dropdown JavaScript is absent**. It avoids a second Bootstrap initialization.

## Install

From your existing Academy project root:

```bash
unzip -o ~/Downloads/turfclub-academy-agentic-ai-dropdown-and-code-fix.zip -d .
```

Rebuild and restart through your normal process. No Java source, `application.yml`, navbar `layout.html`, or Academy controller is changed by this ZIP.

## Verification

Navigate to `http://localhost:8130/agentic-ai/workforce`, open **Agentic AI** in the top navbar, and select **Rex**. On the Workforce page select **View actual Python source code**, then expand `workforce/workforce/worker.py` or other files.
