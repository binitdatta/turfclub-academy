#!/usr/bin/env python3
"""Writes TurfBot's tool registry to build/tools.json. Run it with the chatbot's own Python (chatbot/.venv/bin/python).

usage: export_tools.py <erp-root>"""
import json
import os
import sys

erp = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(erp, "chatbot"))
from turfbot.agent.tools import REGISTRY  # noqa: E402

here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(here, "build"), exist_ok=True)
rows = [{"name": t.name, "module": t.module, "description": t.description, "audit": t.roles is not None,
         "args": list(t.properties)} for t in REGISTRY.values()]
with open(os.path.join(here, "build", "tools.json"), "w") as f:
    json.dump(rows, f, indent=1)
print(f"{len(rows)} TurfBot tools")
