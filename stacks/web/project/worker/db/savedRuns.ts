export interface SavedRunRow {
  id: string;
  owner_id: string;
  title: string;
  lineup_json: string;
  result_json: string;
  created_at: string;
}

export interface CreateSavedRunInput {
  title?: string;
  lineup: unknown;
  result: unknown;
}

export async function listSavedRuns(
  db: D1Database,
  ownerId: string,
): Promise<SavedRunRow[]> {
  const rows = await db
    .prepare(
      `SELECT id, owner_id, title, lineup_json, result_json, created_at
       FROM saved_runs
       WHERE owner_id = ?
       ORDER BY created_at DESC
       LIMIT 50`,
    )
    .bind(ownerId)
    .all<SavedRunRow>();
  return rows.results ?? [];
}

export async function createSavedRun(
  db: D1Database,
  ownerId: string,
  input: CreateSavedRunInput,
): Promise<SavedRunRow> {
  const id = crypto.randomUUID();
  const title = input.title?.trim() || "Untitled run";
  const createdAt = new Date().toISOString();
  const lineupJson = JSON.stringify(input.lineup);
  const resultJson = JSON.stringify(input.result);

  await db
    .prepare(
      `INSERT INTO saved_runs
        (id, owner_id, title, lineup_json, result_json, created_at)
       VALUES (?, ?, ?, ?, ?, ?)`,
    )
    .bind(id, ownerId, title, lineupJson, resultJson, createdAt)
    .run();

  return {
    id,
    owner_id: ownerId,
    title,
    lineup_json: lineupJson,
    result_json: resultJson,
    created_at: createdAt,
  };
}
