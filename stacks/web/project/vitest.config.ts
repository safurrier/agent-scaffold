import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["tests/**/*.test.ts", "tests/**/*.test.tsx"],
    reporters: ["default", "junit"],
    outputFile: {
      junit: "test-results/vitest-junit.xml",
    },
  },
});
