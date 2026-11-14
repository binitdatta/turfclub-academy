# Turf Club ERP Academy

A Spring Boot 3.4.9 + Thymeleaf site (same Bootstrap 5 **Bright Blue** theme as the ERP) for making education videos
about the Rollingstone Turf Club ERP. Port **8130**. No database and no sign-in: it is a read-only teaching site.

## Run

```bash
cd ~/Development/Turf_Club/turfclub-academy
mvn spring-boot:run
```
Open http://localhost:8130. Or build a jar: `mvn clean package` then `java -jar target/turfclub-academy-1.0.0-SNAPSHOT.jar`.

Settings (environment variables): `ACADEMY_PORT` (8130), `ERP_HOST` (localhost - the host the "open the live screen"
links point to), `KEYCLOAK_URL` (http://localhost:8080).

## What is in it

| Menu | Pages |
|---|---|
| **Architecture** (home) | Interactive system map (click a box to trace its connections), the seven layers, how the modules work together, three money paths, module tiles, technology, the whole video series with minutes, a pre-recording checklist |
| **Business Domains** | 15 pages grouped Shared core · Racing · Betting & prizes · Members & hospitality · Supply · Finance · AI assistant |
| **Security · Keycloak · OAuth2 · OIDC** | The realm, roles and composites, browser sign-in (OIDC + PKCE), APIs as resource servers, client credentials between services, TurfBot's stateless PKCE, sign-out and sessions, identity in the database |
| **Database Schemas** | 19 schemas: tables, ER diagram, guard triggers, every column, key, index, check and guard message |

Every page has a **video plan**: hook, learning objectives, talking points, a live demo script with the user to sign in
as, and a recap. **Copy outline** copies it as text for your notes or the video description. Domain pages also carry
key concepts, a connection diagram, design decisions, screens (with links that open the live ERP screen), REST API,
accounting events with debit / credit accounts, fees and settings, owned tables, database-enforced rules, a code tour
and the test cases from the testing READMEs. Every diagram has a **Download SVG** button.

**Presenter mode** (top bar) enlarges the text and hides the side panels while you record; it is remembered per browser.

## Where the content comes from

`src/main/resources/content/{domains,security,schemas}/*.json` is generated - facts such as ports, menus, endpoints,
posting rules, fees, tables, columns, triggers and code snippets are read from the ERP's source and database, the
teaching text comes from `tools/content-generator/{domains,security,schemas}.py`.

After changing the ERP (or the teaching text), regenerate:
```bash
cd ~/Development/Turf_Club/turfclub-erp/database && ./install-db.sh --reset
cd ~/Development/Turf_Club/turfclub-academy
bash tools/content-generator/generate.sh ~/Development/Turf_Club/turfclub-erp ~/Development/Turf_Club/turfclub-testing
```
It needs python3 (with no extra packages), the `mysql` client (root / localroot by default, or `MYSQL_USER` /
`MYSQL_PASSWORD`) and the chatbot's virtualenv `turfclub-erp/chatbot/.venv` (to list TurfBot's tools). The second
argument is the folder of the testing READMEs; leave it out if you do not have them.

## Project layout

```
src/main/java/com/rollingstone/turfclub/academy/
  AcademyApplication, AcademyProperties
  content/  ContentPage (the page model), ContentLoader (JSON -> pages, navigation), ContentRepository, Kind, NavGroup, Html
  web/      HomeController (/), PageController (/domains/{slug}, /security/{slug}, /schemas/{slug}), NavigationAdvice
src/main/resources/
  templates/  index.html, page.html, error.html, fragments/layout.html (head, navbar, footer, scripts), fragments/sections.html
  static/     css/academy.css, js/academy.js (presenter mode, copy, highlight, Mermaid), js/architecture.js (system map)
  content/    generated JSON
tools/content-generator/  extract.py, export_tools.py, build.py, domains.py, security.py, schemas.py, generate.sh
```
Bootstrap 5.3.3, Bootstrap Icons 1.11.3, Mermaid 11.4.1 and highlight.js 11.9.0 load from public CDNs.

## Test
`mvn test` checks that every content file parses, every page has a video plan, section types are known and every
internal link points to a page that exists.
