import { describe, expect, it } from "vitest";
import { formatSavedRunTitle } from "../src/sim/savedRun";

describe("formatSavedRunTitle", () => {
  it("formats the title with an ISO date", () => {
    const title = formatSavedRunTitle(
      "Perfect season",
      new Date("2026-06-08T12:00:00Z"),
    );
    expect(title).toBe("Perfect season - 2026-06-08");
  });
});
