# Архитектура агентов

Этот документ объясняет, где что лежит в `agent-lab` и как не превращать агентов в black box.

## Главная идея

Каждый агент должен быть понятен как небольшой внутренний продукт: у него есть цель, входные данные, правила, команда запуска, отчёт и критерии качества.

## Роли папок

```text
agent-lab/
├─ agents/          # паспорта агентов: README, prompt, config, checklist
├─ skills/          # знания и правила, которые агент должен применять
├─ lib/             # технические клиенты и общие функции
├─ scripts/         # короткие команды запуска
├─ docs/            # инструкции для человека
├─ data/            # кеши и временные данные
└─ package.json     # список команд npm
```

Рядом с проектом находится Obsidian vault:

```text
Company OS/
├─ Agents/          # карточки агентов для управления
├─ Run Logs/        # отчёты запусков
├─ Decisions/       # решения по архитектуре и правилам
└─ Playbooks/       # регулярные сценарии работы
```

## Поток работы агента

```mermaid
flowchart TD
  Human[Руководитель] --> Obsidian[Obsidian Company OS]
  Obsidian --> AgentCard[Карточка агента]
  AgentCard --> NpmCommand[npm команда]
  NpmCommand --> Script[script запуск]
  Script --> AgentFolder[agents папка]
  Script --> Skill[skills правила]
  Script --> Client[lib API клиент]
  Client --> Api[Внешний API]
  Script --> CursorSdk[Cursor SDK]
  CursorSdk --> Report[Markdown отчёт]
  Report --> RunLogs[Obsidian Run Logs]
```



## Паспорт агента

Каждый агент получает папку:

```text
agents/<agent-name>/
├─ README.md
├─ prompt.md
├─ config.example.json
└─ eval-checklist.md
```

`README.md` отвечает на вопрос «зачем агент нужен».  
`prompt.md` хранит основную инструкцию.  
`config.example.json` показывает, какие параметры и секреты нужны.  
`eval-checklist.md` помогает оценивать качество результата после каждого запуска.

## Что считается хорошим агентом

- Его можно запустить одной командой.
- Он не требует копировать секреты в чат.
- Он пишет отчёт в `Company OS/Run Logs/`.
- Он логирует `agentId`, `runId`, дату, статус и версию prompt.
- У него есть checklist качества.
- Его можно улучшать через изменения `prompt.md`, `SKILL.md` или конфига.

## Цикл улучшения

1. Запустить агента.
2. Открыть отчёт в Obsidian.
3. Проверить отчёт по `eval-checklist.md`.
4. Записать замечания.
5. Изменить prompt, skill или источник данных.
6. Повторить запуск на тех же или сопоставимых данных.
7. Сравнить качество отчётов.

