# WordPress archive restoration

Checked on 13 October 2026.

## Topics and URLs

- Original WordPress metadata restored for all 51 imported posts: 8 categories and 13 tags.
- Category and tag archives keep their original `/category/.../` and `/tag/.../` URLs. Modern plural paths redirect to them.
- Category/tag pagination uses 10 posts per page to preserve old archive routes, including the search-indexed `/category/uncategorized/page/6/`.
- Old `?p=`, `?page_id=`, `?cat=` and `?tag_id=` URLs redirect in browsers using a fixed map of public IDs. These need JavaScript; GitHub Pages cannot send query-specific HTTP redirects.
- Historical contact, newsletter, volunteering, account, group and app pages now lead readers to current help. Obsolete forms are not recreated.
- The two previously published PDFs keep their original upload URLs. Their PDF object trees were checked for JavaScript, automatic actions, embedded files, launch actions, rich media and XFA before copying.
- Seven old full-size image URLs use the surviving thumbnail copies. These restore the links, with lower resolution.
- `/tag/by-laws/` now redirects to the Foundation archive.

## Missing media

The current import has 200 local blog images. The public Weblate translation badge is displayed from its official endpoint.

23 distinct WordPress image URLs return HTTP 404 and have no matching files in the saved uploads. The public WordPress mirror contains the same broken references. One external TPA image could not be retrieved (TLS timeout). The affected stories have a short archive note instead of dead image links.

Original URLs for a future recovery attempt:

- https://i0.wp.com/ideas.trustroots.org/wp-content/uploads/2021/02/Screenshot-2021-02-06-at-16.52.33.png?ssl=1
- https://i0.wp.com/ideas.trustroots.org/wp-content/uploads/2021/04/15111117_10209773804276135_2169283364924967944_o.jpeg?ssl=1&resize=1536%2C1536
- https://i0.wp.com/ideas.trustroots.org/wp-content/uploads/2021/04/15138523_10209773803276110_5800979883154034976_o-1.jpeg?ssl=1&resize=1536%2C1536
- https://i0.wp.com/ideas.trustroots.org/wp-content/uploads/2021/04/Bea4-1.jpeg?ssl=1
- https://i0.wp.com/ideas.trustroots.org/wp-content/uploads/2021/04/bEA3-1.jpeg?ssl=1
- https://i0.wp.com/ideas.trustroots.org/wp-content/uploads/2021/08/218832323_342739460901048_3267791247241538101_n.jpg?ssl=1
- https://i0.wp.com/ideas.trustroots.org/wp-content/uploads/2021/08/239428893_982340289189748_5913862274539167412_n.jpg?ssl=1
- https://i0.wp.com/ideas.trustroots.org/wp-content/uploads/2021/08/Karu-Finland-3.jpg?ssl=1
- https://i0.wp.com/ideas.trustroots.org/wp-content/uploads/2021/08/Karu-Finland-5.jpg?ssl=1
- https://i0.wp.com/ideas.trustroots.org/wp-content/uploads/2021/09/Edoardo-1.jpg?ssl=1
- https://i1.wp.com/ideas.trustroots.org/wp-content/uploads/2021/04/148681276_10222580873924872_4743158021841354076_n.jpeg?ssl=1&resize=1080%2C1080
- https://i1.wp.com/ideas.trustroots.org/wp-content/uploads/2021/08/Karu-Finland-2.jpg?ssl=1
- https://i1.wp.com/ideas.trustroots.org/wp-content/uploads/2021/08/Karu-Finland.jpg?ssl=1
- https://i1.wp.com/ideas.trustroots.org/wp-content/uploads/2021/09/Edoardo-2.jpg?ssl=1
- https://i1.wp.com/ideas.trustroots.org/wp-content/uploads/2021/09/UNADJUSTEDNONRAW_thumb_33b.jpg?ssl=1
- https://i2.wp.com/ideas.trustroots.org/wp-content/uploads/2021/02/Screenshot-2021-02-06-at-18.34.36.png?ssl=1
- https://i2.wp.com/ideas.trustroots.org/wp-content/uploads/2021/04/Bea5.jpeg?ssl=1
- https://i2.wp.com/ideas.trustroots.org/wp-content/uploads/2021/08/218050197_541661090310511_7680311764213739450_n.jpg?ssl=1
- https://i2.wp.com/ideas.trustroots.org/wp-content/uploads/2021/08/218150486_255632023033310_7034099572798819095_n.jpg?ssl=1
- https://i2.wp.com/ideas.trustroots.org/wp-content/uploads/2021/08/218937536_338047007978884_28727413005100638_n.jpg?ssl=1
- https://i2.wp.com/ideas.trustroots.org/wp-content/uploads/2021/08/238745763_877490089524292_4967716093243906704_n.jpg?ssl=1
- https://i2.wp.com/ideas.trustroots.org/wp-content/uploads/2021/08/Karu-Finland-4.jpg?ssl=1
- https://i2.wp.com/ideas.trustroots.org/wp-content/uploads/2021/09/Meetup7-1024x768.jpg?ssl=1
- https://www.the-tpa.com/images/TPA-p-500.png

## Verification

Hugo builds with `--minify --panicOnWarning`. Local links and image paths were checked across the generated site. Desktop comparison headers and a 390-pixel mobile tag index were visually reviewed. RSS contains the published posts; drafts remain excluded.

Search results are incomplete and change over time. This audit does not prove that every historical URL has been found. Old WordPress feed/plugin endpoints and content outside the published import may still need individual review.
