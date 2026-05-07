import dotenv from "dotenv";
import { appendFile } from "node:fs/promises";
import { failWithAgentError, runLocalCursorAgent } from "../lib/agent-runner.mjs";

dotenv.config({ override: true });

const apiKey = process.env.CURSOR_API_KEY;

if (!apiKey) {
  console.error("Нет CURSOR_API_KEY. Создайте ключ в Cursor Dashboard -> Integrations и экспортируйте переменную окружения.");
  process.exit(1);
}

const prompt = `Изучи этот репозиторий и кратко объясни, что в нём есть.

Правила:
- ничего не меняй;
- не создавай файлы;
- не запускай команды, которые меняют проект;
- объясняй простым языком для руководителя без dev/devops опыта.

В конце дай 3 следующие безопасные задачи для агента.`;

try {
  const runResult = await runLocalCursorAgent({
    apiKey,
    agentName: "repo-summarizer",
    prompt,
  });

  await appendFile(
    "docs/agent-log.md",
    `\n## ${new Date().toISOString()} - local repo summarizer\n\n- agentName: repo-summarizer\n- agentId: ${runResult.agentId}\n- runId: ${runResult.runId}\n- status: ${runResult.status}\n- promptVersion: 0.1.0\n\n### Итог\n\n${runResult.assistantText || "См. вывод SDK в консоли."}\n`,
  );

  if (runResult.status !== "finished") {
    console.error(`\nАгент завершился со статусом: ${runResult.status}`);
    process.exit(2);
  }
} catch (error) {
  failWithAgentError(error);
}
