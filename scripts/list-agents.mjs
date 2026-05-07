import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";

const agentsDir = "agents";
const entries = await readdir(agentsDir, { withFileTypes: true });
const agentNames = entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name).sort();

console.log("Доступные агенты:");

for (const agentName of agentNames) {
  const readmePath = join(agentsDir, agentName, "README.md");
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
