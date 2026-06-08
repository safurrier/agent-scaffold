import { handleHealth } from "./routes/health";
import { handleRunsRequest } from "./routes/runs";

export interface Env {
  ASSETS: Fetcher;
  DB: D1Database;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    return handleRequest(request, env);
  },
} satisfies ExportedHandler<Env>;

export async function handleRequest(
  request: Request,
  env: Env,
): Promise<Response> {
  const url = new URL(request.url);

  if (request.method === "GET" && url.pathname === "/api/health") {
    return handleHealth();
  }

  if (url.pathname.startsWith("/api/runs")) {
    return handleRunsRequest(request, env);
  }

  return env.ASSETS.fetch(request);
}
