import { formatSavedRunTitle } from "../sim/savedRun";

export function ExamplePanel() {
  return (
    <section className="panel">
      <h2>Ready for a real app</h2>
      <p>
        The generated stack includes a React frontend, a Cloudflare Worker API,
        and a D1 migration for saved runs.
      </p>
      <code>
        {formatSavedRunTitle("Example run", new Date("2026-06-08T00:00:00Z"))}
      </code>
    </section>
  );
}
