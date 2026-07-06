#!/usr/bin/env python3
"""Small Zotero SQLite helper for paper curation.

This script intentionally uses a narrow subset of Zotero's schema. Prefer the
official Zotero Web API when an API key is available. Use SQLite writes only
when Zotero is closed and a backup has been made.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import random
import shutil
import sqlite3
import string
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ZOTERO_KEY_CHARS = "23456789ABCDEFGHIJKLMNPQRSTUVWXYZ"
DEFAULT_TAGS = ("unread",)


FIELD_NAMES = {
    "title",
    "abstractNote",
    "genre",
    "repository",
    "archiveID",
    "place",
    "date",
    "DOI",
    "url",
    "accessDate",
    "archive",
    "archiveLocation",
    "shortTitle",
    "language",
    "libraryCatalog",
    "extra",
}


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def random_key(conn: sqlite3.Connection, table: str, library_id: int = 1) -> str:
    while True:
        key = "".join(random.choice(ZOTERO_KEY_CHARS) for _ in range(8))
        if table in {"items", "collections"}:
            row = conn.execute(
                f"SELECT 1 FROM {table} WHERE libraryID=? AND key=?", (library_id, key)
            ).fetchone()
        else:
            row = None
        if not row:
            return key


def one(conn: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> Any:
    row = conn.execute(query, params).fetchone()
    return None if row is None else row[0]


def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return bool(
        conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
        ).fetchone()
    )


def quick_check(conn: sqlite3.Connection) -> None:
    result = one(conn, "PRAGMA quick_check")
    if result != "ok":
        raise RuntimeError(f"SQLite quick_check failed: {result}")


def backup_database(db_path: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = backup_dir / f"{db_path.name}.codex-backup-{stamp}"
    shutil.copy2(db_path, backup_path)
    journal = Path(str(db_path) + "-journal")
    if journal.exists():
        shutil.copy2(journal, backup_dir / f"{journal.name}.codex-backup-{stamp}")
    return backup_path


def check_unlocked_for_write(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path), timeout=2)
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("ROLLBACK")
    finally:
        conn.close()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_field_ids(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute(
        "SELECT fieldID, fieldName FROM fieldsCombined WHERE fieldName IN (%s)"
        % ",".join("?" for _ in FIELD_NAMES),
        tuple(FIELD_NAMES),
    ).fetchall()
    return {name: field_id for field_id, name in rows}


def get_value_id(conn: sqlite3.Connection, value: str) -> int:
    conn.execute("INSERT OR IGNORE INTO itemDataValues(value) VALUES (?)", (value,))
    value_id = one(conn, "SELECT valueID FROM itemDataValues WHERE value=?", (value,))
    if value_id is None:
        raise RuntimeError("Failed to insert itemDataValues row")
    return int(value_id)


def set_item_field(
    conn: sqlite3.Connection, item_id: int, field_ids: dict[str, int], name: str, value: str | None
) -> None:
    if value is None:
        return
    value = str(value).strip()
    if not value:
        return
    field_id = field_ids.get(name)
    if field_id is None:
        raise RuntimeError(f"Zotero field not found: {name}")
    value_id = get_value_id(conn, value)
    conn.execute(
        "INSERT OR REPLACE INTO itemData(itemID, fieldID, valueID) VALUES (?, ?, ?)",
        (item_id, field_id, value_id),
    )


def normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def find_duplicates(conn: sqlite3.Connection, title: str, doi: str | None, archive_id: str | None) -> list[dict[str, Any]]:
    title_norm = normalized(title)
    matches: list[dict[str, Any]] = []
    rows = conn.execute(
        """
        SELECT i.itemID, i.key, it.typeName, v.value AS title
        FROM items i
        JOIN itemTypes it ON it.itemTypeID=i.itemTypeID
        JOIN itemData d ON d.itemID=i.itemID
        JOIN fieldsCombined f ON f.fieldID=d.fieldID AND f.fieldName='title'
        JOIN itemDataValues v ON v.valueID=d.valueID
        WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
        """
    ).fetchall()
    for item_id, key, type_name, existing_title in rows:
        if normalized(existing_title) == title_norm:
            matches.append(
                {"itemID": item_id, "key": key, "typeName": type_name, "title": existing_title, "reason": "title"}
            )

    for field_name, value in (("DOI", doi), ("archiveID", archive_id)):
        if not value:
            continue
        row_matches = conn.execute(
            """
            SELECT i.itemID, i.key, it.typeName, tv.value
            FROM items i
            JOIN itemTypes it ON it.itemTypeID=i.itemTypeID
            JOIN itemData d ON d.itemID=i.itemID
            JOIN fieldsCombined f ON f.fieldID=d.fieldID AND f.fieldName=?
            JOIN itemDataValues tv ON tv.valueID=d.valueID
            WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
              AND lower(tv.value)=lower(?)
            """,
            (field_name, value),
        ).fetchall()
        for item_id, key, type_name, existing_value in row_matches:
            matches.append(
                {
                    "itemID": item_id,
                    "key": key,
                    "typeName": type_name,
                    "value": existing_value,
                    "reason": field_name,
                }
            )
    seen = set()
    unique = []
    for match in matches:
        sig = (match["itemID"], match["reason"])
        if sig not in seen:
            seen.add(sig)
            unique.append(match)
    return unique


def get_or_create_creator(conn: sqlite3.Connection, first: str, last: str, field_mode: int = 0) -> int:
    conn.execute(
        "INSERT OR IGNORE INTO creators(firstName, lastName, fieldMode) VALUES (?, ?, ?)",
        (first, last, field_mode),
    )
    creator_id = one(
        conn,
        "SELECT creatorID FROM creators WHERE firstName=? AND lastName=? AND fieldMode=?",
        (first, last, field_mode),
    )
    if creator_id is None:
        raise RuntimeError(f"Failed to create creator {first} {last}")
    return int(creator_id)


def get_or_create_tag(conn: sqlite3.Connection, tag: str) -> tuple[int, str, bool]:
    tag_clean = tag.strip()
    if not tag_clean:
        raise ValueError("Blank tag")
    row = conn.execute("SELECT tagID, name FROM tags WHERE lower(name)=lower(?)", (tag_clean,)).fetchone()
    if row:
        return int(row[0]), str(row[1]), False
    conn.execute("INSERT INTO tags(name) VALUES (?)", (tag_clean,))
    return int(conn.execute("SELECT last_insert_rowid()").fetchone()[0]), tag_clean, True


def merge_default_tags(tags: list[str]) -> list[str]:
    merged = [tag for tag in tags if tag.strip()]
    seen = {tag.strip().casefold() for tag in merged}
    for tag in DEFAULT_TAGS:
        if tag.casefold() not in seen:
            merged.append(tag)
    return merged


def copy_pdf_to_storage(pdf_path: Path, storage_dir: Path, attachment_key: str, title: str) -> tuple[str, int, str]:
    safe_title = "".join(ch if ch not in '/\\:*?"<>|' else " " for ch in title)
    safe_title = " ".join(safe_title.split())[:180] or "paper"
    filename = f"{safe_title}.pdf"
    target_dir = storage_dir / attachment_key
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename
    shutil.copy2(pdf_path, target_path)
    digest = hashlib.md5(target_path.read_bytes()).hexdigest()
    mod_ms = int(target_path.stat().st_mtime * 1000)
    return f"storage:{filename}", mod_ms, digest


def markdownish_to_note_html(text: str) -> str:
    """Fallback converter for plain/Markdown-ish summaries."""
    lines = text.splitlines()
    out: list[str] = ['<div class="zotero-note znv1"><div data-schema-version="9">']
    in_ul = False
    for raw in lines:
        line = raw.rstrip()
        if not line:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            continue
        if line.startswith("### "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h2>{html.escape(line[4:].strip())}</h2>")
        elif line.startswith("#### "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h3>{html.escape(line[5:].strip())}</h3>")
        elif line.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{html.escape(line[2:].strip())}</li>")
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<p>{html.escape(line)}</p>")
    if in_ul:
        out.append("</ul>")
    out.append("</div></div>")
    return "\n".join(out)


def cmd_inspect(args: argparse.Namespace) -> int:
    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        quick_check(conn)
        if args.collections:
            root_clause = ""
            params: tuple[Any, ...] = ()
            if args.root_collection_id:
                root_clause = "WHERE collectionID=?"
                params = (args.root_collection_id,)
            rows = conn.execute(
                f"""
                WITH RECURSIVE tree(collectionID, path, depth) AS (
                  SELECT collectionID, collectionName, 0 FROM collections {root_clause}
                  UNION ALL
                  SELECT c.collectionID, tree.path || ' / ' || c.collectionName, tree.depth+1
                  FROM collections c JOIN tree ON c.parentCollectionID=tree.collectionID
                )
                SELECT t.collectionID, t.path, COUNT(ci.itemID) AS directItems
                FROM tree t LEFT JOIN collectionItems ci ON ci.collectionID=t.collectionID
                GROUP BY t.collectionID, t.path
                ORDER BY t.path
                """,
                params,
            ).fetchall()
            print(json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2))
        if args.tags:
            rows = conn.execute(
                """
                SELECT t.tagID, t.name, COUNT(it.itemID) AS itemCount
                FROM tags t LEFT JOIN itemTags it ON it.tagID=t.tagID
                GROUP BY t.tagID, t.name
                ORDER BY itemCount DESC, t.name
                LIMIT ?
                """,
                (args.limit,),
            ).fetchall()
            print(json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2))
    finally:
        conn.close()
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    db_path = Path(args.db).expanduser().resolve()
    data_dir = Path(args.data_dir).expanduser().resolve()
    storage_dir = data_dir / "storage"
    metadata = load_json(Path(args.metadata))
    title = metadata["title"].strip()
    archive_id = metadata.get("archiveID") or metadata.get("archive_id")
    doi = metadata.get("DOI") or metadata.get("doi")

    check_unlocked_for_write(db_path)
    backup_path = backup_database(db_path, Path(args.backup_dir).expanduser().resolve())
    conn = sqlite3.connect(str(db_path), timeout=10)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        quick_check(conn)
        duplicates = find_duplicates(conn, title, doi, archive_id)
        if duplicates and not args.allow_duplicate:
            raise RuntimeError("Potential duplicate found: " + json.dumps(duplicates, ensure_ascii=False))

        conn.execute("BEGIN IMMEDIATE")
        now = utc_timestamp()
        library_id = int(metadata.get("libraryID", 1))
        item_type = metadata.get("itemType", "preprint")
        item_type_id = one(conn, "SELECT itemTypeID FROM itemTypes WHERE typeName=?", (item_type,))
        if item_type_id is None:
            raise RuntimeError(f"Unknown Zotero item type: {item_type}")
        parent_key = random_key(conn, "items", library_id)
        conn.execute(
            """
            INSERT INTO items(itemTypeID, dateAdded, dateModified, clientDateModified, libraryID, key, version, synced)
            VALUES (?, ?, ?, ?, ?, ?, 0, 0)
            """,
            (item_type_id, now, now, now, library_id, parent_key),
        )
        parent_item_id = int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])
        field_ids = get_field_ids(conn)
        field_values = {
            "title": title,
            "abstractNote": metadata.get("abstractNote") or metadata.get("abstract"),
            "genre": metadata.get("genre"),
            "repository": metadata.get("repository"),
            "archiveID": archive_id,
            "date": metadata.get("date"),
            "DOI": doi,
            "url": metadata.get("url"),
            "accessDate": metadata.get("accessDate"),
            "language": metadata.get("language", "en"),
            "libraryCatalog": metadata.get("libraryCatalog"),
            "extra": metadata.get("extra"),
        }
        for name, value in field_values.items():
            set_item_field(conn, parent_item_id, field_ids, name, value)

        author_type_id = int(one(conn, "SELECT creatorTypeID FROM creatorTypes WHERE creatorType='author'"))
        for idx, author in enumerate(metadata.get("authors", [])):
            creator_id = get_or_create_creator(
                conn,
                author.get("firstName", ""),
                author.get("lastName", ""),
                int(author.get("fieldMode", 0)),
            )
            conn.execute(
                """
                INSERT INTO itemCreators(itemID, creatorID, creatorTypeID, orderIndex)
                VALUES (?, ?, ?, ?)
                """,
                (parent_item_id, creator_id, author_type_id, idx),
            )

        collection_ids = [int(x) for x in args.collection_id]
        for collection_id in collection_ids:
            next_order = one(
                conn, "SELECT COALESCE(MAX(orderIndex)+1, 0) FROM collectionItems WHERE collectionID=?", (collection_id,)
            )
            conn.execute(
                "INSERT INTO collectionItems(collectionID, itemID, orderIndex) VALUES (?, ?, ?)",
                (collection_id, parent_item_id, int(next_order)),
            )

        tag_report = []
        for tag in merge_default_tags(args.tag):
            tag_id, tag_name, created = get_or_create_tag(conn, tag)
            conn.execute(
                "INSERT OR IGNORE INTO itemTags(itemID, tagID, type) VALUES (?, ?, 0)",
                (parent_item_id, tag_id),
            )
            tag_report.append({"tagID": tag_id, "name": tag_name, "created": created})

        if args.note_file:
            note_text = Path(args.note_file).read_text(encoding="utf-8")
            note_html = note_text if "zotero-note" in note_text else markdownish_to_note_html(note_text)
            note_title = args.note_title or "论文精读笔记"
            note_key = random_key(conn, "items", library_id)
            note_type_id = int(one(conn, "SELECT itemTypeID FROM itemTypes WHERE typeName='note'"))
            conn.execute(
                """
                INSERT INTO items(itemTypeID, dateAdded, dateModified, clientDateModified, libraryID, key, version, synced)
                VALUES (?, ?, ?, ?, ?, ?, 0, 0)
                """,
                (note_type_id, now, now, now, library_id, note_key),
            )
            note_item_id = int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])
            conn.execute(
                "INSERT INTO itemNotes(itemID, parentItemID, note, title) VALUES (?, ?, ?, ?)",
                (note_item_id, parent_item_id, note_html, note_title),
            )
        else:
            note_item_id = None
            note_key = None

        if args.pdf:
            pdf_path = Path(args.pdf).expanduser().resolve()
            attach_key = random_key(conn, "items", library_id)
            attach_type_id = int(one(conn, "SELECT itemTypeID FROM itemTypes WHERE typeName='attachment'"))
            conn.execute(
                """
                INSERT INTO items(itemTypeID, dateAdded, dateModified, clientDateModified, libraryID, key, version, synced)
                VALUES (?, ?, ?, ?, ?, ?, 0, 0)
                """,
                (attach_type_id, now, now, now, library_id, attach_key),
            )
            attach_item_id = int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])
            path, mod_ms, md5 = copy_pdf_to_storage(pdf_path, storage_dir, attach_key, title)
            conn.execute(
                """
                INSERT INTO itemAttachments(
                    itemID, parentItemID, linkMode, contentType, charsetID, path, syncState,
                    storageModTime, storageHash, lastProcessedModificationTime, lastRead
                ) VALUES (?, ?, 0, 'application/pdf', NULL, ?, 2, ?, ?, NULL, NULL)
                """,
                (attach_item_id, parent_item_id, path, mod_ms, md5),
            )
            set_item_field(conn, attach_item_id, field_ids, "title", "PDF")
        else:
            attach_item_id = None
            attach_key = None

        conn.commit()
        quick_check(conn)
        result = {
            "backup": str(backup_path),
            "itemID": parent_item_id,
            "itemKey": parent_key,
            "noteItemID": note_item_id,
            "noteKey": note_key,
            "attachmentItemID": attach_item_id,
            "attachmentKey": attach_key,
            "collections": collection_ids,
            "tags": tag_report,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect", help="Inspect collections and tags")
    inspect.add_argument("--db", required=True)
    inspect.add_argument("--collections", action="store_true")
    inspect.add_argument("--root-collection-id", type=int)
    inspect.add_argument("--tags", action="store_true")
    inspect.add_argument("--limit", type=int, default=200)
    inspect.set_defaults(func=cmd_inspect)

    add = sub.add_parser("add", help="Add a paper, child note, tags, collections, and optional PDF")
    add.add_argument("--db", required=True)
    add.add_argument("--data-dir", required=True)
    add.add_argument("--metadata", required=True)
    add.add_argument("--collection-id", action="append", required=True)
    add.add_argument("--tag", action="append", default=[])
    add.add_argument("--note-file")
    add.add_argument("--note-title")
    add.add_argument("--pdf")
    add.add_argument("--backup-dir", default=".")
    add.add_argument("--allow-duplicate", action="store_true")
    add.set_defaults(func=cmd_add)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
