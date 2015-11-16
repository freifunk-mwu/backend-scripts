#!/bin/bash

CDIR=$(cd "$(dirname "$0")"; pwd)

sphinx-apidoc \
    --doc-project="Modules" \
    --force \
    --output-dir "$CDIR/scripts" \
    --private \
    --module-first \
    --separate \
    "$CDIR/.."
