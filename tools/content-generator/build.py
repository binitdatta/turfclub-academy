#!/usr/bin/env python3
"""Builds the Academy's content JSON (src/main/resources/content/**) from build/facts.json, build/tools.json and the
hand-written teaching content in domains.py, security.py and schemas.py.

usage: build.py <erp-root> <testing-readmes-root or -> <output content folder>"""
import html
import json
import os
import re
import sys

from domains import DOMAINS, GROUPS
from schemas import SCHEMA_GROUPS, SCHEMAS
from security import TOPICS

ERP = os.path.abspath(sys.argv[1])
TESTS = None if sys.argv[2] == "-" else os.path.abspath(sys.argv[2])
OUT = os.path.abspath(sys.argv[3])
HERE = os.path.dirname(os.path.abspath(__file__))
facts = json.load(open(os.path.join(HERE, "build", "facts.json")))
tools = json.load(open(os.path.join(HERE, "build", "tools.json")))
GROUP_LABEL = dict(GROUPS)
SCHEMA_GROUP_LABEL = dict(SCHEMA_GROUPS)
TEST_DIRS = {"core": "01-core", "gl": "02-general-ledger", "horse": "03-horse-registry", "participants": "04-participants",
             "racing": "05-race-operations", "wagering": "06-wagering", "prizes": "07-prizes", "membership": "08-membership",
             "hospitality": "09-hospitality", "inventory": "10-inventory", "purchasing": "11-purchasing",
             "ap": "12-accounts-payable", "ar": "13-accounts-receivable", "treasury": "14-treasury", "turfbot": "15-turfbot"}
SCHEMA_OF = {slug: s["schema"] for slug, s in facts["services"].items()}
SCHEMA_OF["turfbot"] = "chatbot"
CLIENT = {"core": "svc-core", "gl": "svc-gl", "horse": "svc-horse", "participants": "svc-participants", "racing": "svc-racing",
          "wagering": "svc-wagering", "prizes": "svc-prizes", "membership": "svc-membership", "hospitality": "svc-hospitality",
          "inventory": "svc-inventory", "purchasing": "svc-procurement", "ap": "svc-ap", "ar": "svc-ar", "treasury": "svc-treasury",
          "turfbot": "svc-chatbot"}
KIND_LABEL = {"REST": "live REST call", "event": "accounting event", "import": "AR import", "shared data": "shared master data", "data": "reads data"}


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=False)


def md_inline(s):
    """Markdown cell text from the test READMEs -> safe HTML (code, bold, italics)."""
    s = esc(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", s)
    return s


def section(sid, title, stype, **kw):
    return {"id": sid, "title": title, "type": stype, **kw}


def test_sections(slug):
    if TESTS is None or not os.path.exists(os.path.join(TESTS, TEST_DIRS[slug], "README.md")):
        return []
    path = os.path.join(TESTS, TEST_DIRS[slug], "README.md")
    out, title, buf = [], None, []

    def flush():
        rows = [r for r in buf if not re.match(r"^\|\s*-", r)]
        if title and len(rows) > 1:
            cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
            out.append({"title": title, "columns": [md_inline(c) for c in cells[0]], "rows": [[md_inline(c) for c in r] for r in cells[1:]]})

    for line in open(path):
        if line.startswith("## "):
            flush()
            title, buf = line[3:].strip(), []
        elif line.startswith("|"):
            buf.append(line.rstrip("\n"))
    flush()
    return out


def node_id(slug):
    return "n_" + slug


def integration_diagram(slug, d):
    lines = ["flowchart LR", f'  {node_id(slug)}["<b>{d["title"]}</b>"]', f"  class {node_id(slug)} me"]
    seen = set()
    for direction, other, kind, what in d["integrations"]:
        if other not in seen:
            lines.append(f'  {node_id(other)}["{DOMAINS[other]["title"]}"]')
            lines.append(f'  click {node_id(other)} "/domains/{other}"')
            seen.add(other)
        arrow = {"REST": "-->", "event": "-.->", "import": "-.->", "shared data": "---", "data": "-->"}[kind]
        label = what.replace('"', "'")
        if direction == "out":
            lines.append(f'  {node_id(slug)} {arrow}|"{label}"| {node_id(other)}')
        else:
            lines.append(f'  {node_id(other)} {arrow}|"{label}"| {node_id(slug)}')
    lines.append("  classDef me fill:#3b5bfd,color:#fff,stroke:#2a46d6")
    return "\n".join(lines)


def episode(e, default_audience=None):
    return {"title": e["title"], "minutes": e["minutes"], "audience": e.get("audience", default_audience or "Developers and architects"),
            "hook": e["hook"], "objectives": e["objectives"], "talkingPoints": e["talkingPoints"],
            "demo": [{"user": u, "title": t, "text": x} for u, t, x in e["demo"]], "recap": e["recap"]}


def guard_rows(schema):
    rows = []
    for t in facts["schemas"][schema]["triggers"]:
        for m in t["messages"]:
            rows.append([f"<code>{esc(t['table'])}</code>", f"{t['timing']} {t['event']}", esc(m)])
    return rows


def write(kind, slug, page):
    os.makedirs(os.path.join(OUT, kind), exist_ok=True)
    with open(os.path.join(OUT, kind, slug + ".json"), "w") as f:
        json.dump(page, f, indent=1, ensure_ascii=False)


# ------------------------------------------------------------------ domains
for slug, d in DOMAINS.items():
    svc = facts["services"].get(slug)
    schema = SCHEMA_OF[slug]
    port = svc["port"] if svc else d.get("port")
    code = svc["code"] if svc else "CHATBOT"
    sections = [
        section("overview", "Overview", "text", paragraphs=d["story"]),
        section("concepts", "Key concepts", "terms", terms=[{"term": a, "definition": b} for a, b in d["concepts"]]),
        section("connections", "How it connects", "mermaid", diagram=integration_diagram(slug, d),
                intro="Solid arrows are live REST calls, dotted arrows are accounting events or the AR import, plain lines are shared master data. Click a box to open that module."),
        section("connections-table", "Connections in detail", "table", columns=["Direction", "Module", "Mechanism", "What"],
                rows=[["calls / sends to" if dr == "out" else "used by", f'<a href="/domains/{o}">{esc(DOMAINS[o]["title"])}</a>',
                       KIND_LABEL[k], esc(w)] for dr, o, k, w in d["integrations"]]),
        section("decisions", "Design decisions", "bullets", items=d["decisions"]),
    ]
    if svc:
        sections.append(section("screens", "Screens", "table", columns=["Menu section", "Screen", "URL"],
                                rows=[[esc(m["section"] or ""), f'<i class="bi {m["icon"]} me-1"></i>{esc(m["label"])}',
                                       f'<a href="http://localhost:{port}{m["url"]}" target="_blank" rel="noopener"><code>:{port}{esc(m["url"])}</code></a>']
                                      for m in svc["menu"]] +
                                     [["Administration", '<i class="bi bi-cash-stack me-1"></i>Fee Schedule', f"<code>:{port}/admin/fees</code>"],
                                      ["Administration", '<i class="bi bi-list-ul me-1"></i>Reference Data', f"<code>:{port}/admin/reference-data</code>"]]))
        sections.append(section("api", "REST API (/api/v1)", "table", columns=["Method", "Path", "Handler", "Access"],
                                intro="Read by other services with client-credentials tokens (SVC_READ) and by TurfBot as svc-chatbot.",
                                rows=[[f'<span class="badge text-bg-light border">{a["method"]}</span>', f"<code>{esc(a['path'])}</code>",
                                       f"<code>{esc(a['handler'])}()</code>", esc(a["auth"] or f"SVC_READ or {code}_VIEW")] for a in svc["api"]]))
        em = svc["eventModule"]
        rules = [r for r in facts["rules"] if (r["module"] == em if em else True)]
        if slug == "gl":
            counts = {}
            for r in facts["rules"]:
                counts[r["module"]] = counts.get(r["module"], 0) + 1
            sections.append(section("events", "Posting rules by source module", "table", columns=["Source module", "Rules"],
                                    intro="The GL receives events from every module; each module page lists its own events with debit and credit accounts.",
                                    rows=[[esc(k), str(v)] for k, v in sorted(counts.items())]))
        elif rules:
            sections.append(section("events", "Accounting events it emits", "table", columns=["Event code", "Debit", "Credit"],
                                    intro="Written to the outbox in the same transaction as the business change and posted by the GL with these rules.",
                                    rows=[[f"<code>{esc(r['event'])}</code>", f"{r['dr']} {esc(r['drName'])}", f"{r['cr']} {esc(r['crName'])}"] for r in rules]))
        fees = [f for f in facts["fees"] if f["module"] == code]
        if fees:
            sections.append(section("fees", "Fees and settings", "table", columns=["Code", "Description", "Value"],
                                    intro="Maintained under Administration → Fee Schedule (reference_data.fee_schedule).",
                                    rows=[[f"<code>{esc(f['code'])}</code>", esc(f["description"]), f"{esc(f['amount'])} {esc(f['currency'] or '')}".strip()] for f in fees]))
        ent = {e["table"]: e for e in svc["entities"] if e["table"]}
        own = [t for t in facts["schemas"][schema]["tables"]]
        sections.append(section("data", "Data it owns", "table", columns=["Table", "JPA entity", "Seed rows"],
                                intro=f'Schema <a href="/schemas/{schema}"><code>{schema}</code></a>. Read-only references to other schemas come from turfclub-common.',
                                rows=[[f'<a href="/schemas/{schema}#t-{t["name"]}"><code>{t["name"]}</code></a>',
                                       f"<code>{ent[t['name']]['class']}</code>" if t["name"] in ent else "—", str(t["rows"])] for t in own]))
        g = guard_rows(schema)
        if g:
            sections.append(section("guards", "Rules enforced by the database", "table", columns=["Table", "Trigger", "Message"],
                                    intro="Guard triggers refuse changes that would break a business rule, whatever path the change takes.", rows=g))
        sections.append(section("code", "Code tour", "table", columns=["Package", "Classes"],
                                intro=f"<code>{svc['dir']}/src/main/java/{svc['package'].replace('.', '/')}</code>",
                                rows=[[f"<code>{esc(p)}</code>", ", ".join(f"<code>{esc(c)}</code>" for c in cs)] for p, cs in svc["classes"].items() if cs]))
    else:
        sections.append(section("tools", "Tools Claude can use", "table", columns=["Tool", "Module", "What it answers"],
                                intro="Each tool is offered only to users whose roles open its module. Audit tools need TC_AUDITOR or TC_ADMIN.",
                                rows=[[f"<code>{esc(t['name'])}</code>", "AUDIT" if t["audit"] else esc(t["module"]), esc(t["description"])] for t in tools]))
        files = []
        for root, _, fs in os.walk(os.path.join(ERP, "chatbot", "turfbot")):
            for f in sorted(fs):
                if f.endswith((".py", ".html", ".js", ".css")):
                    files.append(os.path.relpath(os.path.join(root, f), os.path.join(ERP, "chatbot")))
        groups = {}
        for f in sorted(files):
            groups.setdefault(os.path.dirname(f), []).append(os.path.basename(f))
        sections.append(section("code", "Code tour", "table", columns=["Folder", "Files"], intro="<code>chatbot/</code>",
                                rows=[[f"<code>{esc(k)}</code>", ", ".join(f"<code>{esc(x)}</code>" for x in v)] for k, v in groups.items()]))
        sections.append(section("data", "Data it owns", "table", columns=["Table", "Rows"], intro='Schema <a href="/schemas/chatbot"><code>chatbot</code></a>',
                                rows=[[f'<a href="/schemas/chatbot#t-{t["name"]}"><code>{t["name"]}</code></a>', str(t["rows"])] for t in facts["schemas"]["chatbot"]["tables"]]))
    for i, t in enumerate(test_sections(slug)):
        sections.append(section(f"test-{i}", "Test cases · " + t["title"], "table", columns=t["columns"], rows=t["rows"], collapsed=True))

    fact_rows = [
        {"label": "Port", "value": f":{port}", "href": f"http://localhost:{port}/"},
        {"label": "Module code", "value": code},
        {"label": "Roles", "value": f"{code}_VIEW · {code}_MANAGE" if svc else "users' own roles"},
        {"label": "Service client", "value": CLIENT[slug]},
        {"label": "Schema", "value": schema, "href": f"/schemas/{schema}"},
        {"label": "Delivered in", "value": f"Stage {d['stage']}"},
        {"label": "Source", "value": svc["dir"] if svc else "chatbot/"},
    ]
    page = {"kind": "domain", "slug": slug, "title": d["title"], "group": d["group"], "groupLabel": GROUP_LABEL[d["group"]],
            "order": d["order"], "icon": d["icon"], "subtitle": d["subtitle"], "summary": d["summary"], "facts": fact_rows,
            "sections": sections, "episode": episode(d["episode"])}
    write("domains", slug, page)


# ------------------------------------------------------------------ security
def snippet(rel, markers):
    lines = open(os.path.join(ERP, rel)).read().splitlines()
    start_re, end_re = markers
    start = next(i for i, l in enumerate(lines) if re.search(start_re, l))
    if start > 0 and lines[start - 1].strip().startswith("@") and not lines[start].strip().startswith("@"):
        start -= 1
    while start > 0 and lines[start - 1].strip().startswith(("@Bean", "@Order", "/**", "*")) and not lines[start].strip().startswith("/**"):
        start -= 1
    end = len(lines) - 1
    if end_re:
        end = next(i for i in range(start + 1, len(lines)) if re.search(end_re, lines[i]))
    block = lines[start:end + 1]
    indent = min((len(l) - len(l.lstrip()) for l in block if l.strip()), default=0)
    return "\n".join(l[indent:] for l in block)


for t in TOPICS:
    secs = []
    for i, s in enumerate(t["sections"]):
        kind, title = s[0], s[1]
        sid = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        if kind == "text":
            secs.append(section(sid, title, "text", paragraphs=s[2]))
        elif kind == "bullets":
            secs.append(section(sid, title, "bullets", items=s[2]))
        elif kind == "table":
            secs.append(section(sid, title, "table", columns=s[2], rows=s[3]))
        elif kind == "mermaid":
            secs.append(section(sid, title, "mermaid", diagram=s[3]))
        elif kind == "code":
            lang, rel, markers, literal = s[2], s[3], s[4], s[5]
            secs.append(section(sid, title, "code", language=lang, source=rel,
                                code=literal if literal is not None else snippet(rel, markers)))
    page = {"kind": "security", "slug": t["slug"], "title": t["title"], "group": "security", "groupLabel": "Security",
            "order": t["order"], "icon": t["icon"], "subtitle": t["subtitle"], "summary": t["summary"],
            "facts": [{"label": "Identity provider", "value": "Keycloak 26 · realm turfclub", "href": "http://localhost:8080/admin/"},
                      {"label": "Protocols", "value": "OAuth 2.0 · OpenID Connect"},
                      {"label": "Spring Security", "value": "oauth2Login · oauth2ResourceServer · oauth2Client"}],
            "sections": secs, "episode": episode(t["episode"])}
    write("security", t["slug"], page)


# ------------------------------------------------------------------ schemas
def simple_type(t):
    return re.sub(r"[^a-z]", "", t.split("(")[0].split(" ")[0]) or "col"


for schema, (grp, order, owner, desc, table_desc) in SCHEMAS.items():
    sf = facts["schemas"][schema]
    tables = sf["tables"]
    names = {t["name"] for t in tables}
    # ER diagram: keys, foreign keys and status-like columns only
    er = ["erDiagram"]
    external = set()
    for t in tables:
        fkcols = {f["column"] for f in t["foreignKeys"]}
        attrs = []
        for c in t["columns"]:
            tag = "PK" if c["key"] == "PRI" else ("FK" if c["name"] in fkcols else ("UK" if c["key"] == "UNI" else None))
            if tag or c["name"] in ("status", "code", "name", "title"):
                attrs.append(f"    {simple_type(c['type'])} {c['name']}" + (f" {tag}" if tag else ""))
        er.append(f"  {t['name']} {{")
        er.extend(attrs[:12])
        er.append("  }")
    for t in tables:
        for f in t["foreignKeys"]:
            target = f["refTable"] if f["refSchema"] == schema else f"{f['refSchema']}__{f['refTable']}"
            if f["refSchema"] != schema:
                external.add(target)
            er.append(f'  {target} ||--o{{ {t["name"]} : "{f["column"]}"')
    for x in sorted(external):
        er.append(f"  {x} {{\n    bigint id PK\n  }}")
    dbtables = []
    for t in tables:
        guards = sorted({m for tr in sf["triggers"] if tr["table"] == t["name"] for m in tr["messages"]})
        trig_kinds = sorted({tr["kind"] for tr in sf["triggers"] if tr["table"] == t["name"]})
        dbtables.append({
            "name": t["name"], "description": table_desc.get(t["name"], ""), "rows": t["rows"],
            "columns": [[c["name"], c["type"], "yes" if c["nullable"] == "YES" else "no", c["key"] or "",
                         c["default"] if c["default"] is not None else "", c["extra"] or ""] for c in t["columns"]],
            "foreignKeys": [f"{f['column']} → {f['refSchema'] + '.' if f['refSchema'] != schema else ''}{f['refTable']}.{f['refColumn']}" for f in t["foreignKeys"]],
            "indexes": [f"{'UNIQUE ' if i['unique'] else ''}{i['name']} ({', '.join(i['columns'])})" for i in t["indexes"]],
            "checks": [f"{c['name']}: {c['clause']}" for c in t["checks"]],
            "guards": guards, "triggers": trig_kinds})
    kinds = {}
    for tr in sf["triggers"]:
        kinds[tr["kind"]] = kinds.get(tr["kind"], 0) + 1
    owner_title = DOMAINS[owner]["title"]
    secs = [
        section("overview", "Overview", "text", paragraphs=[
            esc(desc),
            f'Owned by <a href="/domains/{owner}">{esc(owner_title)}</a>. ' +
            ("Other services read it through read-only JPA entities in turfclub-common." if schema in ("enterprise_core", "reference_data", "financial_gl") else
             "No other service writes to it; they ask its owner through /api/v1 or read posted events."),
            "Every table carries <code>created_at / created_by / updated_at / updated_by / version_no</code>; audit triggers copy each change into <code>audit_compliance.audit_event</code>, and version triggers increment <code>version_no</code> for optimistic locking."
            if schema not in ("chatbot",) else "TurfBot owns this schema; guard triggers make the AI audit trail append-only."]),
        section("tables", "Tables", "table", columns=["Table", "What it holds", "Columns", "Seed rows"],
                rows=[[f'<a href="#t-{t["name"]}"><code>{t["name"]}</code></a>', esc(table_desc.get(t["name"], "")), str(len(t["columns"])), str(t["rows"])] for t in tables]),
        section("er", "Entity relationships", "mermaid", diagram="\n".join(er),
                intro="Primary keys, foreign keys and identifying columns. Tables from other schemas are shown as schema__table."),
    ]
    g = guard_rows(schema)
    if g:
        secs.append(section("guards", "Guard triggers", "table", columns=["Table", "Trigger", "Message"], rows=g,
                            intro="Business rules the database enforces on its own."))
    secs.append(section("details", "Table details", "dbtables", tables=dbtables))
    page = {"kind": "schema", "slug": schema, "title": schema, "group": grp, "groupLabel": SCHEMA_GROUP_LABEL[grp], "order": order,
            "icon": "bi-database", "subtitle": esc(desc), "summary": esc(desc),
            "facts": [{"label": "Owner", "value": owner_title, "href": f"/domains/{owner}"},
                      {"label": "Tables", "value": str(len(tables))},
                      {"label": "Seed rows", "value": str(sum(t["rows"] for t in tables))},
                      {"label": "Audit triggers", "value": str(kinds.get("audit", 0))},
                      {"label": "Version triggers", "value": str(kinds.get("version", 0))},
                      {"label": "Guard triggers", "value": str(kinds.get("guard", 0))}],
            "sections": secs,
            "episode": {"title": f"Inside the {schema} schema", "minutes": max(5, min(12, 3 + len(tables))),
                        "audience": "Developers and DBAs", "hook": f"What does {owner_title} remember, and which rules can no code path break?",
                        "objectives": ["Walk the tables and their relationships", "Show the guard triggers in action", "Connect the tables to the screens that use them"],
                        "talkingPoints": [f"{t['name']}: {table_desc.get(t['name'], '')}" for t in tables][:10] +
                                         (["Guard triggers: " + "; ".join(r[2] for r in g[:3])] if g else []),
                        "demo": [{"user": "root", "title": "Open the schema", "text": f"mysql -uroot -p {schema} → SHOW TABLES; SHOW TRIGGERS;"},
                                 {"user": "auditor", "title": "See the audit trail", "text": f"Core → Audit Trail → filter schema {schema}."}],
                        "recap": ["One schema per service", "Rules live in the database too", "Every change is audited"]}}
    write("schemas", schema, page)

print("pages:", sum(len(os.listdir(os.path.join(OUT, k))) for k in os.listdir(OUT)))
