import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";

const API_BASE_URL = "https://api-metrika.yandex.net";
const DEFAULT_LANG = "ru";

export class MetrikaConfigError extends Error {}
export class MetrikaApiError extends Error {}

export function requireEnv(name) {
  const value = process.env[name]?.trim();

  if (!value || value.includes("your_") || value.includes("вставьте")) {
    throw new MetrikaConfigError(`Не настроена переменная ${name}. Проверьте .env.`);
  }

  return value;
}

export function getDateRange(days = 30) {
  const date2 = new Date();
  date2.setDate(date2.getDate() - 1);

  const date1 = new Date(date2);
  date1.setDate(date1.getDate() - days + 1);

  return {
    date1: toIsoDate(date1),
    date2: toIsoDate(date2),
  };
}

export function parseGoalIds(value = "") {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export async function listCounters({ token, search }) {
  const payload = await metrikaRequestJson({
    token,
    path: "/management/v1/counters",
    params: { lang: DEFAULT_LANG, per_page: "1000" },
  });

  const counters = (payload.counters || []).map((counter) => ({
    id: counter.id,
    name: counter.name,
    site: counter.site || counter.site2?.site || "",
    status: counter.code_status || counter.status || "",
  }));

  if (!search) return counters;

  const query = search.toLowerCase();
  return counters.filter((counter) =>
    [counter.id, counter.name, counter.site, counter.status]
      .join(" ")
      .toLowerCase()
      .includes(query),
  );
}

export async function getCounterInfo({ token, counterId }) {
  const payload = await metrikaRequestJson({
    token,
    path: `/management/v1/counter/${counterId}`,
    params: { lang: DEFAULT_LANG },
  });

  const counter = payload.counter || {};
  return {
    id: counter.id,
    name: counter.name,
    site: counter.site || counter.site2?.site || "",
    status: counter.code_status || counter.status || "",
    timezone: counter.time_zone_name || counter.time_zone || "",
    currency: counter.currency || "",
  };
}

export async function listGoals({ token, counterId }) {
  const payload = await metrikaRequestJson({
    token,
    path: `/management/v1/counter/${counterId}/goals`,
    params: { lang: DEFAULT_LANG },
  });

  return (payload.goals || []).map((goal) => ({
    id: goal.id,
    name: goal.name,
    type: goal.type,
    isRetargeting: Boolean(goal.is_retargeting),
  }));
}

export async function fetchReport({
  token,
  counterId,
  date1,
  date2,
  metrics,
  dimensions,
  filters,
  sort,
  limit = 20,
  cacheName,
}) {
  const params = {
    ids: String(counterId),
    date1,
    date2,
    metrics,
    accuracy: "1",
    lang: DEFAULT_LANG,
    limit: String(limit),
  };

  if (dimensions) params.dimensions = dimensions;
  if (filters) params.filters = filters;
  if (sort) params.sort = sort;

  const cacheFile = cacheName
    ? join("data", "metrika", "cache", `${cacheName}-${hashParams(params)}.json`)
    : undefined;

  if (cacheFile && date2 !== toIsoDate(new Date())) {
    const cached = await readJsonIfExists(cacheFile);
    if (cached) return { ...cached, fromCache: true };
  }

  const payload = await metrikaRequestJson({
    token,
    path: "/stat/v1/data",
    params,
  });

  if (cacheFile) await writeJson(cacheFile, payload);

  return { ...payload, fromCache: false };
}

export function formatCounters(counters) {
  if (!counters.length) return "Счётчики не найдены.";

  return counters
    .map((counter) => `${counter.id}\t${counter.name || "-"}\t${counter.site || "-"}\t${counter.status || "-"}`)
    .join("\n");
}

export function reportToMarkdownTable(report, { dimensions = [], metrics = [] }) {
  const rows = report.data || [];

  if (!rows.length) return "Нет данных.";

  const headers = [...dimensions, ...metrics];
  const table = [
    `| ${headers.join(" | ")} |`,
    `| ${headers.map(() => "---").join(" | ")} |`,
  ];

  for (const row of rows) {
    const dimensionValues = (row.dimensions || []).map((dimension) => dimension.name || dimension.id || "-");
    const metricValues = (row.metrics || []).map(formatMetric);
    table.push(`| ${[...dimensionValues, ...metricValues].join(" | ")} |`);
  }

  return table.join("\n");
}

export function totalsToMarkdown(report, metrics) {
  const totals = report.totals || [];

  if (!totals.length) return "Нет итоговых метрик.";

  return metrics.map((metric, index) => `- ${metric}: ${formatMetric(totals[index])}`).join("\n");
}

async function metrikaRequestJson({ token, path, params = {} }) {
  const url = new URL(path, API_BASE_URL);

  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") url.searchParams.set(key, value);
  }

  const response = await fetch(url, {
    headers: {
      Authorization: `OAuth ${token}`,
      Accept: "application/json",
    },
  });

  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};

  if (!response.ok) {
    const message = payload.message || payload.errors?.[0]?.message || response.statusText;
    throw new MetrikaApiError(`Yandex Metrika API ${response.status}: ${message}`);
  }

  return payload;
}

async function readJsonIfExists(filePath) {
  try {
    return JSON.parse(await readFile(filePath, "utf8"));
  } catch (error) {
    if (error.code === "ENOENT") return undefined;
    throw error;
  }
}

async function writeJson(filePath, payload) {
  await mkdir(dirname(filePath), { recursive: true });
  await writeFile(filePath, JSON.stringify(payload, null, 2));
}

function hashParams(params) {
  return createHash("sha256").update(JSON.stringify(params)).digest("hex").slice(0, 16);
}

function toIsoDate(date) {
  return date.toISOString().slice(0, 10);
}

function formatMetric(value) {
  if (value === undefined || value === null) return "-";
  if (Number.isInteger(value)) return String(value);
  if (typeof value === "number") return value.toFixed(2);
  return String(value);
}
