import { createSavedRun, listSavedRuns } from "../db/savedRuns";
import type { Env } from "../index";

export async function handleRunsRequest(
  request: Request,
  env: Env,
): Promise<Response> {
  const url = new URL(request.url);

  if (request.method === "GET" && url.pathname === "/api/runs/mine") {
    const ownerId = ownerFromRequest(request);
    if (!ownerId) {
      return Response.json({ error: "unauthorized" }, { status: 401 });
    }
    return Response.json({ runs: await listSavedRuns(env.DB, ownerId) });
  }

  if (request.method === "POST" && url.pathname === "/api/runs") {
    const ownerId = ownerFromRequest(request);
    if (!ownerId) {
      return Response.json({ error: "unauthorized" }, { status: 401 });
    }
    const body = (await request.json().catch(() => null)) as unknown;
    if (!isCreateRunBody(body)) {
      return Response.json({ error: "invalid_run" }, { status: 400 });
    }
    const run = await createSavedRun(env.DB, ownerId, body);
    return Response.json({ run }, { status: 201 });
  }

  return Response.json({ error: "not_found" }, { status: 404 });
}

function ownerFromRequest(request: Request): string | null {
  const accessEmail = request.headers.get("Cf-Access-Authenticated-User-Email");
  if (accessEmail) return accessEmail;

  const hostname = new URL(request.url).hostname;
  if (
    hostname === "localhost" ||
    hostname === "127.0.0.1" ||
    hostname === "[::1]"
  ) {
    return "local-dev";
  }
  return null;
}

interface CreateRunBody {
  title?: string;
  lineup: unknown;
  result: unknown;
}

function isCreateRunBody(body: unknown): body is CreateRunBody {
  if (!body || typeof body !== "object") return false;
  const candidate = body as Record<string, unknown>;
  return "lineup" in candidate && "result" in candidate;
}
