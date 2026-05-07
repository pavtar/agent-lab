import { access, readFile } from "node:fs/promises";
import { join } from "node:path";

const agentName = process.argv[2];

if (!agentName) {
  console.error("Укажите агента: npm run agent:check -- <agent-name>");
  process.exit(1);
}

const requiredFiles = ["README.md", "prompt.md", "config.example.json", "eval-checklist.md"];
const agentDir = join("agents", agentName);
const missing = [];

for (const file of requiredFiles) {
  try {
    await access(join(agentDir, file));
  } catch {
    missing.push(file);
  }
}

if (missing.length) {
  console.error(`Агент "${agentName}" неполный. Не хватает: ${missing.join(", ")}`);
  process.exit(1);
}

const config = JSON.parse(await readFile(join(agentDir, "config.example.json"), "utf8"));

if (config.agentName !== agentName) {
  console.error(`config.example.json: agentName должен быть "${agentName}".`);
  process.exit(1);
}

console.log(`Агент "${agentName}" описан корректно.`);
