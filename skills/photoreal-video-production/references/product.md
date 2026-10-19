# Photoreal product sheet

Use `video-production/references/sheets/product-sheet.md` as written: it is photoreal by default. What to add for a photoreal video:

- The sheet is made from the client's real product photos (`make.py sheet ... --ref`), never generated from a description.
- Every still prompt that shows the product quotes the label text exactly and passes the sheet with a `use_for` naming what it gives (the label, the softgel's look) and what to ignore (the sheet's grey backdrop, its layout).
