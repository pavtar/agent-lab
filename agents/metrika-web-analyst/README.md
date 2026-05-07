# metrika-web-analyst

Еженедельный веб-аналитик и SEO-маркетолог по данным Яндекс.Метрики.

## Задача

Собрать данные по трафику, источникам, UTM, поисковым системам и конверсиям, затем сохранить управленческий отчёт в Obsidian.

## Когда нужен SDK

SDK нужен, потому что агент работает регулярно, получает данные из API и должен сохранять отчёт с `agentId`, `runId`, периодом и ограничениями данных.

## Команды

```bash
npm run metrika:counters
npm run agent:metrika
npm run agent:run -- metrika-web-analyst
```

## Входные данные

- `CURSOR_API_KEY`
- `YANDEX_METRIKA_TOKEN`
- `YANDEX_METRIKA_COUNTER_ID`
- `YANDEX_METRIKA_GOAL_IDS`

## Выход

Markdown-отчёт в `../Company OS/Run Logs/`.
