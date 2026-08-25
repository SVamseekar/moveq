# moveq website

Static HTML for https://moveq.souravamseekar.com.

The Vercel GitHub integration on project `moveq-website` deploys this
directory (framework Other, no install/build). Pushes to `main` update
production; pull requests get preview URLs. Commits that do not touch
`website/` skip the site build.

GitHub Actions job **Website** (`python scripts/check_website.py`) checks
clean-URL routes, internal links, and that `package.json` has no Node
build. Locally:

```bash
python scripts/check_website.py
python website/dev_server.py 8080
```
