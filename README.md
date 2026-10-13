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

CI builds pull requests and pushes to `main`. It does not deploy automatically
until explicitly requested. To publish after review:

1. In repository Settings → Pages, choose **GitHub Actions**.
2. Run **Hugo site** from Actions on `main`, with `deploy` enabled.
3. Review the GitHub Pages URL before changing production DNS.
4. Verify domain ownership in GitHub, configure `ideas.trustroots.org` in Pages,
   then update DNS and enforce HTTPS. Rebuild with the production base URL.

For the initial project-site preview, enter
`https://trustroots.github.io/ideas.trustroots.org/` as the workflow's `base_url`.
The custom domain and DNS have not been configured by this scaffold.

The workflow pins Hugo and GitHub Actions, verifies the Hugo archive checksum,
and grants Pages write/OIDC permissions only to the manual deployment job.
Once domain setup is complete, automatic deployment on `main`
can be enabled deliberately.

## Content license

Original Trustroots blog text is licensed under **CC BY 4.0**, with author credits
retained on each post. The comparison page retains its original CC BY 4.0 notice.
See [LICENSE](LICENSE) for the legal terms and [License & credits](content/license.md)
for scope and attribution instructions. Third-party material and software source
code are not included in this text license.
