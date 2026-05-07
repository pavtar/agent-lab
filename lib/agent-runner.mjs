import { Agent, CursorAgentError } from "@cursor/sdk";

export async function runLocalCursorAgent({ apiKey, agentName, prompt, cwd = process.cwd(), model = "composer-2" }) {
  let agent;

  try {
    agent = await Agent.create({
      apiKey,
      model: { id: model },
      local: { cwd },
    });

    const run = await agent.send(prompt);
    console.log(`agentName: ${agentName}`);
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

    return {
      agentId: agent.agentId,
      runId: run.id,
      status,
      assistantText,
    };
  } catch (error) {
    if (error instanceof CursorAgentError) {
      error.messageForUser = `Ошибка запуска SDK: ${error.message}\nМожно повторить: ${error.isRetryable}`;
    }

    throw error;
  } finally {
    if (agent) await agent[Symbol.asyncDispose]();
  }
}

export function failWithAgentError(error) {
  if (error?.messageForUser) {
    console.error(error.messageForUser);
    process.exit(1);
  }

  throw error;
}
