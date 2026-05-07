import "dotenv/config";
import { appendFile } from "node:fs/promises";
import { Agent, CursorAgentError } from "@cursor/sdk";

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

let agent;

try {
  agent = await Agent.create({
    apiKey,
    model: { id: "composer-2" },
    local: { cwd: process.cwd() },
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
    `\n## ${new Date().toISOString()} - local repo summarizer\n\n- agentId: ${agent.agentId}\n- runId: ${run.id}\n- status: ${status}\n\n### Итог\n\n${assistantText || "См. вывод SDK в консоли."}\n`,
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
