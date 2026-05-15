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
- `docs/` — инструкции, roadmap, архитектура (`docs/agent-architecture.md`) и журнал запусков.
- `tools/` — внутренние генераторы (сейчас `uplab-slide-generator/` для презентаций).
- `skills/` — методики; у `excel-workbook-generation` также `guide/` и `examples/`.

## Рабочие агенты

### Портфель (`agents/`)

- `toyota-kata-coach` — коуч по Toyota Kata: советы, тренажёр руководителя, weekly coaching, problem improvement, team playbook.
- `metrika-web-analyst` — веб-аналитик/маркетолог по данным Яндекс.Метрики и SEO.
- `process-architect` — описание и проектирование бизнес-процессов через BPM и Value Stream Mapping.
- `brand-presentation-maker` — создание презентаций в фирменном стиле.
- `spreadsheet-maker` — создание управленческих `.xlsx`-таблиц.

### Черновики (`agents/draft/`)

- `meeting-secretary` — протоколы встреч, решения и задачи.
- `business-system-analyst` — BRD, ТЗ и user stories.
- `finance-director` — будущий агент для управленческих финансовых отчётов.
- `repo-summarizer` — обзор структуры репозитория (учебный read-only сценарий).

См. `docs/agent-roadmap.md`.

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

## Глобальные симлинки в Cursor (macOS)

Чтобы вызывать методики и промпты из **любой открытой папки** (в том числе в Agents Window), на машине можно держать симлинки в домашнем каталоге Cursor. Источник правды по-прежнему этот репозиторий: правки делайте в `agent-lab`, симлинки только подхватывают те же файлы.

### `~/.cursor/skills/`

Сюда связаны каталоги из `skills/`, в которых есть `**SKILL.md`** (персональные skills Cursor; каталог `skills-cursor` для встроенных навыков не используйте):

- `business-process-mapping`
- `excel-workbook-generation`
- `toyota-kata-coaching`
- `uplab-presentation-generation`
- `yandex-metrika`

Папка `skills/attribution/` в симлинки не входит — там только учёт внешних источников, без `SKILL.md`.

### `~/.cursor/agent-lab-agents/`

Сюда связаны все папки из `agents/<имя>/` (удобно открывать или перетаскивать в чат `**prompt.md**` по короткому пути, например `~/.cursor/agent-lab-agents/toyota-kata-coach/prompt.md`). Это не skills в терминах Cursor: у агентов в корне паспорта лежит `prompt.md`, а не `SKILL.md`.

### Если перенесли репозиторий

Пересоздайте симлинки на новые абсолютные пути (старые ссылки станут «битыми»).

После изменений в `~/.cursor/skills/` имеет смысл выполнить в Cursor **Reload Window**, чтобы список skills обновился.

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
docs/metrika-setup.md
```

По Яндекс.Метрике и агенту `metrika-web-analyst` см. `docs/metrika-setup.md` (токен, счётчики, `npm run agent:metrika`, вывод в `Company OS/Run Logs/`).

## Первый cloud PR

Сначала опубликуйте этот проект в GitHub, затем задайте URL репозитория:

```bash
export GITHUB_REPO_URL="https://github.com/your-user/agent-lab"
npm run agent:cloud-pr
```

Cloud-агент запустится на отдельной инфраструктуре Cursor и создаст Pull Request для ручной проверки.

## Правила безопасности

- Не храните `.env`, API keys и токены в репозитории.
- Первые задачи для агентов должны быть про чтение, анализ и документацию.
- Изменения проверяйте через Pull Request перед merge.
- Ведите журнал запусков в `docs/agent-log.md` и Obsidian.

