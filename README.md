# agent-lab

Рабочая папка для агентов компании: паспорта агентов, skills, база знаний, SDK-скрипты и инструкции по запуску.

## С чего начинать

Если вы хотите просто воспользоваться агентом через Cursor, начните с этого файла:

```text
docs/how-to-use-agents.md
```

Это короткая инструкция без терминала: как выбрать агента, выбрать сценарий и вставить готовый prompt в Cursor Agent.

Если вы хотите понять, какие агенты уже есть и что развиваем дальше, откройте:

```text
docs/agent-roadmap.md
```

Если вы хотите разобраться в архитектуре: где agents, skills, knowledge и SDK, откройте:

```text
docs/agent-architecture.md
docs/agents-vs-skills.md
docs/sdk-decision-guide.md
```

## Что внутри

- `agents/` — паспорта агентов: цель, prompt, конфиг и checklist качества.
- `skills/` — методики и правила, по которым работают агенты.
- `knowledge/` — подробная база знаний и исходные материалы для агентов.
- `scripts/` — SDK-скрипты и технические команды запуска.
- `lib/` — общие технические модули для SDK и API.
- `docs/` — инструкции, roadmap, архитектура и журнал запусков.
- `vendor/` — локальные копии внешних инструментов, которые нужны агентам.

## Рабочие агенты

- `toyota-kata-coach` — коуч по Toyota Kata: советы, тренажёр руководителя, weekly coaching, problem improvement, team playbook.
- `metrika-web-analyst` — веб-аналитик/маркетолог по данным Яндекс.Метрики и SEO.
- `process-architect` — описание и проектирование бизнес-процессов через BPM и Value Stream Mapping.
- `brand-presentation-maker` — создание презентаций в фирменном стиле.
- `spreadsheet-maker` — создание управленческих `.xlsx`-таблиц.
- `meeting-secretary` — протоколы встреч, решения и задачи.
- `business-system-analyst` — BRD, ТЗ и user stories.
- `finance-director` — будущий агент для управленческих финансовых отчётов.

## Как выбрать способ запуска

Используйте Cursor Agent в интерфейсе, если задача интерактивная или разовая:

```text
спросить совет
провести тренировку
подготовить черновик
разобрать проблему
```

Используйте Cursor SDK, если нужен повторяемый процесс:

```text
регулярный отчёт
данные из API
запись в Obsidian
логирование запусков
одинаковый запуск каждую неделю
```

## Команды для SDK и проверки

Эти команды нужны не для обычного разговора с агентом, а для технической проверки и автоматизированных запусков.

Проверить проект:

```bash
npm run check
```

Список агентов:

```bash
npm run agents:list
```

Проверка паспорта агента:

```bash
npm run agent:check -- toyota-kata-coach
```

Единый запуск агента, если для него уже есть SDK-команда:

```bash
npm run agent:run -- metrika-web-analyst
npm run agent:run -- repo-summarizer
```

## Подготовка SDK

1. Создайте Cursor SDK API key в Cursor Dashboard -> Integrations.
2. Настройте переменную окружения:

```bash
export CURSOR_API_KEY="cursor_..."
```

## Учебные SDK-запуски

```bash
npm run agent:local
```

Агент получает инструкцию только читать проект и ничего не менять.

## Операционная модель

Главные документы:

```text
docs/how-to-use-agents.md
docs/agent-architecture.md
docs/agents-vs-skills.md
docs/sdk-decision-guide.md
docs/agent-roadmap.md
```

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

