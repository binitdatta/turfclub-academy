/* Turf Club ERP Academy - the interactive system map on the home page (click a box to trace its connections). */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  var svg = document.getElementById("arch");

  var DOMAINS = {
    channel: { color: "--d-ident", soft: "--tc-card", tag: "Channel" },
    ident: { color: "--d-ident", soft: "--d-ident-soft", tag: "Identity" },
    ai: { color: "--d-ai", soft: "--d-ai-soft", tag: "External AI" },
    bot: { color: "--d-ai", soft: "--tc-card", tag: "Assistant" },
    core: { color: "--d-core", soft: "--d-core-soft", tag: "Shared core" },
    racing: { color: "--d-racing", soft: "--d-racing-soft", tag: "Racing" },
    betting: { color: "--d-betting", soft: "--d-betting-soft", tag: "Betting & prizes" },
    club: { color: "--d-club", soft: "--d-club-soft", tag: "Members & hospitality" },
    supply: { color: "--d-supply", soft: "--d-supply-soft", tag: "Supply" },
    finance: { color: "--d-finance", soft: "--d-finance-soft", tag: "Finance" },
    bus: { color: "--d-finance", soft: "--tc-card", tag: "Integration" },
    data: { color: "--d-data", soft: "--d-data-soft", tag: "Data" }
  };

  var NODES = [
    { id: "staff", d: "channel", x: 40, y: 44, w: 440, h: 64, name: "Club staff in the browser", sub: "Thymeleaf UIs, one per module, Bright Blue theme",
      text: "Every module has its own web UI with grids, entry forms, status actions and Excel export. The Modules menu moves between them; Keycloak single sign-on means one sign-in.",
      lists: { "What people use": ["Entry forms, grids with filter / sort / paging, Excel export", "Status actions with optimistic locking", "Fee schedule and reference data in every module"] } },
    { id: "bot", d: "bot", port: "8120", x: 520, y: 44, w: 360, h: 64, name: "TurfBot", sub: "Flask + LangGraph agent, read-only",
      text: "Answers questions from live ERP data. Signs users in with PKCE, gives Claude only the lookups of modules the user's roles open, and checks every call again before running it.",
      lists: { "Reads": ["All 14 services' /api/v1 as svc-chatbot (SVC_READ)", "Core audit API for TC_AUDITOR / TC_ADMIN"], "Keeps": ["schema chatbot: questions, answers, every lookup and every API call with tokens and cost (append-only)"] } },
    { id: "claude", d: "ai", x: 920, y: 44, w: 280, h: 64, name: "Anthropic Messages API", sub: "Claude · tool use, streaming, prompt cache", external: true,
      text: "Claude decides which lookups to make and writes the answer. Tool definitions and instructions are cached between calls; usage and cost are recorded per call.",
      lists: { "Sent": ["System prompt and the user's allowed tool definitions", "The question, short history, tool results (cut to 100 rows)"] } },
    { id: "kc", d: "ident", port: "8080", x: 40, y: 156, w: 1160, h: 52, name: "Keycloak 26 · realm turfclub", sub: "PKCE for people · client credentials between services · realm roles <MODULE>_VIEW / _MANAGE, TC_ADMIN, TC_AUDITOR",
      text: "One realm for everything. People sign in through the public client turfclub-web with PKCE; each service has its own svc-<module> client for calls to other services. Roles in the token decide what each screen and each TurfBot lookup allows.",
      lists: { "Clients": ["turfclub-web (PKCE, all UIs and TurfBot)", "svc-<module> ×14 (SVC_READ, SVC_GL_POST)", "svc-chatbot (SVC_READ)"], "Test users": ["tcadmin, auditor, coreadmin, registrar, steward, tote, memberdesk, hospitality, storekeeper, buyer, accountant"] } },
    { id: "core", d: "core", port: "8101", x: 40, y: 256, w: 1160, h: 64, name: "Enterprise Core · portal", sub: "Parties and addresses · legal entities · venues · business calendar · users and roles · audit trail for every schema",
      text: "The shared master data and the portal. An owner, jockey, supplier, member and customer are all one party here. Database triggers record every change in every module with the Keycloak user, and the audit API answers TurfBot's 'who changed…' questions.",
      lists: { "Owns": ["enterprise_core, identity_security, audit_compliance, reference_data"], "Used by": ["Every module (parties, venues, calendar)", "Racing: meetings only on open calendar days", "TurfBot: audit-events and party history API"] } },

    { id: "horse", d: "racing", port: "8103", x: 60, y: 404, w: 250, h: 58, name: "Horse Registry", sub: "pedigree, owners, documents, medical",
      text: "Registers horses with pedigree and ownership shares (must total 100 %), documents with checksums and medical withdrawals.",
      lists: { "Answers": ["Is this horse eligible on a date? (Racing)", "Who owned it on race day? (Racing entry fee, Prizes split)"], "Emits": ["HORSE_REGISTRATION_FEE → GL, AR invoice to the largest owner"] } },
    { id: "part", d: "racing", port: "8104", x: 60, y: 484, w: 250, h: 58, name: "Participants", sub: "licences, trainers, contracts",
      text: "Jockey, trainer, owner and official licences with renewals and expiry, trainer assignments per horse and jockey contracts.",
      lists: { "Answers": ["Valid JOCKEY / OFFICIAL licence on race day? (Racing)", "Current trainer of a horse (Racing)"], "Emits": ["LICENCE_FEE → GL, AR", "JOCKEY_CONTRACT_FEE → GL"] } },
    { id: "racing", d: "racing", port: "8105", x: 60, y: 564, w: 250, h: 58, name: "Race Operations", sub: "meetings, entries, declaration, results",
      text: "Plans meetings on open days, takes entries with live checks, declares fields with the draw, starts races and certifies results that can never change.",
      lists: { "Calls": ["Horse Registry: eligibility, owners", "Participants: licences, trainer"], "Serves": ["Race status and certified results to Wagering and Prizes"], "Emits": ["RACE_ENTRY_FEE, PURSE_COMMITMENT, PURSE_RELEASE"] } },
    { id: "wager", d: "betting", port: "8106", x: 370, y: 404, w: 230, h: 58, name: "Wagering", sub: "pools, tickets, settlement",
      text: "Tote pools per race (WIN to TRIFECTA), idempotent ticket sales on five channels, auto-close at the off, settlement with dividends, breakage, minus pools and refunds.",
      lists: { "Calls": ["Race Operations: start, cancel, certified result"], "Serves": ["Winning tickets to Prizes"], "Emits": ["WAGER_HANDLE, TAKEOUT_REVENUE, DIVIDENDS_DECLARED, BREAKAGE, MINUS_POOL, WAGER_REFUND"] } },
    { id: "prize", d: "betting", port: "8107", portLow: true, x: 370, y: 564, w: 230, h: 58, name: "Prizes & Settlement", sub: "prize money, ticket payouts",
      text: "Prize schedules from the purse, awards calculated from the certified result with owner shares by race-day ownership, and payouts of winning tickets with tax withholding.",
      lists: { "Calls": ["Race Operations: official result", "Horse Registry: ownership on race day", "Wagering: winning tickets, mark paid"], "Emits": ["PRIZE_AWARD, PRIZE_PAYMENT, PRIZE_UNAWARDED, TAX_WITHHELD, TICKET_PAYOUT"] } },
    { id: "member", d: "club", port: "8108", x: 660, y: 404, w: 230, h: 58, name: "Club Membership", sub: "members, dependents, renewals",
      text: "Applications, activation with the first year invoiced, dependents, plan changes, renewals generated and invoiced in bulk, nightly expiry.",
      lists: { "Serves": ["Member standing and guest allowance to Hospitality"], "Emits": ["MEMBERSHIP_FEE, MEMBERSHIP_RECEIPT → GL, AR invoice / settlement"] } },
    { id: "hosp", d: "club", port: "8109", x: 660, y: 564, w: 230, h: 58, name: "Hospitality", sub: "reservations, POS, club events",
      text: "Restaurant reservations with automatic table choice, POS bills paid by cash, card or member account, and club events with capacity and bookings.",
      lists: { "Calls": ["Membership: standing, guest allowance"], "Emits": ["POS_SALE / TAX, POS_MEMBER_CHARGE / TAX, EVENT_BOOKING / CANCEL → GL, AR"] } },
    { id: "inv", d: "supply", port: "8110", x: 950, y: 404, w: 230, h: 58, name: "Inventory Control", sub: "items, stock, movements, reorder",
      text: "Items with lots and stock by location, an immutable movement ledger (no negative stock), and a reorder report. Each category's GL class decides the inventory account.",
      lists: { "Serves": ["Reorder report and the stock receipts API to Purchasing"], "Emits": ["STOCK_ISSUE, STOCK_ADJUSTMENT, STOCK_GAIN, STOCK_RETURN by GL class"] } },
    { id: "proc", d: "supply", port: "8111", x: 950, y: 564, w: 230, h: 58, name: "Purchasing", sub: "requisitions, orders, goods receipts",
      text: "Requisitions (also straight from the reorder report), purchase orders approved by a second user, and goods receipts posted into stock or reversed back to the supplier.",
      lists: { "Calls": ["Inventory: reorder report, book receipts and returns"], "Serves": ["Orders and receipts to AP for the three-way match"], "Emits": ["GOODS_RECEIVED, GOODS_RETURNED by GL class"] } },

    { id: "bus", d: "bus", x: 40, y: 684, w: 1160, h: 46, name: "", sub: "", bus: true,
      text: "Every module writes its accounting events into integration.accounting_event_outbox in the same transaction as the business change. Its relay sends them to the GL with the service's token; the GL applies the posting rule (or the account the event names) and returns the journal.",
      lists: { "Guarantees": ["No money movement without its event (same transaction)", "At most once per source reference", "Retries with back-off while the GL is down"] } },

    { id: "ar", d: "finance", port: "8113", x: 40, y: 790, w: 270, h: 62, name: "Accounts Receivable", sub: "customer invoices, receipts, imports",
      text: "Customer invoices and receipts into the bank, plus every module charge imported from posted events: fees, member charges, event bookings. Module payments settle them; cancellations credit them.",
      lists: { "Reads": ["Posted module events (AR import, every minute)", "GL balances 1200 / 1210 for the sub-ledger check"], "Emits": ["AR_INVOICE_POSTED, AR_INVOICE_TAX, AR_RECEIPT, AR_RECEIPT_REVERSAL"] } },
    { id: "gl", d: "finance", port: "8102", x: 350, y: 790, w: 270, h: 62, name: "General Ledger", sub: "journals, periods, posting rules",
      text: "The books of Rollingstone Turf Club Ltd: chart of accounts, monthly periods, manual journals, and the accounting-event API that turns every module's events into balanced journals.",
      lists: { "Receives": ["Accounting events from all 13 other services"], "Controls": ["Closed periods refuse postings", "Posted journals are immutable - reversal only"] } },
    { id: "treas", d: "finance", port: "8114", x: 660, y: 790, w: 250, h: 62, name: "Treasury", sub: "bank accounts, statements, matching",
      text: "Bank accounts on their GL cash accounts, statement upload, bank charges and interest posted from the statement, and reconciliation of statement lines to GL lines.",
      lists: { "Reads": ["GL lines on the bank account (AP payments, AR receipts, prize and refund payments)"], "Emits": ["BANK_CHARGE, BANK_INTEREST"] } },
    { id: "ap", d: "finance", port: "8112", x: 950, y: 790, w: 250, h: 62, name: "Accounts Payable", sub: "supplier invoices, payments, ageing",
      text: "Supplier invoices from a purchase order with a three-way match, or to expense accounts; approval by a second user; payments out of the bank; ageing against GL 2100.",
      lists: { "Calls": ["Purchasing: order lines and received, not-yet-invoiced value"], "Emits": ["AP_INVOICE_POSTED, AP_INVOICE_EXPENSE, AP_PRICE_VARIANCE, AP_INVOICE_TAX, AP_PAYMENT"] } },

    { id: "db", d: "data", port: "3306", x: 40, y: 900, w: 1160, h: 62, name: "MySQL 8 · one schema per module", sub: "16 domain schemas + integration (outbox) + audit_compliance + reference_data + chatbot · audit, version and guard triggers in the database",
      text: "Each service owns its schema and validates it at start-up. Business rules that must never be broken live in triggers too: shares over 100 %, negative stock, changing a certified result or a posted journal.",
      lists: { "Shared": ["integration.accounting_event_outbox", "audit_compliance.audit_event", "reference_data (domains, fee schedules, settings)"] } }
  ];

  var FRAMES = [
    { d: "racing", x: 46, y: 364, w: 278, h: 272, label: "Racing" },
    { d: "betting", x: 356, y: 364, w: 258, h: 272, label: "Betting & prizes" },
    { d: "club", x: 646, y: 364, w: 258, h: 272, label: "Members & hospitality" },
    { d: "supply", x: 936, y: 364, w: 258, h: 272, label: "Supply" }
  ];
  var BANDS = [[34, "Channels"], [146, "Identity"], [246, "Shared core"], [354, "Operations"], [676, ""], [780, "Finance"], [890, "Data"]];

  // [from, to, type, description, fromSide, toSide, fromAt, toAt, curve]
  // side = top / bottom / left / right; "at" = x (top / bottom) or y (left / right); default = centre
  var EDGES = [
    ["staff", "kc", "auth", "Sign-in with PKCE (turfclub-web)", "bottom", "top", 260, 260],
    ["bot", "kc", "auth", "User PKCE sign-in; svc-chatbot client-credentials token", "bottom", "top", 640, 640],
    ["bot", "claude", "ai", "Messages API: tools, streaming, prompt cache", "right", "left"],
    ["bot", "core", "rest", "Reads every module's /api/v1 as svc-chatbot, limited to the user's modules", "bottom", "top", 820, 820],
    ["core", "horse", "master", "Parties (owners)", "bottom", "top", 185, 185],
    ["core", "wager", "master", "Venues, parties", "bottom", "top", 572, 572],
    ["core", "member", "master", "Parties (members, dependents)", "bottom", "top", 862, 862],
    ["core", "inv", "master", "Venues, parties (suppliers)", "bottom", "top", 1065, 1065],
    ["racing", "horse", "rest", "Eligibility on race day, owners", "left", "left", 600, 440, 34],
    ["racing", "part", "rest", "Licence check, current trainer", "left", "left", 585, 513, 22],
    ["wager", "racing", "rest", "Race start / cancel, certified result", "left", "right", 440, 580],
    ["prize", "racing", "rest", "Official result", "left", "right", 606, 606],
    ["prize", "wager", "rest", "Winning tickets, mark paid", "top", "bottom", 485, 485],
    ["prize", "horse", "rest", "Ownership on race day", "left", "right", 580, 426],
    ["hosp", "member", "rest", "Member standing, guest allowance", "top", "bottom"],
    ["proc", "inv", "rest", "Reorder report, book receipts and returns", "top", "bottom"],
    ["ap", "proc", "rest", "Order lines, received not invoiced", "top", "bottom", 1150, 1150],
    ["racing", "bus", "event", "Racing events", "bottom", "top", 185, 185],
    ["prize", "bus", "event", "Wagering and prize events", "bottom", "top", 485, 485],
    ["hosp", "bus", "event", "Membership and hospitality events", "bottom", "top", 775, 775],
    ["proc", "bus", "event", "Inventory and purchasing events", "bottom", "top", 1000, 1000],
    ["bus", "gl", "event", "Relay posts events; GL returns the journal", "bottom", "top", 485, 485],
    ["bus", "ar", "import", "Posted module charges become customer invoices", "bottom", "top", 175, 175],
    ["ar", "gl", "event", "AR invoices and receipts", "right", "left"],
    ["treas", "gl", "event", "Bank charges, interest; reads bank GL lines", "left", "right"],
    ["ap", "gl", "event", "AP invoices and payments", "bottom", "bottom", 1075, 560, 26]
  ];
  var LABELS = [
    [812, 238, "TurfBot → every module's /api/v1 (svc-chatbot, user's roles only)", "end"],
    [190, 772, "AR import"],
    [493, 772, "posted to the GL"]
  ];
  // extra (hidden-path) relations used for highlighting only
  var ALSO = { horse: ["bus"], part: ["bus"], wager: ["bus"], member: ["bus"], inv: ["bus"] };

  var HREF = {"bot": "/domains/turfbot", "kc": "/security/keycloak-realm", "core": "/domains/core", "horse": "/domains/horse", "part": "/domains/participants", "racing": "/domains/racing", "wager": "/domains/wagering", "prize": "/domains/prizes", "member": "/domains/membership", "hosp": "/domains/hospitality", "inv": "/domains/inventory", "proc": "/domains/purchasing", "bus": "/schemas/integration", "ar": "/domains/ar", "gl": "/domains/gl", "treas": "/domains/treasury", "ap": "/domains/ap", "db": "/schemas/enterprise_core", "staff": "/domains/core"};
  var byId = {};
  NODES.forEach(function (n) { byId[n.id] = n; });

  function el(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function v(name) { return "var(" + name + ")"; }

  // arrow markers per edge type
  var defs = document.getElementById("archDefs");
  ["rest", "event", "import", "auth", "master", "ai"].forEach(function (t) {
    var m = el("marker", { id: "mk-" + t, viewBox: "0 0 10 10", refX: "9", refY: "5", markerWidth: "7", markerHeight: "7", orient: "auto-start-reverse" }, defs);
    el("path", { d: "M0,0 L10,5 L0,10 z", "class": "mk-" + t }, m);
  });

  // band labels and domain frames
  var frames = document.getElementById("archFrames");
  BANDS.forEach(function (b) { if (b[1]) { var t = el("text", { x: 40, y: b[0] - 6, "class": "band-label" }, frames); t.textContent = b[1]; } });
  FRAMES.forEach(function (f) {
    var c = DOMAINS[f.d].color;
    el("rect", { x: f.x, y: f.y, width: f.w, height: f.h, rx: 10, "class": "frame", stroke: v(c), fill: "none" }, frames);
    var t = el("text", { x: f.x + 14, y: f.y + 24, "class": "frame-label", fill: v(c) }, frames);
    t.textContent = f.label;
  });

  function anchor(n, toward) {
    var cx = n.x + n.w / 2, cy = n.y + n.h / 2;
    var dx = toward.x - cx, dy = toward.y - cy;
    if (Math.abs(dy) * (n.w / n.h) * 0.5 > Math.abs(dx) || n.w > 600) {
      // vertical exit; wide bands exit straight above / below the target
      var x = n.w > 600 ? Math.min(Math.max(toward.x, n.x + 30), n.x + n.w - 30) : cx;
      return { x: x, y: dy > 0 ? n.y + n.h : n.y, dir: [0, dy > 0 ? 1 : -1] };
    }
    return { x: dx > 0 ? n.x + n.w : n.x, y: cy, dir: [dx > 0 ? 1 : -1, 0] };
  }
  function center(n) { return { x: n.x + n.w / 2, y: n.y + n.h / 2 }; }

  var edgeG = document.getElementById("archEdges");
  var edgeEls = [];
  function sideAnchor(n, side, at) {
    if (side === "top") return { x: at == null ? n.x + n.w / 2 : at, y: n.y, dir: [0, -1] };
    if (side === "bottom") return { x: at == null ? n.x + n.w / 2 : at, y: n.y + n.h, dir: [0, 1] };
    if (side === "left") return { x: n.x, y: at == null ? n.y + n.h / 2 : at, dir: [-1, 0] };
    return { x: n.x + n.w, y: at == null ? n.y + n.h / 2 : at, dir: [1, 0] };
  }
  EDGES.forEach(function (e) {
    var a = byId[e[0]], b = byId[e[1]];
    var pa = sideAnchor(a, e[4], e[6]), pb = sideAnchor(b, e[5], e[7]);
    var dist = e[8] || Math.max(16, Math.min(60, Math.hypot(pb.x - pa.x, pb.y - pa.y) * 0.4));
    var d = (pa.x === pb.x || pa.y === pb.y) && pa.dir[0] === -pb.dir[0] && pa.dir[1] === -pb.dir[1]
      ? "M" + pa.x + "," + pa.y + " L" + pb.x + "," + pb.y
      : "M" + pa.x + "," + pa.y + " C" + (pa.x + pa.dir[0] * dist) + "," + (pa.y + pa.dir[1] * dist) + " " +
        (pb.x + pb.dir[0] * dist) + "," + (pb.y + pb.dir[1] * dist) + " " + pb.x + "," + pb.y;
    var p = el("path", { d: d, "class": "edge " + e[2], "marker-end": "url(#mk-" + e[2] + ")" }, edgeG);
    var t = el("title", {}, p); t.textContent = (a.name || "Accounting event bus").replace(/ ·.*/, "") + " → " + (b.name || "accounting event bus").replace(/ ·.*/, "") + ": " + e[3];
    edgeEls.push({ el: p, from: e[0], to: e[1], type: e[2], label: e[3] });
  });
  LABELS.forEach(function (l) { var t = el("text", { x: l[0], y: l[1], "class": "edge-label", "text-anchor": l[3] || "start" }, edgeG); t.textContent = l[2]; });

  var nodeG = document.getElementById("archNodes");
  var nodeEls = {};
  NODES.forEach(function (n) {
    var dom = DOMAINS[n.d];
    var g = el("g", { "class": "anode", tabindex: "0", role: "button", "data-id": n.id, "aria-label": (n.name || "Accounting event bus") + (n.port ? ", port " + n.port : "") }, nodeG);
    var r = el("rect", { x: n.x, y: n.y, width: n.w, height: n.h, rx: n.bus ? 23 : 8, "class": "box", fill: v(dom.soft), stroke: v(dom.color) }, g);
    if (n.external) r.setAttribute("stroke-dasharray", "6 4");
    if (n.bus) {
      var t1 = el("text", { x: n.x + n.w / 2, y: n.y + 21, "text-anchor": "middle", "class": "bus-text" }, g);
      t1.textContent = "ACCOUNTING EVENTS · transactional outbox → relay → GL posting rules";
      var t2 = el("text", { x: n.x + n.w / 2, y: n.y + 37, "text-anchor": "middle", "class": "bus-sub" }, g);
      t2.textContent = "integration.accounting_event_outbox · one row per money movement, written in the same transaction";
    } else {
      var nm = el("text", { x: n.x + 14, y: n.y + (n.h > 56 ? 26 : 23), "class": "name" }, g); nm.textContent = n.name;
      var sb = el("text", { x: n.x + 14, y: n.y + (n.h > 56 ? 46 : 42), "class": "sub" }, g); sb.textContent = n.sub;
      if (n.port) {
        var pt = el("text", { x: n.x + n.w - 12, y: n.y + (n.portLow ? (n.h > 56 ? 46 : 42) : (n.h > 56 ? 26 : 23)), "text-anchor": "end", "class": "port", fill: v(dom.color) }, g);
        pt.textContent = ":" + n.port;
      }
    }
    var tt = el("title", {}, g); tt.textContent = n.text;
    nodeEls[n.id] = g;
    g.addEventListener("click", function () { select(n.id); });
    g.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); select(n.id); } });
  });

  var card = document.getElementById("archCard");
  var current = null;
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function codeify(s) { return esc(s).replace(/\b([A-Z][A-Z_]{3,}[A-Z])\b/g, "<code>$1</code>"); }

  function overview() {
    card.innerHTML =
      '<span class="tag" style="background:var(--d-core-soft);color:var(--d-core)">Overview</span>' +
      "<h3>Seven layers, one set of books</h3>" +
      '<div class="port-line">click any box to trace it</div>' +
      "<p>People reach the system through the module UIs or TurfBot. Keycloak signs everyone in. Core holds the parties, venues and calendar every module shares. The operational modules check each other live where a rule needs a current answer, and every money movement leaves through the accounting event bus into the General Ledger, from where AR, AP and Treasury keep the sub-ledgers and the bank in step.</p>" +
      "<h4>Start with</h4><ul><li><b>Race Operations</b>: the busiest set of live checks</li><li><b>Accounting event bus</b>: how every module reaches the books</li><li><b>TurfBot</b>: AI over the whole backbone, within each user's roles</li></ul>";
  }

  function select(id) {
    if (current === id) { clear(); return; }
    current = id;
    var n = byId[id], dom = DOMAINS[n.d];
    var linked = {}; linked[id] = true;
    var rels = [];
    edgeEls.forEach(function (e) {
      var on = e.from === id || e.to === id;
      e.el.classList.toggle("on", on);
      if (on) {
        linked[e.from] = true; linked[e.to] = true;
        var other = byId[e.from === id ? e.to : e.from];
        rels.push((e.from === id ? "→ " : "← ") + "<b>" + esc((other.name || "Accounting event bus").replace(/ ·.*/, "")) + "</b>: " + codeify(e.label));
      }
    });
    (ALSO[id] || []).forEach(function (x) { linked[x] = true; });
    if (id === "bus") Object.keys(ALSO).forEach(function (x) { linked[x] = true; });
    svg.classList.add("focus");
    Object.keys(nodeEls).forEach(function (k) {
      nodeEls[k].classList.toggle("on", !!linked[k]);
      nodeEls[k].classList.toggle("selected", k === id);
    });
    var html = '<span class="tag" style="background:' + v(dom.soft) + ";color:" + v(dom.color) + '">' + esc(dom.tag) + "</span>" +
      "<h3>" + esc(n.name || "Accounting event bus") + "</h3>" +
      '<div class="port-line">' + (n.port ? "port " + esc(n.port) : (n.bus ? "integration schema" : "external service")) + "</div>" +
      "<p>" + esc(n.text) + "</p>";
    Object.keys(n.lists || {}).forEach(function (h) {
      html += "<h4>" + esc(h) + "</h4><ul>" + n.lists[h].map(function (x) { return "<li>" + codeify(x) + "</li>"; }).join("") + "</ul>";
    });
    if (rels.length) html += "<h4>Connections drawn</h4><ul>" + rels.map(function (r) { return "<li>" + r + "</li>"; }).join("") + "</ul>";
    html += '<div class="d-flex flex-wrap gap-2 mt-3">' +
      (HREF[id] ? '<a class="btn btn-sm btn-primary" href="' + HREF[id] + '"><i class="bi bi-arrow-right-circle me-1"></i>Open the page</a>' : "") +
      '<button type="button" class="btn btn-sm btn-outline-primary" id="clearSel">Whole map</button></div>';
    card.innerHTML = html;
    document.getElementById("clearSel").addEventListener("click", clear);
  }

  function clear() {
    current = null;
    svg.classList.remove("focus");
    edgeEls.forEach(function (e) { e.el.classList.remove("on"); });
    Object.keys(nodeEls).forEach(function (k) { nodeEls[k].classList.remove("on", "selected"); });
    overview();
  }

  overview();
})();
