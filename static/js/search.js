(() => {
  const root = document.querySelector('[data-search-index]');
  if (!root) return;
  const input = document.getElementById('search-query');
  const form = root.querySelector('form');
  const status = document.getElementById('search-status');
  const results = document.getElementById('search-results');
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  let indexPromise;
  let sequence = 0;
  let timer;

  function loadIndex() {
    if (!indexPromise) {
      indexPromise = fetch(root.dataset.searchIndex)
        .then(response => {
          if (!response.ok) throw new Error('Search index unavailable');
          return response.json();
        })
        .then(pages => pages.map(page => ({
          ...page,
          titleKey: normalize(page.title),
          authorKey: normalize(page.author),
          text: page.text.replace(/\s+/g, ' ').trim(),
          key: normalize([page.title, page.author, page.date, page.text].join(' ')),
        })))
        .catch(error => { indexPromise = null; throw error; });
    }
    return indexPromise;
  }

  function excerpt(text, terms, phrase) {
    const key = normalize(text);
    const positions = terms.map(term => key.indexOf(term)).filter(position => position >= 0);
    const phrasePosition = key.indexOf(phrase);
    const position = phrasePosition >= 0 ? phrasePosition : (positions.length ? Math.min(...positions) : 0);
    let start = Math.max(0, position - 65);
    if (start) {
      const space = text.indexOf(' ', start);
      if (space >= 0 && space < start + 25) start = space + 1;
    }
    const snippet = text.slice(start, start + 230).trim();
    return (start ? '… ' : '') + snippet + (text.length > start + 230 ? '…' : '');
  }

  async function search() {
    const request = ++sequence;
    const query = input.value.trim().slice(0, 160);
    const url = new URL(location.href);
    if (query) url.searchParams.set('q', query);
    else url.searchParams.delete('q');
    history.replaceState(null, '', url);
    results.replaceChildren();
    results.removeAttribute('aria-busy');
    if (!query) {
      status.textContent = 'Search titles and text across the blog and comparison page.';
      return;
    }
    status.textContent = 'Searching…';
    results.setAttribute('aria-busy', 'true');
    try {
      const pages = await loadIndex();
      if (request !== sequence) return;
      const terms = [...new Set(normalize(query).split(/\s+/).filter(Boolean))];
      const matches = pages.filter(page => terms.every(term => page.key.includes(term)))
        .map(page => ({ page, score: terms.reduce((score, term) => score + (page.titleKey.includes(term) ? 5 : 0) + (page.authorKey.includes(term) ? 2 : 0), 0) + (page.titleKey.includes(normalize(query)) ? 10 : 0) }))
        .sort((a, b) => b.score - a.score || b.page.date.localeCompare(a.page.date));
      status.textContent = matches.length
        ? `${matches.length} ${matches.length === 1 ? 'result' : 'results'} for “${query}”`
        : `No results for “${query}”. Try another word or browse the archive.`;
      const fragment = document.createDocumentFragment();
      for (const { page } of matches) {
        const item = document.createElement('li');
        const heading = document.createElement('h2');
        const link = document.createElement('a');
        link.href = page.url;
        link.textContent = page.title;
        heading.append(link);
        const meta = document.createElement('p');
        meta.className = 'eyebrow';
        meta.textContent = `${page.dateLabel} · ${page.author}`;
        const summary = document.createElement('p');
        summary.textContent = excerpt(page.text, terms, normalize(query));
        item.append(meta, heading, summary);
        fragment.append(item);
      }
      results.replaceChildren(fragment);
    } catch {
      if (request === sequence) status.textContent = 'Search could not load. Please try again, or browse the archive.';
    } finally {
      if (request === sequence) results.removeAttribute('aria-busy');
    }
  }

  input.value = (new URL(location.href).searchParams.get('q') || '').slice(0, 160);
  input.addEventListener('input', () => {
    clearTimeout(timer);
    timer = setTimeout(search, 150);
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    clearTimeout(timer);
    search();
  });
  search();
})();
