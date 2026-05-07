import dotenv from "dotenv";
import {
  MetrikaApiError,
  MetrikaConfigError,
  formatCounters,
  listCounters,
  requireEnv,
} from "../lib/yandex-metrika-client.mjs";

dotenv.config({ override: true });

const search = getArgValue("--search");

try {
  const token = requireEnv("YANDEX_METRIKA_TOKEN");
  const counters = await listCounters({ token, search });

  console.log("ID\tНазвание\tСайт\tСтатус");
  console.log(formatCounters(counters));

  if (!process.env.YANDEX_METRIKA_COUNTER_ID && counters.length) {
    console.log("");
    console.log("Выберите нужный ID и добавьте в .env:");
    console.log(`YANDEX_METRIKA_COUNTER_ID=${counters[0].id}`);
  }
} catch (error) {
  if (error instanceof MetrikaConfigError || error instanceof MetrikaApiError) {
    console.error(error.message);
    process.exit(1);
  }

  throw error;
}

function getArgValue(name) {
  const index = process.argv.indexOf(name);
  return index === -1 ? undefined : process.argv[index + 1];
}
