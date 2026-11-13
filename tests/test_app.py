const state = {
  page: 1,
  perPage: 20,
  total: 0,
  lastQuery: null,
};

function readFilters() {
  return {
    q: document.getElementById('search-input')?.value || '',
    discovery_method: document.getElementById('method-filter')?.value || '',
    radius_min: parseFloat(document.getElementById('radius-min')?.value || '0') || undefined,
    radius_max: parseFloat(document.getElementById('radius-max')?.value || '') || undefined,
    mass_min: parseFloat(document.getElementById('mass-min')?.value || '0') || undefined,
    mass_max: parseFloat(document.getElementById('mass-max')?.value || '') || undefined,
    year_min: parseInt(document.getElementById('year-min')?.value || '', 10) || undefined,
    year_max: parseInt(document.getElementById('year-max')?.value || '', 10) || undefined,
  };
}

async function fetchDiscoveryMethods() {
  const response = await fetch('/api/exoplanets?page=1&per_page=1');
  const data = await response.json();
  const uniqueMethods = [...new Set((data.items || []).map(item => item.discovery_method).filter(Boolean))];
  const select = document.getElementById('method-filter');
  if (!select) return;

  uniqueMethods.forEach(method => {
    const option = document.createElement('option');
    option.value = method;
    option.textContent = method;
    select.appendChild(option);
  });
}

async function loadCatalog() {
  const filters = readFilters();
  state.lastQuery = filters;

  const query = new URLSearchParams({
    page: String(state.page),
    per_page: String(state.perPage),
    ...Object.fromEntries(
      Object.entries(filters).filter(([, value]) => value !== '' && value !== null && value !== undefined)
    ),
  });

  const response = await fetch(`/api/exoplanets?${query.toString()}`);
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

  document.getElementById('prev-page')?.toggleAttribute('disabled', state.page <= 1);
  document.getElementById('next-page')?.toggleAttribute('disabled', state.page >= (data.pages || 1));
}

function attachEvents() {
  document.getElementById('apply-filters')?.addEventListener('click', () => {
    state.page = 1;
    loadCatalog();
  });

  document.getElementById('reset-filters')?.addEventListener('click', () => {
    document.getElementById('search-input').value = '';
    document.getElementById('method-filter').value = '';
    document.getElementById('radius-min').value = '';
    document.getElementById('radius-max').value = '';
    document.getElementById('mass-min').value = '';
    document.getElementById('mass-max').value = '';
    document.getElementById('year-min').value = '';
    document.getElementById('year-max').value = '';
    state.page = 1;
    loadCatalog();
  });

  document.getElementById('prev-page')?.addEventListener('click', () => {
    if (state.page > 1) {
      state.page -= 1;
      loadCatalog();
    }
  });

  document.getElementById('next-page')?.addEventListener('click', () => {
    state.page += 1;
    loadCatalog();
  });
}

fetchDiscoveryMethods();
attachEvents();
loadCatalog();
