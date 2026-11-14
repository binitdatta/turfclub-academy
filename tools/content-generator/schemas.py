"""Hand-written descriptions of the database schemas and their tables."""

SCHEMA_GROUPS = [("shared", "Shared platform"), ("racing", "Racing"), ("betting", "Betting & prizes"),
                 ("club", "Members & hospitality"), ("supply", "Supply"), ("finance", "Finance"), ("ai", "AI assistant")]

SCHEMAS = {
    "enterprise_core": ("shared", 1, "core", "Master data shared by every module: parties, legal entities, venues, employees and the business calendar.", {
        "party": "Every person or organisation the club deals with: owners, jockeys, trainers, suppliers, members, customers.",
        "party_address": "Addresses of a party; exactly one may be primary.",
        "legal_entity": "Companies that keep books (RSTC) with base currency and tax id.",
        "venue": "Racecourses and sites with their time zone.",
        "employee": "Club staff, each a PERSON party.",
        "business_calendar": "One row per venue and day: open, race day, note.",
    }),
    "identity_security": ("shared", 2, "core", "Users as they first signed in through Keycloak, application roles and permissions for Core's security screens.", {
        "app_user": "A Keycloak user recorded at first sign-in, optionally linked to a party.",
        "app_role": "Application roles mirroring the realm roles.",
        "permission": "Fine-grained permissions shown in the role matrix.",
        "role_permission": "The role × permission matrix.",
        "user_role": "Role assignments per user and legal entity.",
    }),
    "audit_compliance": ("shared", 3, "core", "The compliance trail: audit events written by triggers in every schema, security events and business exceptions.", {
        "audit_event": "Insert / update / delete on any audited table with before and after JSON, actor and request id.",
        "security_event": "Sign-ins, sign-outs and failed sign-ins.",
        "business_exception": "Problems a job could not solve, waiting for a person (e.g. failed accounting events).",
    }),
    "reference_data": ("shared", 4, "core", "Shared reference domains and values, and the fee schedule / settings of every module.", {
        "ref_domain": "A list of allowed values (COUNTRY, CURRENCY, TAX_CODE, AR_IMPORT_EVENT ...).",
        "ref_value": "The values of each domain.",
        "fee_schedule": "Fees and numeric settings per module and legal entity (REGISTRATION_FEE, TAKEOUT_WIN, MATCH_TOLERANCE_PCT ...).",
    }),
    "integration": ("shared", 5, "core", "Cross-module plumbing: the transactional outbox of accounting events and document number sequences.", {
        "accounting_event_outbox": "Accounting events written with the business change, relayed to the GL (PENDING → SENT → POSTED / FAILED).",
        "document_sequence": "Next number per entity, prefix and year (APP-2026-000001 ...).",
    }),
    "horse_registry": ("racing", 1, "horse", "Horses, their effective-dated ownership, documents and medical records.", {
        "horse": "Registration number, name, sex, colour, foaling date, sire, dam, status.",
        "horse_ownership": "Owner party and percentage share with validity dates.",
        "horse_document": "Uploaded passports and certificates with SHA-256 and expiry.",
        "horse_medical_record": "Treatments and examinations, optionally withdrawing the horse until a date.",
    }),
    "racing_participants": ("racing", 2, "participants", "Licences of jockeys, trainers, owners and officials, trainer assignments and jockey contracts.", {
        "participant_license": "A licence: holder, type, number, authority, validity, status.",
        "horse_trainer_assignment": "Which trainer has a horse between two dates.",
        "jockey_contract": "Retainer contracts between a jockey and a legal entity.",
    }),
    "racing_operations": ("racing", 3, "racing", "Race meetings, races, entries, officials and certified results.", {
        "race_meeting": "A race day at a venue.",
        "race": "One race of a meeting with conditions, purse and status.",
        "race_entry": "A horse in a race with jockey, trainer, weight, saddlecloth and draw.",
        "race_official": "Stewards, judges and other officials of a race.",
        "race_result": "Finishing position and time per entry; immutable once official.",
    }),
    "wagering": ("betting", 1, "wagering", "Tote pools, tickets with selections, settlements and declared dividends.", {
        "betting_pool": "One pool per race and bet type with takeout and status.",
        "wager_ticket": "A sold ticket: pool, stake, channel, status.",
        "ticket_selection": "The runners selected on a ticket, by leg / position.",
        "pool_settlement": "Gross, takeout, net and breakage of a settled pool.",
        "winning_dividend": "Dividend per winning combination.",
    }),
    "prizes_settlement": ("betting", 2, "prizes", "Prize schedules, prize awards per payee and payouts of winning tickets.", {
        "prize_schedule": "Prize amount per finishing position of a race.",
        "prize_award": "One award line per payee (owner, trainer, jockey).",
        "ticket_payout": "Payout of a winning ticket with tax withheld.",
    }),
    "membership": ("club", 1, "membership", "Membership plans, members, dependents and renewals.", {
        "membership_plan": "FULL, SOCIAL, JUNIOR with annual fee and guest allowance.",
        "club_member": "A member: party, number, plan, dates, status.",
        "member_dependent": "A dependent party with access dates.",
        "membership_renewal": "One membership year: DUE, INVOICED, PAID or WAIVED.",
    }),
    "hospitality": ("club", 2, "hospitality", "Outlets, tables, menus, reservations, POS orders and club events.", {
        "outlet": "Restaurants, bars and function rooms.",
        "dining_table": "Tables of an outlet with seats and service flag.",
        "menu_item": "Priced items of an outlet with tax code.",
        "reservation": "A table booking with party size, member and status.",
        "pos_order": "A bill with tender and status.",
        "pos_order_line": "Items on a bill with quantity, price and tax.",
        "club_event": "Ticketed club events with capacity and price.",
        "event_booking": "Places booked for an event by a member.",
    }),
    "inventory": ("supply", 1, "inventory", "Items, categories with GL classes, locations, lots and the movement ledger.", {
        "item_category": "Categories with the GL class that picks inventory and expense accounts.",
        "inventory_item": "Stock items with unit, standard cost and reorder point.",
        "stock_location": "Barns, kitchen, cellar and stores.",
        "stock_lot": "Received batches with remaining quantity and cost.",
        "stock_movement": "The append-only ledger of every quantity change.",
    }),
    "procurement": ("supply", 2, "purchasing", "Suppliers, requisitions, purchase orders and goods receipts.", {
        "supplier": "A party as supplier with terms, tax id and status.",
        "purchase_requisition": "An internal request to buy.",
        "purchase_requisition_line": "Requested items and quantities.",
        "purchase_order": "An order to a supplier with approval and status.",
        "purchase_order_line": "Ordered, received and invoiced quantities per item.",
        "goods_receipt": "A delivery received into a location.",
        "goods_receipt_line": "Received, accepted and rejected quantities per order line.",
    }),
    "financial_gl": ("finance", 1, "gl", "Chart of accounts, fiscal periods, journals and posting rules.", {
        "gl_account": "Accounts of a legal entity: header or posting, type, parent.",
        "fiscal_period": "Monthly periods with OPEN / SOFT_CLOSED / CLOSED status.",
        "journal": "A journal header: date, source module and reference, status.",
        "journal_line": "Debit or credit lines of a journal.",
        "posting_rule": "Debit and credit accounts per module and event code.",
    }),
    "financial_ap": ("finance", 2, "ap", "Supplier invoices, their lines and payments.", {
        "ap_invoice": "A supplier invoice with match, approval and balance.",
        "ap_invoice_line": "Lines with item / PO line or expense account, amount and tax.",
        "ap_payment": "Payments from a bank account, scheduled or executed.",
    }),
    "financial_ar": ("finance", 3, "ar", "Customer invoices, receipts and the import log of module receivables.", {
        "ar_invoice": "A customer invoice, own or imported from a module event.",
        "ar_invoice_line": "Revenue lines with account and tax.",
        "ar_receipt": "Money received, cheques pending until cleared.",
        "ar_import": "One row per imported outbox event with its result.",
    }),
    "treasury": ("finance", 4, "treasury", "Bank accounts, statement lines and reconciliations.", {
        "bank_account": "A bank account linked to its GL cash account.",
        "bank_transaction": "An imported statement line.",
        "bank_reconciliation": "A reconciliation to a statement date and closing balance.",
        "bank_reconciliation_line": "A statement line matched to a GL line.",
    }),
    "chatbot": ("ai", 1, "turfbot", "TurfBot's AI audit trail: conversations, messages, tool calls and LLM usage.", {
        "conversation": "One chat thread per user; archived, never deleted.",
        "message": "Every question and answer with stop reason, error and latency.",
        "tool_call": "Every lookup the model asked for: arguments, status, rows and full result.",
        "llm_usage": "One row per Messages API call: tokens, cache reads / writes, cost.",
    }),
}
