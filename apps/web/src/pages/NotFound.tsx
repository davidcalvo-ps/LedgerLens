import { Link } from 'react-router';

export function NotFound() {
  return (
    <section aria-labelledby="not-found-title">
      <h1 id="not-found-title">Page not found</h1>
      <p>
        <Link to="/">Back to the dashboard</Link>
      </p>
    </section>
  );
}
