import fs from "fs";

async function main() {
  const outputFile = process.argv[2] || "hook-log.json";

  let input = "";
  for await (const chunk of process.stdin) {
    input += chunk;
  }

  if (!input.trim()) {
    fs.writeFileSync(outputFile, "{}\n", "utf8");
    return;
  }

  try {
    const parsed = JSON.parse(input);
    fs.writeFileSync(outputFile, `${JSON.stringify(parsed, null, 2)}\n`, "utf8");
  } catch {
    // Keep raw payload if parsing fails so debugging data is not lost.
    fs.writeFileSync(outputFile, `${input.trim()}\n`, "utf8");
  }
}

main().catch((err) => {
  console.error(`log_hook error: ${err.message}`);
  process.exit(1);
});
