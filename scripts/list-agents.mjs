import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";

const agentsDir = "agents";
const draftDir = join(agentsDir, "draft");

const entries = await readdir(agentsDir, { withFileTypes: true });
const topLevel = entries
  .filter((entry) => entry.isDirectory() && entry.name !== "draft")
  .map((entry) => entry.name)
  .sort();

let draftNames = [];
try {
  const draftEntries = await readdir(draftDir, { withFileTypes: true });
  draftNames = draftEntries.filter((entry) => entry.isDirectory()).map((entry) => entry.name).sort();
} catch {
  draftNames = [];
}

console.log("Доступные агенты (первые запуски / портфель):");

for (const agentName of topLevel) {
  await printAgent(agentName, join(agentsDir, agentName));
}

if (draftNames.length) {
  console.log("");
  console.log("Черновики (agents/draft/) — см. docs/agent-roadmap.md:");
  for (const agentName of draftNames) {
    await printAgent(agentName, join(draftDir, agentName));
  }
}

async function printAgent(agentName, baseDir) {
  const readmePath = join(baseDir, "README.md");
  const description = await readFirstDescription(readmePath);
  console.log(`- ${agentName}${description ? ` — ${description}` : ""}`);
}

async function readFirstDescription(readmePath) {
  try {
    const content = await readFile(readmePath, "utf8");
    return content
      .split(/\r?\n/)
      .map((line) => line.trim())
      .find((line) => line && !line.startsWith("#"));
  } catch (error) {
    if (error.code === "ENOENT") return "";
    throw error;
  }
}
