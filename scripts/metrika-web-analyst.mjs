import dotenv from "dotenv";
import { mkdir, writeFile, appendFile } from "node:fs/promises";
import { join } from "node:path";
import { failWithAgentError, runLocalCursorAgent } from "../lib/agent-runner.mjs";
import {
  MetrikaApiError,
  MetrikaConfigError,
  fetchReport,
  getCounterInfo,
  getDateRange,
  listGoals,
  parseGoalIds,
  reportToMarkdownTable,
  requireEnv,
  totalsToMarkdown,
} from "../lib/yandex-metrika-client.mjs";

dotenv.config({ override: true });

const OBSIDIAN_RUN_LOGS_DIR = join("..", "Company OS", "Run Logs");
const HUMAN_VISITS_FILTER = "ym:s:isRobot=='No'";
const ORGANIC_TRAFFIC_FILTER = "ym:s:lastsignTrafficSource=='organic'";

const trafficMetrics = [
  "ym:s:visits",
  "ym:s:users",
  "ym:s:bounceRate",
  "ym:s:pageDepth",
  "ym:s:avgVisitDurationSeconds",
];

const seoMetrics = [
  "ym:s:visits",
  "ym:s:users",
  "ym:s:bounceRate",
  "ym:s:pageDepth",
  "ym:s:avgVisitDurationSeconds",
];

try {
  const apiKey = requireEnv("CURSOR_API_KEY");
  const token = requireEnv("YANDEX_METRIKA_TOKEN");
  const counterId = requireEnv("YANDEX_METRIKA_COUNTER_ID");
  const goalIds = parseGoalIds(process.env.YANDEX_METRIKA_GOAL_IDS);
  const { date1, date2 } = getDateRange(Number(process.env.METRIKA_REPORT_DAYS || 30));

  const counter = await getCounterInfo({ token, counterId });
  const goals = await listGoals({ token, counterId });
  const selectedGoals = goals.filter((goal) => goalIds.includes(String(goal.id)));

  const traffic = await fetchReport({
    token,
    counterId,
    date1,
    date2,
    metrics: trafficMetrics.join(","),
    dimensions: "ym:s:lastsignTrafficSource",
    filters: HUMAN_VISITS_FILTER,
    sort: "-ym:s:visits",
    limit: 20,
    cacheName: "traffic",
  });

  const utm = await fetchReport({
    token,
    counterId,
    date1,
    date2,
    metrics: "ym:s:visits,ym:s:users,ym:s:bounceRate",
    dimensions: "ym:s:lastsignUTMCampaign",
    filters: HUMAN_VISITS_FILTER,
    sort: "-ym:s:visits",
    limit: 20,
    cacheName: "utm",
  });

  const searchEngines = await fetchReport({
    token,
    counterId,
    date1,
    date2,
    metrics: "ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth",
    dimensions: "ym:s:searchEngineName",
    filters: combineMetrikaFilters(HUMAN_VISITS_FILTER, ORGANIC_TRAFFIC_FILTER),
    sort: "-ym:s:visits",
    limit: 20,
    cacheName: "search-engines",
  });

  const seoReportWarnings = [];
  const searchPhrases = await fetchOptionalReport({
    reportName: "поисковые фразы",
    warnings: seoReportWarnings,
    request: {
      token,
      counterId,
      date1,
      date2,
      preset: "sources_search_phrases",
      metrics: seoMetrics.join(","),
      filters: HUMAN_VISITS_FILTER,
      sort: "-ym:s:visits",
      limit: 20,
      cacheName: "search-phrases",
    },
  });
  const organicLandingPages = await fetchOptionalReport({
    reportName: "органические посадочные страницы",
    warnings: seoReportWarnings,
    request: {
      token,
      counterId,
      date1,
      date2,
      metrics: seoMetrics.join(","),
      dimensions: "ym:s:startURLHash",
      filters: combineMetrikaFilters(HUMAN_VISITS_FILTER, ORGANIC_TRAFFIC_FILTER),
      sort: "-ym:s:visits",
      limit: 20,
      cacheName: "organic-landing-pages",
    },
  });
  const organicDevices = await fetchOptionalReport({
    reportName: "органика по устройствам",
    warnings: seoReportWarnings,
    request: {
      token,
      counterId,
      date1,
      date2,
      metrics: seoMetrics.join(","),
      dimensions: "ym:s:deviceCategory",
      filters: combineMetrikaFilters(HUMAN_VISITS_FILTER, ORGANIC_TRAFFIC_FILTER),
      sort: "-ym:s:visits",
      limit: 10,
      cacheName: "organic-devices",
    },
  });

  const conversions = selectedGoals.length
    ? await fetchReport({
        token,
        counterId,
        date1,
        date2,
        metrics: selectedGoals
          .flatMap((goal) => [`ym:s:goal${goal.id}reaches`, `ym:s:goal${goal.id}conversionRate`])
          .join(","),
        filters: HUMAN_VISITS_FILTER,
        limit: 1,
        cacheName: "conversions",
      })
    : undefined;

  const dataSnapshot = buildDataSnapshot({
    counter,
    date1,
    date2,
    goals,
    selectedGoals,
    traffic,
    utm,
    searchEngines,
    searchPhrases,
    organicLandingPages,
    organicDevices,
    seoReportWarnings,
    conversions,
  });

  const runResult = await runLocalCursorAgent({
    apiKey,
    agentName: "metrika-web-analyst",
    prompt: buildPrompt(dataSnapshot),
  });
  const reportPath = await writeObsidianReport({
    date1,
    date2,
    counter,
    agentId: runResult.agentId,
    runId: runResult.runId,
    status: runResult.status,
    dataSnapshot,
    assistantText: runResult.assistantText,
  });

  await appendFile(
    "docs/agent-log.md",
    `\n## ${new Date().toISOString()} - metrika web analyst\n\n- agentName: metrika-web-analyst\n- agentId: ${runResult.agentId}\n- runId: ${runResult.runId}\n- status: ${runResult.status}\n- agentVersion: 0.2.1\n- promptVersion: 0.2.1\n- counterId: ${counterId}\n- period: ${date1} — ${date2}\n- dataFilter: only human visits, ${HUMAN_VISITS_FILTER}\n- obsidianReport: ${reportPath}\n\n`,
  );

  console.log("");
  console.log(`\nObsidian отчёт: ${reportPath}`);

  if (runResult.status !== "finished") {
    console.error(`\nАгент завершился со статусом: ${runResult.status}`);
    process.exit(2);
  }
} catch (error) {
  if (error instanceof MetrikaConfigError || error instanceof MetrikaApiError) {
    console.error(error.message);
    process.exit(1);
  }

  failWithAgentError(error);
}

async function fetchOptionalReport({ reportName, request, warnings }) {
  try {
    return await fetchReport(request);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    warnings.push(`${reportName}: ${message}`);
    return undefined;
  }
}

function combineMetrikaFilters(...filters) {
  return filters.filter(Boolean).map((filter) => `(${filter})`).join(" AND ");
}

function buildDataSnapshot({
  counter,
  date1,
  date2,
  goals,
  selectedGoals,
  traffic,
  utm,
  searchEngines,
  searchPhrases,
  organicLandingPages,
  organicDevices,
  seoReportWarnings,
  conversions,
}) {
  const conversionMetrics = selectedGoals.flatMap((goal) => [
    `goal ${goal.id} reaches (${goal.name})`,
    `goal ${goal.id} conversion rate (${goal.name})`,
  ]);

  return `# Данные Яндекс.Метрики

## Контекст

- Счётчик: ${counter.id} — ${counter.name || "-"}
- Сайт: ${counter.site || "-"}
- Период: ${date1} — ${date2}
- Фильтр данных: только визиты людей, исключены роботы через ${HUMAN_VISITS_FILTER}
- Доступные цели: ${goals.length ? goals.map((goal) => `${goal.id} ${goal.name}`).join("; ") : "цели не найдены"}
- Выбранные бизнес-цели: ${selectedGoals.length ? selectedGoals.map((goal) => `${goal.id} ${goal.name}`).join("; ") : "не выбраны"}

## Итого по трафику

${totalsToMarkdown(traffic, trafficMetrics)}

## Источники трафика

${reportToMarkdownTable(traffic, {
  dimensions: ["Источник"],
  metrics: ["Визиты", "Пользователи", "Отказы %", "Глубина", "Время сек"],
})}

## UTM-кампании

${reportToMarkdownTable(utm, {
  dimensions: ["UTM campaign"],
  metrics: ["Визиты", "Пользователи", "Отказы %"],
})}

## Поисковые системы

${reportToMarkdownTable(searchEngines, {
  dimensions: ["Поисковая система"],
  metrics: ["Визиты", "Пользователи", "Отказы %", "Глубина"],
})}

## SEO-срез

### Поисковые фразы

${reportOrLimitation(
  searchPhrases,
  {
    dimensions: ["Поисковая система", "Поисковая фраза"],
    metrics: ["Визиты", "Пользователи", "Отказы %", "Глубина", "Время сек"],
  },
  "API Метрики не вернул поисковые фразы.",
)}

### Органические посадочные страницы

${reportOrLimitation(
  organicLandingPages,
  {
    dimensions: ["Посадочная страница"],
    metrics: ["Визиты", "Пользователи", "Отказы %", "Глубина", "Время сек"],
  },
  "API Метрики не вернул органические посадочные страницы.",
)}

### Органика по устройствам

${reportOrLimitation(
  organicDevices,
  {
    dimensions: ["Устройство"],
    metrics: ["Визиты", "Пользователи", "Отказы %", "Глубина", "Время сек"],
  },
  "API Метрики не вернул органику по устройствам.",
)}

## Конверсии

${conversions ? totalsToMarkdown(conversions, conversionMetrics) : "Бизнес-цели не выбраны. Добавьте YANDEX_METRIKA_GOAL_IDS в .env."}

## Ограничения SEO-данных

${seoReportWarnings.length ? seoReportWarnings.map((warning) => `- ${warning}`).join("\n") : "- SEO-отчёты получены без ошибок API."}

## Ограничения данных

- traffic sampled: ${traffic.sampled ? "yes" : "no"}, sample share: ${traffic.sample_share ?? "-"}
- utm sampled: ${utm.sampled ? "yes" : "no"}, sample share: ${utm.sample_share ?? "-"}
- search sampled: ${searchEngines.sampled ? "yes" : "no"}, sample share: ${searchEngines.sample_share ?? "-"}
- search phrases sampled: ${sampledStatus(searchPhrases)}
- organic landing pages sampled: ${sampledStatus(organicLandingPages)}
- organic devices sampled: ${sampledStatus(organicDevices)}
- contains sensitive data: ${containsSensitiveData(traffic, utm, searchEngines, searchPhrases, organicLandingPages, organicDevices) ? "yes" : "no"}
`;
}

function reportOrLimitation(report, tableOptions, limitation) {
  if (!report) return limitation;
  return reportToMarkdownTable(report, tableOptions);
}

function sampledStatus(report) {
  if (!report) return "not available";
  return `${report.sampled ? "yes" : "no"}, sample share: ${report.sample_share ?? "-"}`;
}

function containsSensitiveData(...reports) {
  return reports.some((report) => Boolean(report?.contains_sensitive_data));
}

function buildPrompt(dataSnapshot) {
  return `Ты веб-аналитик, SEO-специалист и маркетолог для руководителя компании.

Проанализируй данные Яндекс.Метрики ниже.

Правила:
- не меняй файлы проекта;
- не запускай дополнительные команды;
- не проси секреты;
- анализируй только данные из снимка, уже отфильтрованные по визитам людей без роботов;
- пиши простым управленческим языком;
- отделяй факты от гипотез;
- если данных недостаточно, прямо напиши, чего не хватает;
- отдельно оцени SEO-срез: органический трафик, поисковые фразы, посадочные страницы и устройства;
- не придумывай ключевые слова или страницы, если Метрика их не вернула;
- дай 3-5 практических SEO/маркетинговых действий на следующую неделю.

Формат ответа:
1. Короткий вывод для руководителя.
2. Что хорошо.
3. Что вызывает риск.
4. SEO-срез: органика, поисковые фразы, посадочные страницы, устройства.
5. Каналы и кампании, на которые обратить внимание.
6. Рекомендации на следующую неделю.
7. Что проверить вручную в Яндекс.Метрике.

${dataSnapshot}`;
}

async function writeObsidianReport({ date1, date2, counter, agentId, runId, status, dataSnapshot, assistantText }) {
  await mkdir(OBSIDIAN_RUN_LOGS_DIR, { recursive: true });

  const reportPath = join(OBSIDIAN_RUN_LOGS_DIR, `${new Date().toISOString().slice(0, 10)} metrika-web-analyst.md`);
  const content = `# Metrika web analyst

## Запуск

- Дата: ${new Date().toISOString()}
- Период: ${date1} — ${date2}
- Счётчик: ${counter.id} — ${counter.name || "-"}
- Сайт: ${counter.site || "-"}
- agentId: ${agentId}
- runId: ${runId}
- status: ${status}

## Вывод агента

${assistantText || "Агент не вернул текстовый вывод."}

## Снимок данных

${dataSnapshot}
`;

  await writeFile(reportPath, content);
  return reportPath;
}
