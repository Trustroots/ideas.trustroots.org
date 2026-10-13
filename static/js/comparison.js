(() => {
  const controls = document.querySelector('.comparison-options');
  const tables = [...document.querySelectorAll('.prose > table')].slice(0, 2);
  if (!controls || tables.length !== 2) return;
  tables.forEach(table => { table.classList.add('platform-comparison'); table.tabIndex = 0; table.setAttribute('aria-label', 'Hospitality platform comparison'); });
  const ids = ['cs', 'bw', 'tr', 'co', 'ws', 'servas', 'has', 'hc'];
  const defaults = ids.slice(0, 5);
  const alternatives = ['tr', 'co', 'servas', 'has', 'hc'];
  const inputs = [...controls.querySelectorAll('input')];
  const status = document.querySelector('.comparison-status');
  function update() {
    const selected = inputs.filter(input => input.checked).map(input => input.value);
    for (const table of tables) {
      for (const row of table.rows) {
        [...row.cells].forEach((cell, index) => {
          cell.hidden = index > 0 && !selected.includes(ids[index - 1]);
        });
      }
    }
    status.textContent = selected.length ? `${selected.length} platforms shown. Scroll tables sideways on smaller screens.` : 'Choose at least one platform to compare.';
  }
  function preset(selected) {
    inputs.forEach(input => { input.checked = selected.includes(input.value); });
    update();
  }
  controls.addEventListener('toggle', () => preset(controls.open ? alternatives : defaults));
  controls.addEventListener('change', update);
  controls.hidden = false;
  status.hidden = false;
  preset(defaults);
})();
