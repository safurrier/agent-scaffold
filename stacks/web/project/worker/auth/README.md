# Auth Activation

This scaffold is D1-ready but does not enable a full login UI by default.

For a saved-runs app, the intended path is Better Auth backed by the same D1
database used by `saved_runs`. Add the Better Auth route once the app has a real
login provider decision, then keep session reads inside the Worker route layer.

The generated `saved_runs.owner_id` column is deliberately generic so it can use
Cloudflare Access email during local/private development or a Better Auth user id
after login is enabled.
