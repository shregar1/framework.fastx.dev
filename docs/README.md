# Documentation (`docs/`)

## What this module does

The **`docs`** directory is the **authoritative source** for MkDocs: user guides, API reference pages, ecosystem notes, and assets (stylesheets, images, JavaScript) used when you build the site with **`mkdocs build`** or **`mkdocs serve`**.

The **published site** (navigation, titles, plugins) is configured in **`mkdocs.yml`** at the repo root. This folder is **not** the same as the auto-generated OpenAPI/Swagger UI served by FastAPI at runtime—those live under the app’s `/docs` URL when enabled.

## Layout (conceptual)

```
docs/
├── index.md                 # Site home
├── guide/                   # Tutorials: installation, Docker, testing, …
├── api/                     # Markdown API reference (non-OpenAPI)
├── ecosystem/               # Related packages (FastCLI, FastDataI, …)
├── reference/               # Reference index and snippets
├── stylesheets/             # Extra CSS for MkDocs
├── javascripts/             # Extra JS (e.g. Swagger embed)
└── CHANGELOG*.md            # Changelog pages linked from nav
```

## How to work with it

1. **Edit** Markdown under `docs/`; **nav** is updated in `mkdocs.yml`.  
2. **Build locally**: `mkdocs serve` (after `pip install -r requirements.txt` or `make docs-install`).  
3. **Link** to code with `mkdocstrings` where configured in `mkdocs.yml`.  

## Related files

- **`mkdocs.yml`** — theme, nav, plugins  
- **`requirements.txt`** — MkDocs section includes Material and related doc build tools (see file comments).  

## Practices

1. Keep **paths** in docs aligned with real modules (`_maint`, `controllers`, …).  
2. For **critical** operational folders, link to the dedicated guide (e.g. `guide/maint-folder.md`).  
3. Prefer **relative** links between Markdown files.
