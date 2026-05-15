# Skills

Skills — это знания и правила, которые агент должен применять при выполнении задачи.

## Типы skills

## 1. Проектные skills

Хранятся в этом репозитории:

```text
skills/<skill-name>/SKILL.md
```

Используйте их, если skill нужен только для `agent-lab` или связан с конкретными агентами компании.

Пример:

```text
skills/yandex-metrika/SKILL.md
skills/excel-workbook-generation/SKILL.md
skills/uplab-presentation-generation/SKILL.md
```

## 2. Внешние skills

Если skill взят из внешнего репозитория, храните источник и адаптацию отдельно:

```text
skills/attribution/
```

Не смешивайте внешний оригинал и свои правила без пояснения.

## 3. Личные Cursor skills

Если skill должен быть доступен во всех проектах, его можно вынести в:

```text
~/.cursor/skills/<skill-name>/SKILL.md
```

Не создавайте и не меняйте skills в:

```text
~/.cursor/skills-cursor/
```

Это служебная папка Cursor.

## Правило

Сначала делайте skill проектным. Если он полезен во многих проектах, переносите копию в личные skills.