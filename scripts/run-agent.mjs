import { spawn } from "node:child_process";

const agentName = process.argv[2];

const commands = {
  "repo-summarizer": ["node", "scripts/local-repo-summarizer.mjs"],
  "metrika-web-analyst": ["node", "scripts/metrika-web-analyst.mjs"],
};

if (!agentName) {
  console.error("Укажите агента: npm run agent:run -- <agent-name>");
  console.error("Посмотреть список: npm run agents:list");
  process.exit(1);
}

if (!commands[agentName]) {
  console.error(`Для агента "${agentName}" пока нет автоматического SDK-запуска.`);
  console.error("Откройте его README в agents/ и используйте Cursor Agent вручную или создайте mini-plan интеграции.");
  process.exit(1);
}

const [command, ...args] = commands[agentName];
const child = spawn(command, args, {
  stdio: "inherit",
  env: process.env,
  cwd: process.cwd(),
});

child.on("exit", (code) => {
  process.exit(code ?? 1);
});
