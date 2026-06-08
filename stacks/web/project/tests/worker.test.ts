import { describe, expect, it } from "vitest";
import { handleHealth } from "../worker/routes/health";

describe("worker health route", () => {
  it("returns an ok health payload", async () => {
    const response = handleHealth();
    expect(response.status).toBe(200);
    await expect(response.json()).resolves.toMatchObject({ ok: true });
  });
});
