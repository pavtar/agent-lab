# brand-presentation-maker

Создатель презентаций в фирменном стиле.

## Задача

На основе темы, структуры и бренд-документации подготовить фирменную презентацию Uplab: Markdown-контент для генератора и, при наличии PPTX-шаблона, готовый `.pptx`.

## Skills

- `skills/uplab-presentation-generation/SKILL.md` — методика генерации презентаций Uplab.

## Когда нужен SDK

Для первой версии SDK не нужен: агент запускается вручную через Cursor Agent и работает с локальной копией генератора внутри проекта.

SDK понадобится позже, если презентации нужно создавать регулярно, по шаблонам, пакетно или одной командой.

## Первый результат

Markdown-файл `content_<topic>.md` и, если доступен PPTX-шаблон, файл `output_<topic>.pptx`.

## Проверенная команда

Из папки `vendor/uplab-slide-generator/`:

```bash
python3 generate.py examples/master_universal.md -o ../../outputs/brand-presentation-maker/output_universal_test.pptx
```

Проверочный результат: презентация на 14 слайдов создаётся успешно.

## Входные данные

- Папка с генератором и документацией: `vendor/uplab-slide-generator/`.
- Skill: `skills/uplab-presentation-generation/SKILL.md`.
- Тема презентации.
- Аудитория.
- Цель выступления.

## Важное ограничение

Перед обещанием `.pptx` агент должен проверить наличие core-пакета генератора: `generate.py`, `requirements.txt`, `AGENT_RULES.md`, `USAGE.md`, `src/`, `templates/`, `assets/`, `examples/` и `templates/Шаблон для презентации.pptx`.

В текущей локальной папке шаблон найден:

```text
vendor/uplab-slide-generator/templates/Шаблон для презентации.pptx
```

Если при переносе на другой компьютер шаблона нет, агент готовит Markdown-контент и фиксирует, что для финальной генерации нужен PPTX-шаблон.