# Site maintenance

This repository contains the public Hugo blog. Keep content in plain Markdown
and preserve existing post URLs when editing content.

Keep the build static and dependency-light. Run `hugo --minify --panicOnWarning`
after changes, and verify post links, RSS, mobile layout and draft exclusion.
Production deployment is manual.

Keep Actions pinned to full commit SHAs and verify downloaded build tools. A
public repository exposes drafts and media even if the site build excludes them.
