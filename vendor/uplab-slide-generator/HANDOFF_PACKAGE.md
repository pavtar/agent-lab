# Анонс для чата

Коллеги, передаю актуальный пакет генератора презентаций Uplab. Внутри один основной мастер контента (`examples/master_universal.md`) и рабочий скрипт генерации в `.pptx`. Временные файлы и тестовые генерации не входят в рабочий пакет.

## Что передаем пользователям

Передавать как основной рабочий пакет:

- `generate.py`
- `requirements.txt`
- `USAGE.md`
- `AGENT_RULES.md`
- `src/`
- `templates/`
- `assets/`
- `examples/master_universal.md`
- `examples/content_tkp.md`
- `examples/content_finmodel.md`
- `sample_presentations/` (витрина качества: готовые примеры `.pptx`)

## Что не входит в рабочий пакет

- временные тестовые генерации;
- устаревшие пресеты;
- любые локальные служебные папки/материалы вне core-пакета.

## Быстрый старт для пользователя

```bash
pip install -r requirements.txt
python generate.py examples/master_universal.md -o output_universal.pptx
```

## Примеры готовых презентаций

Перед установкой можно открыть и посмотреть качество в папке `sample_presentations/`:

- `sample_presentations/finmodel_demo.pptx`
- `sample_presentations/chint_kp_demo.pptx`
- `sample_presentations/output_q1_2026_commercial_report.pptx`

## Принцип работы

- Визуальный шаблон: `templates/Шаблон для презентации.pptx`
- Контент по умолчанию: `examples/master_universal.md`
- При необходимости пользователь создает свой файл: `examples/content_<topic>.md`

