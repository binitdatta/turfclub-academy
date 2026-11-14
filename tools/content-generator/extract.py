#!/usr/bin/env python3
"""Extracts facts about the Turf Club ERP from its source tree and the live MySQL schema into build/facts.json.

usage: extract.py <erp-root>      (MySQL from MYSQL_HOST / MYSQL_PORT / MYSQL_USER / MYSQL_PASSWORD, default root / localroot)
Run it against a freshly installed database (database/install-db.sh --reset) so the row counts are the seed data."""
import json, os, re, subprocess, glob, sys

ERP = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "../../../turfclub-erp")
HERE = os.path.dirname(os.path.abspath(__file__))
MYSQL = ["mysql", "-h", os.environ.get("MYSQL_HOST", "127.0.0.1"), "-P", os.environ.get("MYSQL_PORT", "3306"),
         "-u", os.environ.get("MYSQL_USER", "root"), "-N", "-B"]
os.environ.setdefault("MYSQL_PWD", os.environ.get("MYSQL_PASSWORD", "localroot"))
SERVICES = [
    ("core", "core-service", "core", "CORE", "enterprise_core", 8101),
    ("gl", "finance-gl-service", "gl", "GL", "financial_gl", 8102),
    ("horse", "horse-registry-service", "horse", "HORSE", "horse_registry", 8103),
    ("participants", "racing-participants-service", "participant", "PARTICIPANT", "racing_participants", 8104),
    ("racing", "racing-operations-service", "racing", "RACING", "racing_operations", 8105),
    ("wagering", "wagering-service", "wagering", "WAGERING", "wagering", 8106),
    ("prizes", "prizes-settlement-service", "prizes", "PRIZE", "prizes_settlement", 8107),
    ("membership", "membership-service", "membership", "MEMBERSHIP", "membership", 8108),
    ("hospitality", "hospitality-service", "hospitality", "HOSPITALITY", "hospitality", 8109),
    ("inventory", "inventory-service", "inventory", "INVENTORY", "inventory", 8110),
    ("purchasing", "procurement-service", "procurement", "PROCUREMENT", "procurement", 8111),
    ("ap", "finance-ap-service", "ap", "AP", "financial_ap", 8112),
    ("ar", "finance-ar-service", "ar", "AR", "financial_ar", 8113),
    ("treasury", "treasury-service", "treasury", "TREASURY", "treasury", 8114),
]
# outbox source_module per service (may differ from role prefix)
EVENT_MODULE = {"core": "CORE", "gl": None, "horse": "HORSE", "participants": "PARTICIPANT", "racing": "RACING",
                "wagering": "WAGERING", "prizes": "PRIZE", "membership": "MEMBERSHIP", "hospitality": "HOSPITALITY",
                "inventory": "INVENTORY", "purchasing": "PROCUREMENT", "ap": "AP", "ar": "AR", "treasury": "TREASURY"}


def sql(query):
    out = subprocess.run(MYSQL + ["-e", query], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"MySQL query failed: {out.stderr.strip()}")
    rows = []
    for line in out.stdout.splitlines():
        rows.append([None if c == "NULL" else c for c in line.split("\t")])
    return rows


def menu(svc_dir):
    path = f"{ERP}/{svc_dir}/src/main/resources/templates/fragments/module-menu.html"
    items, section = [], None
    for line in open(path):
        m = re.search(r'tc-sidebar-section">([^<]*)<', line)
        if m:
            section = m.group(1).strip()
        m = re.search(r"navItem\('([^']*)', '([^']*)', '([^']*)'\)", line)
        if m:
            items.append({"section": section, "url": m.group(1), "icon": m.group(2), "label": m.group(3)})
    return items


def api(svc_dir, pkg):
    rows = []
    for f in sorted(glob.glob(f"{ERP}/{svc_dir}/src/main/java/com/rollingstone/turfclub/{pkg}/api/*Controller.java")):
        src = open(f).read()
        base = re.search(r'@RequestMapping\("([^"]*)"\)', src)
        base = base.group(1) if base else ""
        for m in re.finditer(r'@(Get|Post|Put|Delete)Mapping(?:\("([^"]*)"\))?\s*(?:@PreAuthorize\("([^"]*)"\)\s*)?public\s+[\w<>, ?]+\s+(\w+)\(', src):
            rows.append({"method": m.group(1).upper(), "path": base + (m.group(2) or ""), "handler": m.group(4),
                         "auth": m.group(3), "file": os.path.relpath(f, ERP)})
    return rows


def classes(svc_dir, pkg):
    root = f"{ERP}/{svc_dir}/src/main/java/com/rollingstone/turfclub/{pkg}"
    out = {}
    for sub in sorted(os.listdir(root)):
        p = os.path.join(root, sub)
        if os.path.isdir(p):
            out[sub] = sorted(f[:-5] for f in os.listdir(p) if f.endswith(".java"))
    return out


def entities(svc_dir, pkg):
    rows = []
    for f in sorted(glob.glob(f"{ERP}/{svc_dir}/src/main/java/com/rollingstone/turfclub/{pkg}/domain/*.java")):
        src = open(f).read()
        if "@Entity" not in src:
            continue
        t = re.search(r'@Table\(name\s*=\s*"([^"]*)"', src)
        ro = "@Immutable" in src
        rows.append({"class": os.path.basename(f)[:-5], "table": t.group(1) if t else None, "readOnly": ro})
    return rows


facts = {"services": {}, "schemas": {}, "rules": [], "fees": [], "settings": []}
for slug, d, pkg, code, schema, port in SERVICES:
    facts["services"][slug] = {"dir": d, "package": f"com.rollingstone.turfclub.{pkg}", "code": code, "schema": schema,
                               "port": port, "menu": menu(d), "api": api(d, pkg), "classes": classes(d, pkg),
                               "entities": entities(d, pkg), "eventModule": EVENT_MODULE[slug]}

for r in sql("select r.source_module, r.event_code, d.account_code, d.name, c.account_code, c.name from financial_gl.posting_rule r "
             "join financial_gl.gl_account d on d.id=r.debit_account_id join financial_gl.gl_account c on c.id=r.credit_account_id order by 1,2"):
    facts["rules"].append(dict(zip(["module", "event", "dr", "drName", "cr", "crName"], r)))
for r in sql("select module_code, fee_code, description, currency, amount from reference_data.fee_schedule where active=1 order by 1,2"):
    facts["fees"].append(dict(zip(["module", "code", "description", "currency", "amount"], r)))

schemas = [r[0] for r in sql("select schema_name from information_schema.schemata where schema_name not in "
                              "('mysql','sys','performance_schema','information_schema','chatbot_test') order by 1")]
for s in schemas:
    tables = []
    for t, rows, engine in sql(f"select table_name, table_rows, engine from information_schema.tables where table_schema='{s}' and table_type='BASE TABLE' order by table_name"):
        cols = [dict(zip(["name", "type", "nullable", "key", "default", "extra"], c)) for c in
                sql(f"select column_name, column_type, is_nullable, column_key, column_default, extra from information_schema.columns "
                    f"where table_schema='{s}' and table_name='{t}' order by ordinal_position")]
        fks = [dict(zip(["name", "column", "refSchema", "refTable", "refColumn"], f)) for f in
               sql(f"select constraint_name, column_name, referenced_table_schema, referenced_table_name, referenced_column_name "
                   f"from information_schema.key_column_usage where table_schema='{s}' and table_name='{t}' and referenced_table_name is not null order by constraint_name, ordinal_position")]
        idx = {}
        for name, uniq, col in sql(f"select index_name, non_unique, column_name from information_schema.statistics where table_schema='{s}' "
                                    f"and table_name='{t}' order by index_name, seq_in_index"):
            idx.setdefault(name, {"name": name, "unique": uniq == "0", "columns": []})["columns"].append(col)
        checks = [dict(zip(["name", "clause"], c)) for c in sql(
            f"select cc.constraint_name, cc.check_clause from information_schema.check_constraints cc join information_schema.table_constraints tc "
            f"on tc.constraint_schema=cc.constraint_schema and tc.constraint_name=cc.constraint_name where tc.table_schema='{s}' and tc.table_name='{t}'")]
        count = sql(f"select count(*) from `{s}`.`{t}`")[0][0]
        tables.append({"name": t, "rows": int(count), "columns": cols, "foreignKeys": fks, "indexes": list(idx.values()), "checks": checks})
    trig = []
    for name, timing, event, table, body in sql(f"select trigger_name, action_timing, event_manipulation, event_object_table, "
                                                 f"replace(replace(action_statement, '\\n', ' '), '\\t', ' ') from information_schema.triggers where trigger_schema='{s}' order by event_object_table, trigger_name"):
        msgs = sorted(set(re.findall(r"MESSAGE_TEXT\s*=\s*'([^']*)'", body or "")))
        kind = "audit" if "audit_event" in (body or "") else ("version" if "version_no" in (body or "") and not msgs else ("guard" if msgs else "other"))
        trig.append({"name": name, "timing": timing, "event": event, "table": table, "kind": kind, "messages": msgs})
    facts["schemas"][s] = {"tables": tables, "triggers": trig}

os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
json.dump(facts, open(os.path.join(HERE, "build", "facts.json"), "w"), indent=1)
print({k: len(v) for k, v in facts.items()}, sum(len(x["tables"]) for x in facts["schemas"].values()))
for slug, s in facts["services"].items():
    print(slug, len(s["menu"]), len(s["api"]), len(s["entities"]))
