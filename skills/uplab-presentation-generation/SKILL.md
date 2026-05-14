---

## name: uplab-presentation-generation
description: Создаёт презентации Uplab в формате Markdown для Uplab Slide Generator и, при наличии PPTX-шаблона, генерирует .pptx. Использовать при создании КП, pitch, докладов, отчётов и фирменных презентаций Uplab.

# Генерация презентаций Uplab

Используй этот skill, когда агент должен подготовить фирменную презентацию Uplab.

## Источник

Рабочая документация и генератор лежат здесь:

```text
vendor/uplab-slide-generator/
```

Перед работой прочитай:

- `AGENT_RULES.md`
- `USAGE.md`
- при необходимости `examples/master_universal.md`

## Workflow

1. Уточни задачу: тип презентации, тема, клиент, аудитория, ключевые тезисы, нужный объём.
2. Проверь, что в папке генератора есть core-пакет: `generate.py`, `requirements.txt`, `AGENT_RULES.md`, `USAGE.md`, `src/`, `templates/`, `assets/`, `examples/master_universal.md`, `examples/content_tkp.md`, `examples/content_finmodel.md`.
3. Если шаблона нет, не обещай финальный `.pptx`: подготовь Markdown-контент и явно напиши, что для генерации нужен шаблон.
4. Сгенерируй `content_<topic>.md` по правилам `AGENT_RULES.md`.
5. Если шаблон доступен, запусти генерацию:

```bash
python generate.py content_<topic>.md -o output_<topic>.pptx
```

1. Проверь результат: файл существует, количество слайдов разумное, первый слайд `cover`, последний `contacts`, нет пустых слайдов.
2. Верни путь к `.md` и `.pptx`, а также список того, что нужно проверить человеку.

## Типы слайдов

Используй доступные типы:

- `cover`
- `toc`
- `section`
- `stats`
- `columns: 2`
- `columns: 3`
- `steps`
- `table`
- `table: sidebar`
- `case`
- `timeline`
- `grid: 3`
- `highlight`
- `quote`
- `text`
- `image`
- `team`
- `contacts`

## Правила качества

- `cover` всегда первый.
- `contacts` всегда последний.
- Слайды должны быть короткими: это презентация, не документ.
- Заголовки: 3-7 слов.
- Если контент не помещается, разбивай на несколько слайдов.
- Добавляй `section` перед логическими блоками.
- Для 2-3 параллельных блоков используй `columns`, а не длинный `text`.
- Для чисел и KPI используй `stats`.
- Для бюджета, сроков и сравнений используй `table`.
- Для хронологии используй `timeline`.
- Для процесса используй `steps`.

## Подробные правила

См. [reference.md](reference.md).