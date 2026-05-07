import dotenv from "dotenv";
import { appendFile } from "node:fs/promises";
import { Agent, CursorAgentError } from "@cursor/sdk";

dotenv.config({ override: true });

const apiKey = process.env.CURSOR_API_KEY;
const repoUrl = process.env.GITHUB_REPO_URL;
const startingRef = process.env.GITHUB_STARTING_REF || "main";

if (!apiKey) {
  console.error("Нет CURSOR_API_KEY. Создайте ключ в Cursor Dashboard -> Integrations и экспортируйте переменную окружения.");
  process.exit(1);
}

if (!repoUrl) {
  console.error("Нет GITHUB_REPO_URL. Укажите URL опубликованного GitHub-репозитория, например https://github.com/your-user/agent-lab.");
  process.exit(1);
}

const prompt = `Сделай безопасное документационное изменение.

Задача:
- изучи README.md;
- улучши его так, чтобы руководителю без dev/devops опыта было понятно, как запустить первого локального агента;
- не меняй секреты, зависимости и production-конфигурации;
- создай Pull Request для ручной проверки.

Критерий готовности: README.md стал понятнее, а PR содержит краткое описание изменений.`;

let agent;

try {
  agent = await Agent.create({
    apiKey,
    model: { id: "composer-2" },
    cloud: {
      repos: [{ url: repoUrl, startingRef }],
      autoCreatePR: true,
    },
  });

  const run = await agent.send(prompt);
  console.log(`agentId: ${agent.agentId}`);
  console.log(`runId: ${run.id}`);
  console.log("");

  let assistantText = "";

  if (run.supports("stream")) {
    for await (const event of run.stream()) {
      if (event.type !== "assistant") continue;

      for (const block of event.message.content) {
        if (block.type !== "text") continue;
        process.stdout.write(block.text);
        assistantText += block.text;
      }
    }
  }

  const result = await run.wait();
  const status = result.status ?? "unknown";

  await appendFile(
    "docs/agent-log.md",
    `\n## ${new Date().toISOString()} - cloud README PR\n\n- agentId: ${agent.agentId}\n- runId: ${run.id}\n- status: ${status}\n- repo: ${repoUrl}\n- startingRef: ${startingRef}\n\n### Итог\n\n${assistantText || "См. вывод SDK в консоли и Cursor Dashboard."}\n`,
  );

  if (status !== "finished") {
    console.error(`\nАгент завершился со статусом: ${status}`);
    process.exit(2);
  }
} catch (error) {
  if (error instanceof CursorAgentError) {
    console.error(`Ошибка запуска SDK: ${error.message}`);
    console.error(`Можно повторить: ${error.isRetryable}`);
    process.exit(1);
  }

  throw error;
} finally {
  if (agent) {
    await agent[Symbol.asyncDispose]();
  }
}
