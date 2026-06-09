# Auth Activation

This scaffold is D1-ready but does not enable a full login UI by default.

For a saved-runs app, the intended path is Better Auth backed by the same D1
database used by `saved_runs`. Add the Better Auth route once the app has a real
login provider decision, then keep session reads inside the Worker route layer.

The generated `saved_runs.owner_id` column is deliberately generic so it can use
a Better Auth user id, a validated Cloudflare Access identity, or another stable
app user id after login is enabled.

Until real auth is wired, saved-run routes only allow the explicit localhost
`local-dev` owner. Deployed requests return `401` even if a caller sends identity
headers, because those headers are spoofable unless the Worker validates the auth
provider's token or runs behind a trusted access boundary.
