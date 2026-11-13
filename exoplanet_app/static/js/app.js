:root {
  --bg: #020817;
  --panel: rgba(15, 23, 42, 0.9);
  --panel-strong: #111827;
  --surface: #0f172a;
  --muted: #94a3b8;
  --text: #e2e8f0;
  --accent: #5eead4;
  --accent-strong: #14b8a6;
  --border: rgba(148, 163, 184, 0.2);
  --shadow: rgba(15, 23, 42, 0.5);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Inter, "Segoe UI", sans-serif;
  background: radial-gradient(circle at top, #0f172a 0%, #020817 55%);
  color: var(--text);
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 3rem;
  border-bottom: 1px solid var(--border);
  background: rgba(15, 23, 42, 0.85);
  position: sticky;
  top: 0;
  backdrop-filter: blur(12px);
}

.brand {
  color: var(--text);
  text-decoration: none;
  font-size: 1.4rem;
  font-weight: 700;
}

.nav {
  display: flex;
  gap: 1.2rem;
}

.nav a {
  color: var(--muted);
  text-decoration: none;
}

.page-shell {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.2rem 4rem;
}

.hero {
  padding: 3rem 0 2rem;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.7rem;
  color: var(--accent);
  margin-bottom: 0.8rem;
}

h1, h2 {
  margin-top: 0;
}

h1 {
  font-size: clamp(2.2rem, 5vw, 4rem);
  margin-bottom: 0.8rem;
}

.subtitle {
  color: var(--muted);
  max-width: 700px;
  line-height: 1.6;
}

.cta-row {
  margin-top: 1.5rem;
}

.primary-btn, .ghost-btn {
  padding: 0.8rem 1.2rem;
  border-radius: 10px;
  border: 1px solid transparent;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
}

.primary-btn {
  background: linear-gradient(135deg, var(--accent), var(--accent-strong));
  color: #06213b;
  font-weight: 700;
}

.ghost-btn {
  border-color: var(--border);
  color: var(--text);
  background: transparent;
}

.alert-banner {
  background: rgba(20, 184, 166, 0.12);
  border: 1px solid rgba(94, 234, 212, 0.4);
  color: #d1fae5;
  border-radius: 12px;
  padding: 0.9rem 1rem;
  margin-top: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.stat-card, .panel {
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid var(--border);
  border-radius: 18px;
  box-shadow: 0 15px 35px var(--shadow);
}

.stat-card {
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.stat-card span {
  color: var(--muted);
  font-size: 0.8rem;
}

.stat-card strong {
  font-size: 2rem;
}

.panel-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1rem;
  margin-top: 1.5rem;
}

.panel {
  padding: 1.4rem;
}

.panel-wide {
  min-height: 320px;
}

.bullets {
  margin: 0;
  padding-left: 1.2rem;
  color: var(--muted);
  line-height: 1.8;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  color: var(--muted);
  font-size: 0.8rem;
}

input, select {
  width: 100%;
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid var(--border);
  color: var(--text);
  border-radius: 8px;
  padding: 0.72rem 0.75rem;
}

.button-row {
  margin-top: 1rem;
  display: flex;
  gap: 0.8rem;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th, td {
  text-align: left;
  padding: 0.8rem 0.75rem;
  border-bottom: 1px solid var(--border);
}

th {
  color: var(--muted);
  font-weight: 600;
}

tbody tr:hover {
  background: rgba(148, 163, 184, 0.08);
}

.pager {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
}

.results-meta {
  color: var(--muted);
  font-size: 0.9rem;
}

.detail-grid {
  margin-bottom: 1.5rem;
}

@media (max-width: 768px) {
  .topbar {
    padding: 1rem 1.2rem;
    flex-direction: column;
    gap: 1rem;
  }

  .panel-grid {
    grid-template-columns: 1fr;
  }
}
