# Настройка Яндекс.Метрики для агента

Эта инструкция нужна, чтобы агент `metrika-web-analyst` мог читать данные Яндекс.Метрики.

## Что понадобится

- Аккаунт Яндекса с доступом к нужному счётчику Метрики.
- Cursor SDK key в `CURSOR_API_KEY`.
- OAuth token Яндекса с правом только на чтение Метрики.

## 1. Создать OAuth-приложение Яндекса

1. Откройте: [https://oauth.yandex.ru/client/new](https://oauth.yandex.ru/client/new)
2. Название приложения: `Cursor Metrika Agent`.
3. Платформа: `Веб-сервисы`.
4. В доступах выберите только:

```text
metrika:read
```

1. Сохраните приложение и скопируйте `ClientID`.

## 2. Получить OAuth token

Откройте ссылку, заменив `ВАШ_CLIENT_ID`:

```text
https://oauth.yandex.ru/authorize?response_type=token&client_id=ВАШ_CLIENT_ID
```

После разрешения доступа Яндекс откроет страницу с адресом примерно такого вида:

```text
https://oauth.yandex.ru/#access_token=ТОКЕН&token_type=bearer&expires_in=31536000
```

Скопируйте только значение после `access_token=`.

## 3. Добавить токен в `.env`

Откройте локальный файл:

```text
.env
```

Добавьте строки:

```bash
YANDEX_METRIKA_TOKEN=ваш_токен
```

Не вставляйте токен в чат, `.env.example`, README или GitHub.

## 4. Найти счётчик

Запустите:

```bash
npm run metrika:counters
```

Команда покажет доступные счётчики. Выберите нужный ID и добавьте в `.env`:

```bash
YANDEX_METRIKA_COUNTER_ID=12345678
```

## 5. Выбрать бизнес-цели

Первый отчёт можно запустить без целей, но лучше указать цели, которые действительно важны бизнесу: заявка, заказ, звонок, покупка.

Добавьте в `.env`:

```bash
YANDEX_METRIKA_GOAL_IDS=111111,222222
```

## 6. Запустить агента

```bash
npm run agent:metrika
```

Агент создаст Markdown-отчёт в Obsidian:

```text
../Company OS/Run Logs/YYYY-MM-DD metrika-web-analyst.md
```

## Безопасность

- OAuth token действует примерно 1 год.
- Давайте только `metrika:read`, не выдавайте права на запись.
- Если токен случайно попал в чат или GitHub, удалите его в Яндексе и создайте новый.
- Сырые данные и кеш Метрики не коммитятся: они исключены через `.gitignore`.

