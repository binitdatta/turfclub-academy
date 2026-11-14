#!/usr/bin/env bash
# Regenerates src/main/resources/content/** from the ERP's code, its database and the test READMEs.
#   bash tools/content-generator/generate.sh [erp-root] [testing-readmes-root]
# Defaults: ../turfclub-erp and ../turfclub-testing next to this project. Needs python3, the mysql client and the
# chatbot's virtualenv (chatbot/.venv). Run "database/install-db.sh --reset" first so row counts are the seed data.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PROJECT="$(cd "$HERE/../.." && pwd)"
ERP="$(cd "${1:-$PROJECT/../turfclub-erp}" && pwd)"
TESTS="${2:-$PROJECT/../turfclub-testing}"
[[ -d "$TESTS" ]] || TESTS="-"

echo "ERP:   $ERP"
echo "Tests: $TESTS"
python3 "$HERE/extract.py" "$ERP"
"$ERP/chatbot/.venv/bin/python" "$HERE/export_tools.py" "$ERP"
rm -rf "$PROJECT/src/main/resources/content"
python3 "$HERE/build.py" "$ERP" "$TESTS" "$PROJECT/src/main/resources/content"
echo "Content regenerated - restart the Academy to see it."
