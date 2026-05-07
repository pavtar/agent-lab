# agent-lab

Учебный проект для первых запусков Cursor SDK агентов.

## Что внутри

- `scripts/local-repo-summarizer.mjs` - локальный агент, который читает текущий репозиторий и кратко объясняет его структуру.
- `scripts/cloud-readme-pr.mjs` - cloud-агент, который может создать Pull Request с улучшением `README.md`.
- `scripts/metrika-counters.mjs` - проверка доступа к счётчикам Яндекс.Метрики.
- `scripts/metrika-web-analyst.mjs` - агент веб-аналитик/маркетолог по данным Яндекс.Метрики.
- `agents/` - паспорта агентов: цель, prompt, конфиг и checklist качества.
- `skills/` - правила и domain knowledge для агентов.
- `docs/tasks.md` - список учебных задач для агентов.
- `docs/agent-log.md` - журнал запусков агентов.
- `docs/agent-card-template.md` - шаблон карточки агента для Obsidian.
- `docs/metrika-setup.md` - инструкция получения OAuth token Яндекс.Метрики.

## Подготовка

1. Создайте Cursor SDK API key в Cursor Dashboard -> Integrations.
2. Настройте переменную окружения:

```bash
export CURSOR_API_KEY="cursor_..."
```

1. Проверьте скрипты:

```bash
npm run check
```

## Первый локальный запуск

```bash
npm run agent:local
```

Агент получает инструкцию только читать проект и ничего не менять.

## Операционная модель

Главные документы:

```text
docs/agent-architecture.md
docs/sdk-decision-guide.md
docs/agent-roadmap.md
```

Список агентов:

```bash
npm run agents:list
```

Проверка паспорта агента:

```bash
npm run agent:check -- metrika-web-analyst
```

Единый запуск агента, если для него уже есть SDK-команда:

```bash
npm run agent:run -- metrika-web-analyst
npm run agent:run -- repo-summarizer
```

Для остальных агентов сначала используйте их папки в `agents/` как паспорт и prompt для ручной работы в Cursor Agent.

## Первый cloud PR

Сначала опубликуйте этот проект в GitHub, затем задайте URL репозитория:

```bash
export GITHUB_REPO_URL="https://github.com/your-user/agent-lab"
npm run agent:cloud-pr
```

Cloud-агент запустится на отдельной инфраструктуре Cursor и создаст Pull Request для ручной проверки.

## Metrika web analyst

Агент `metrika-web-analyst` анализирует данные Яндекс.Метрики и сохраняет Markdown-отчёт в Obsidian.

Сначала настройте доступ по инструкции:

```text
docs/metrika-setup.md
```

Проверьте, что API token видит ваши счётчики:

```bash
npm run metrika:counters
```

После выбора счётчика и бизнес-целей запустите отчёт:

```bash
npm run agent:metrika
```

Отчёт появится в:

```text
../Company OS/Run Logs/
```

## Правила безопасности

- Не храните `.env`, API keys и токены в репозитории.
- Первые задачи для агентов должны быть про чтение, анализ и документацию.
- Изменения проверяйте через Pull Request перед merge.
- Ведите журнал запусков в `docs/agent-log.md` и Obsidian.

