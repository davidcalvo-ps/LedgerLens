import { routeById } from '../routes';

const TILES = [
  { label: 'Cash on hand', hint: 'Sum of posted transactions across bank accounts' },
  { label: 'Bills due in 14 days', hint: 'Approved bills not yet paid' },
  { label: 'Open receivables', hint: 'Sent and part-paid invoices' },
  { label: 'Runway', hint: 'Days until projected cash drops below zero' },
] as const;

export function Dashboard() {
  const route = routeById('dashboard');
  return (
    <section aria-labelledby="dashboard-title">
      <h1 id="dashboard-title">{route.label}</h1>
      <p className="lead">{route.summary}</p>
      <ul className="tiles">
        {TILES.map((t) => (
          <li key={t.label} className="tile">
            <span className="tile-label">{t.label}</span>
            <span className="tile-value" aria-label={`${t.label}: no data yet`}>
              —
            </span>
            <span className="tile-hint">{t.hint}</span>
          </li>
        ))}
      </ul>
      <p className="empty">
        No ledger data yet. Figures appear here once a bank CSV has been imported and the
        forecast engine is in place (week {route.plannedWeek}).
      </p>
    </section>
  );
}
