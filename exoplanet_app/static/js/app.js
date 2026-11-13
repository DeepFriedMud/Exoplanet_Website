const state = {
  page: 1,
  perPage: 20,
  total: 0,
};

function readFilters() {
  const searchInput = document.getElementById('search-input');
  const methodFilter = document.getElementById('method-filter');
  const radiusMinInput = document.getElementById('radius-min');
  const radiusMaxInput = document.getElementById('radius-max');
  const massMinInput = document.getElementById('mass-min');
  const massMaxInput = document.getElementById('mass-max');
  const yearMinInput = document.getElementById('year-min');
  const yearMaxInput = document.getElementById('year-max');

  return {
    q: searchInput ? searchInput.value.trim() : '',
    discovery_method: methodFilter ? methodFilter.value : '',
    radius_min: radiusMinInput && radiusMinInput.value ? Number(radiusMinInput.value) : undefined,
    radius_max: radiusMaxInput && radiusMaxInput.value ? Number(radiusMaxInput.value) : undefined,
    mass_min: massMinInput && massMinInput.value ? Number(massMinInput.value) : undefined,
    mass_max: massMaxInput && massMaxInput.value ? Number(massMaxInput.value) : undefined,
    year_min: yearMinInput && yearMinInput.value ? Number(yearMinInput.value) : undefined,
    year_max: yearMaxInput && yearMaxInput.value ? Number(yearMaxInput.value) : undefined,
  };
}

async function fetchDiscoveryMethods() {
  const response = await fetch('/api/exoplanets?page=1&per_page=200');
  const data = await response.json();
  const select = document.getElementById('method-filter');
  if (!select) return;

  const methods = [...new Set((data.items || []).map(item => item.discovery_method).filter(Boolean))];
  select.innerHTML = '<option value="">Any</option>';
  methods.forEach(method => {
    const option = document.createElement('option');
    option.value = method;
    option.textContent = method;
    select.appendChild(option);
  });
}

async function loadCatalog() {
  const filters = readFilters();
  const params = new URLSearchParams({
    page: String(state.page),
    per_page: String(state.perPage),
  });

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== '' && value !== undefined && value !== null) {
      params.append(key, String(value));
    }
  });

  const response = await fetch(`/api/exoplanets?${params.toString()}`);
  const data = await response.json();

  state.total = data.total || 0;
  const tableBody = document.getElementById('planet-table-body');
  if (!tableBody) return;

  tableBody.innerHTML = '';
  if (!data.items || data.items.length === 0) {
    tableBody.innerHTML = '<tr><td colspan="8">No planets match the current filters.</td></tr>';
  } else {
    data.items.forEach(item => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><a href="/planet/${item.id}">${item.name}</a></td>
        <td>${item.host_star_name || '—'}</td>
        <td>${item.discovery_method || '—'}</td>
        <td>${item.discovery_year ?? '—'}</td>
        <td>${item.orbital_period_days ?? '—'}</td>
        <td>${item.radius_jupiter ?? '—'}</td>
        <td>${item.mass_jupiter ?? '—'}</td>
        <td>${item.equilibrium_temperature_k ?? '—'}</td>
      `;
      tableBody.appendChild(row);
    });
  }

  const meta = document.getElementById('results-meta');
  if (meta) {
    meta.textContent = `Showing ${data.items?.length || 0} of ${data.total || 0} planets.`;
  }

  const pageIndicator = document.getElementById('page-indicator');
  if (pageIndicator) {
    pageIndicator.textContent = `Page ${state.page} / ${data.pages || 1}`;
  }

  const prevButton = document.getElementById('prev-page');
  const nextButton = document.getElementById('next-page');
  if (prevButton) prevButton.disabled = state.page <= 1;
  if (nextButton) nextButton.disabled = state.page >= (data.pages || 1);
}

function attachEvents() {
  const applyButton = document.getElementById('apply-filters');
  const resetButton = document.getElementById('reset-filters');
  const prevButton = document.getElementById('prev-page');
  const nextButton = document.getElementById('next-page');

  applyButton?.addEventListener('click', () => {
    state.page = 1;
    loadCatalog();
  });

  resetButton?.addEventListener('click', () => {
    const searchInput = document.getElementById('search-input');
    const methodFilter = document.getElementById('method-filter');
    const radiusMinInput = document.getElementById('radius-min');
    const radiusMaxInput = document.getElementById('radius-max');
    const massMinInput = document.getElementById('mass-min');
    const massMaxInput = document.getElementById('mass-max');
    const yearMinInput = document.getElementById('year-min');
    const yearMaxInput = document.getElementById('year-max');

    if (searchInput) searchInput.value = '';
    if (methodFilter) methodFilter.value = '';
    if (radiusMinInput) radiusMinInput.value = '';
    if (radiusMaxInput) radiusMaxInput.value = '';
    if (massMinInput) massMinInput.value = '';
    if (massMaxInput) massMaxInput.value = '';
    if (yearMinInput) yearMinInput.value = '';
    if (yearMaxInput) yearMaxInput.value = '';

    state.page = 1;
    loadCatalog();
  });

  prevButton?.addEventListener('click', () => {
    if (state.page > 1) {
      state.page -= 1;
      loadCatalog();
    }
  });

  nextButton?.addEventListener('click', () => {
    state.page += 1;
    loadCatalog();
  });
}

fetchDiscoveryMethods();
attachEvents();
loadCatalog();
