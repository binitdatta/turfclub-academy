Turf Club Academy — Shared Navbar Integration

This package updates ONLY 9 Agentic AI Thymeleaf templates and the existing shared fragments/layout.html.
No controller or Java sources are changed. Preserve your AgenticAiTrainingController and existing academy CSS.

Copy contents of src/main/resources into the corresponding src/main/resources directory of your existing turfclub-academy project.

The shared layout adds /css/agentic-ai-training.css only on /agentic-ai routes, so the training pages retain their appearance without changing other Academy pages.

Each training page now imports fragments/layout :: head, navbar, footer and scripts instead of its own standalone navigation.

Make sure your already-installed src/main/resources/static/css/agentic-ai-training.css remains present.

Back up your existing src/main/resources/templates/fragments/layout.html before replacing it if you have made newer edits since the previously supplied version.
