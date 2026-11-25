import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config.ts";

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: "node",
      include: ["tests/**/*.test.{ts,tsx}", "prototype/tests/**/*.test.ts"],
      exclude: ["**/e2e/**", "**/node_modules/**"],
    },
  }),
);
