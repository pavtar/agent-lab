# Справочник по презентациям Uplab

Источник:

```text
tools/uplab-slide-generator/
```

## Основные файлы

Перед рабочим запуском проверь, что core-пакет генератора содержит:

- `AGENT_RULES.md` — главные правила для AI-агента.
- `USAGE.md` — пользовательская инструкция и команды.
- `generate.py` — CLI-генератор `.pptx`.
- `requirements.txt` — зависимости Python.
- `src/` — движок генерации.
- `templates/` — PPTX-шаблон.
- `assets/` — логотипы и иконки.
- `examples/master_universal.md` — универсальный мастер контента.
- `examples/content_tkp.md` — пример ТКП.
- `examples/content_finmodel.md` — пример презентации по финмодели.
- `templates/Шаблон для презентации.pptx` — ожидаемый PPTX-шаблон.
- `sample_presentations/` — витрина качества с готовыми `.pptx`.

## Быстрая проверка пакета

Из папки генератора:

```bash
pip install -r requirements.txt
python generate.py examples/master_universal.md -o output_universal.pptx
```

В `agent-lab` проверенная команда для внутренней копии:

```bash
cd tools/uplab-slide-generator
python3 generate.py examples/master_universal.md -o ../../outputs/brand-presentation-maker/output_universal_test.pptx
```

Ожидаемые примеры качества:

- `sample_presentations/finmodel_demo.pptx`
- `sample_presentations/chint_kp_demo.pptx`
- `sample_presentations/output_q1_2026_commercial_report.pptx`

## Формат Markdown

Frontmatter:

```yaml
---
template: templates/Шаблон для презентации.pptx
output: result.pptx
breadcrumb: "Uplab × Название клиента"
---
```

Каждый слайд:

```markdown
# slide_type
## Заголовок слайда
Содержимое
<!-- note: Заметка для докладчика -->
```

## Типовая структура ТКП

1. `cover` — название проекта.
2. `toc` — содержание, если нужно.
3. `stats` — Uplab в цифрах.
4. `section` — цели и задачи.
5. `columns: 2` — цели + задачи.
6. `section` — архитектура / решение.
7. `text` или `columns` — описание решения.
8. `table` — технологический стек.
9. `section` — бюджет и сроки.
10. `table: sidebar` — стоимость и итоговые параметры.
11. `timeline` — график реализации.
12. `steps` — процесс работы.
13. `section` — кейсы.
14. `case` — 2-4 кейса.
15. `grid: 3` — подход или преимущества.
16. `team` — команда, если нужно.
17. `contacts` — контакты.

## Ограничения контента

- `text`: до 8 строк или 6 буллетов.
- `columns`: до 5 строк на колонку.
- `stats`: до 6 метрик.
- `steps`: до 4 шагов.
- `table`: до 8 строк данных.
- `timeline`: до 6 этапов.
- `grid`: до 6 карточек.
- `case`: 1 кейс на слайд, до 2 метрик.
- `highlight`: 1 число и до 2 строк пояснения.
- `quote`: 1 цитата и автор.

Если контент не помещается, разбей его на 2 слайда.

## Контакты Uplab

```markdown
# contacts
## Москва

**Email:** info@uplab.ru
**Phone:** +7 499 653 78 83
**City:** Москва
**Address:** 127055, ул. Новослободская, д. 61, стр. 2
**Site:** www.uplab.ru
```

## Проверка

После генерации проверь:

- файл `.md` создан;
- если шаблон доступен, файл `.pptx` создан;
- первый слайд `cover`;
- последний слайд `contacts`;
- есть `section` перед логическими блоками;
- нет пустых слайдов;
- таблицы читаемы;
- типы слайдов разнообразны;
- указано, что человеку нужно проверить вручную.

