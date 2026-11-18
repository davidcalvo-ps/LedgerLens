import type { AppRoute } from '../routes';

export function SectionPage({ route }: { route: AppRoute }) {
  return (
    <section aria-labelledby={`${route.id}-title`}>
      <h1 id={`${route.id}-title`}>{route.label}</h1>
      <p className="lead">{route.summary}</p>
      <p className="empty">Planned for week {route.plannedWeek} of the roadmap.</p>
    </section>
  );
}
