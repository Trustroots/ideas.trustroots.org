# Trustroots Ideas

A Hugo blog for https://ideas.trustroots.org/. Content is Markdown; the public
website is static HTML and CSS. No third-party theme, JavaScript framework,
database, tracking or remote fonts are required.

## Local development

Install Hugo **0.167.0** from https://github.com/gohugoio/hugo/releases/tag/v0.167.0.
The standard edition is sufficient; Node.js, Ruby and Go are not needed.

```sh
hugo server --bind 127.0.0.1 --buildDrafts
```

Open http://localhost:1313/. A production build is `hugo --minify --panicOnWarning`.
Generated `public/` files are not committed.

## Write a post

```sh
hugo new content posts/my-post.md
```

Edit the Markdown, date, title and optional description, author, slug and tags.
Put images in `static/images/` and link to `/images/example.jpg`. Set `draft: false`
when ready. Default post URLs are `/year/month/day/slug/`; individual posts can use
an explicit `url` to preserve their original path.

The `.pages.yml` configuration also supports the browser editor at
https://app.pagescms.org/. A repository administrator must grant its GitHub App
access to **this repository only** before it can be used. The configuration has
not yet been tested with an authenticated Pages CMS session.

**This is a public repository. Drafts, future posts and uploaded media committed
here are public, even when Hugo excludes them from the website.** Keep confidential
drafts outside the repository. Future-dated posts require a build after their
publication date; there is no scheduled build configured.

## Build and deploy

Every push to `main` builds, tests and publishes to GitHub Pages. Pull requests
build and test without publishing. Repository Settings → Pages must use
**GitHub Actions**. Manual runs can also publish when `deploy` is enabled.

The workflow reads the canonical URL directly from GitHub Pages settings. It
automatically follows custom-domain changes; manual runs cannot override the URL
and accidentally publish broken project-site asset paths.

CI checks the rendered comparison content, all six platform logos and their image
files, internal post and attribution links, excluded outbound links, and RSS.
After publishing, it checks the same live content and `revision.txt` against the
deployed commit. A build alone therefore cannot be mistaken for a deployment.
Run the content checks locally after building with the matching base URL:

```sh
hugo --minify --panicOnWarning --baseURL https://trustroots.github.io/ideas.trustroots.org/
python3 scripts/check_site.py --directory public --base-url https://trustroots.github.io/ideas.trustroots.org/
```

The workflow pins Hugo and GitHub Actions, verifies the Hugo archive checksum,
and grants Pages write/OIDC permissions only to the deployment job.

## Search and thumbnail crops

`/search/` searches published post titles, authors and text, plus the comparison
page. Hugo generates `search-index.json`; the search page loads it on demand and
ranks results in the browser without an external search service. Search queries
are shareable using `?q=...`. Archive and license pages are excluded from the index.

For a featured portrait that needs a higher crop, add `image_focus: upper` to
that post's front matter. This changes only its card thumbnail's focal point;
the original image and other thumbnails retain their existing framing.

## Content license

Original Trustroots blog text is licensed under **CC BY 4.0**, with author credits
retained on each post. The comparison page retains its original CC BY 4.0 notice.
See [LICENSE](LICENSE) for the legal terms and [License & credits](content/license.md)
for scope and attribution instructions. Third-party material and software source
code are not included in this text license.

## Custom domain

The intended domain is `ideas.trustroots.org` (also recorded in `static/CNAME`).
For this GitHub Actions deployment, GitHub requires the custom domain in
Settings → Pages; the CNAME file alone does not configure it. Cloudflare needs
a DNS-only CNAME named `ideas` pointing to `trustroots.github.io` (without a
repository path), replacing the old record for this hostname. Configure the
GitHub Pages domain before changing DNS, then deploy and enforce HTTPS when the certificate
is ready. Until cutover, the project-site preview continues to use its own URL.
