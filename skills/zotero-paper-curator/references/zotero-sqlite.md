# Zotero SQLite Notes

Use these notes only for local direct SQLite curation when no writable Zotero API is available.

## Core Tables

- `items`: one row per item, note, or attachment. Use `itemTypes.typeName` values such as `preprint`, `note`, and `attachment`.
- `itemData` + `itemDataValues`: field values. Use `fieldsCombined` for field IDs.
- `creators` + `itemCreators`: author rows and item-author ordering. `creatorTypes.creatorType='author'` is the usual creator type for papers.
- `collections` + `collectionItems`: collection tree and item membership. Do not add child notes or child attachments to collections.
- `tags` + `itemTags`: tag vocabulary and item tag assignment. `itemTags.type=0` for manual tags.
- `itemNotes`: child notes. `parentItemID` links to the parent paper.
- `itemAttachments`: child attachments. Stored PDFs generally use `linkMode=0`, `contentType='application/pdf'`, and `path='storage:<filename>.pdf'`.

## Common Preprint Fields

- `title`
- `abstractNote`
- `date`
- `DOI`
- `url`
- `repository`
- `archiveID`
- `language`
- `libraryCatalog`
- `extra`

For arXiv preprints, use:

- `itemType`: `preprint`
- `repository`: `arXiv`
- `archiveID`: `arXiv:<id>`
- `libraryCatalog`: `arXiv.org`
- `DOI`: `10.48550/arXiv.<id>` when appropriate
- `extra`: include the arXiv category and compact TLDR when useful

## Local Safety Checks

- Use `sqlite3 -readonly <db> "PRAGMA quick_check;"` before analysis.
- Use `lsof <db> <db>-journal` or a short `BEGIN IMMEDIATE` check before writes.
- Back up `<db>` and `<db>-journal` before writes.
- Validate inserted rows by querying item title, creators, collection path, child note, attachment, and tags.
