# agent-lab

Учебный проект для первых запусков Cursor SDK агентов.

## Что внутри

- `scripts/local-repo-summarizer.mjs` - локальный агент, который читает текущий репозиторий и кратко объясняет его структуру.
- `scripts/cloud-readme-pr.mjs` - cloud-агент, который может создать Pull Request с улучшением `README.md`.
- `docs/tasks.md` - список учебных задач для агентов.
- `docs/agent-log.md` - журнал запусков агентов.
- `docs/agent-card-template.md` - шаблон карточки агента для Obsidian.

## Подготовка

1. Создайте Cursor SDK API key в Cursor Dashboard -> Integrations.
2. Настройте переменную окружения:

```bash
export CURSOR_API_KEY="cursor_..."
```

3. Проверьте скрипты:

```bash
npm run check
```

## Первый локальный запуск

```bash
npm run agent:local
```

Агент получает инструкцию только читать проект и ничего не менять.

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
