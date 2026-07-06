---
name: zotero-paper-curator
description: Add or update machine learning papers in the user's local Zotero library, choose suitable existing collections, attach a PDF, add a Chinese paper summary as a Zotero child note, and apply high-quality tags. Use when the user asks to add a summarized paper, arXiv/PDF paper, or paper reading note to Zotero; classify a paper in Zotero; or reuse/create Zotero tags based on paper semantics.
---

# Zotero Paper Curator

## Overview

Use this skill to curate a paper into the user's Zotero library after reading or summarizing it. Prefer official Zotero APIs if writable tools are available; otherwise use the bundled SQLite helper only when Zotero is closed or the database can be locked safely.

## Workflow

1. Locate the Zotero data directory.
   - Prefer `extensions.zotero.dataDir` in the Zotero profile `prefs.js`.
   - Typical local database: `<dataDir>/zotero.sqlite`.
   - Typical attachment storage: `<dataDir>/storage`.

2. Inspect the existing library before deciding.
   - Use `scripts/zotero_paper_curator.py inspect --db <copy-or-db> --collections --root-collection-id <id>` for collection branches.
   - Use `scripts/zotero_paper_curator.py inspect --db <copy-or-db> --tags --limit 200` for tag vocabulary.
   - Search for duplicate title, DOI, arXiv ID, and close semantic neighbors.

3. Choose collections conservatively.
   - Prefer the most specific existing collection that matches the paper's main contribution.
   - Use multiple collections only when the paper genuinely spans independent library branches.
   - Do not use legacy/unreviewed folders unless the library clearly has no curated destination.

4. Choose tags with reuse first.
   - Always include the default manual tag `unread` for newly curated papers unless the user explicitly says not to.
   - Reuse an existing tag when it is semantically equivalent, even if capitalization or wording differs.
   - Reuse exact existing forms for common tags, for example `LLM`, `scaling law`, `multi-task`.
   - Create a new tag only when no existing tag captures the concept.
   - Keep tags focused: include broad domain, core mechanism, task/data setting, and named model/system only when important.

5. Add the item, note, tags, collection membership, and PDF.
   - Store the paper as `preprint` for arXiv unless metadata indicates a venue item type.
   - Add child note HTML using Zotero note wrapper: `<div class="zotero-note znv1"><div data-schema-version="9">...`.
   - Attach the PDF as a stored child attachment when available.
   - Always back up the database before direct SQLite writes.

6. Validate.
   - Run `PRAGMA quick_check` after writing.
   - Query the inserted item, note, attachment, collections, and tags.
   - Report the chosen collection path, reused tags, newly created tags, and backup path.

## Bundled Script

Use `scripts/zotero_paper_curator.py`.

Inspect:

```bash
python3 scripts/zotero_paper_curator.py inspect \
  --db /path/to/zotero.sqlite \
  --collections --root-collection-id 146
```

Add:

```bash
python3 scripts/zotero_paper_curator.py add \
  --db /path/to/zotero.sqlite \
  --data-dir /path/to/zotero-data-dir \
  --metadata paper.json \
  --collection-id 405 \
  --tag LLM \
  --tag "scaling law" \
  --note-file summary.md \
  --pdf paper.pdf \
  --backup-dir /path/to/backups
```

The add command:

- refuses likely duplicates unless `--allow-duplicate` is passed;
- backs up the SQLite database before writing;
- reuses case-insensitive exact tags automatically;
- creates missing requested tags;
- creates a stored PDF child attachment under Zotero `storage/`;
- creates a child note from HTML or Markdown-ish text.

## Safety Rules

- Do not write to a locked database.
- Do not modify live Zotero data without a backup path in the script output.
- Do not delete, move, or rename existing collections/tags during paper insertion.
- If direct SQLite write fails, stop and explain the partial state; do not retry destructive operations.
- If a Zotero write-capable MCP/Web API becomes available, prefer it over direct SQLite.

## Reference

Read `references/zotero-sqlite.md` when using or modifying direct SQLite write behavior.
