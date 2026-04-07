import fs from "fs";
import path from "path";
import { spawnSync } from "child_process";

async function readInput() {
  let input = "";
  for await (const chunk of process.stdin) {
    input += chunk;
  }
  return input;
}

async function main() {
  const raw = await readInput();
  if (!raw.trim()) {
    process.exit(0);
  }

  let payload;
  try {
    payload = JSON.parse(raw);
  } catch {
    process.exit(0);
  }

  const filePath = payload.tool_response?.filePath || payload.tool_input?.file_path || payload.tool_input?.path;
  if (!filePath || typeof filePath !== "string") {
    process.exit(0);
  }

  const resolvedPath = path.resolve(filePath);
  if (!fs.existsSync(resolvedPath)) {
    process.exit(0);
  }

  const result = spawnSync(
    "npx",
    ["--yes", "prettier", "--write", resolvedPath],
    { stdio: "inherit", shell: true }
  );

  // Formatting is best-effort and should not block edits.
  if (result.status !== 0) {
    process.exit(0);
  }
}

main().catch(() => {
  process.exit(0);
});
