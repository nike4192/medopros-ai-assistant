# Medopros MVP

Медицинский ассистент для автоматизации опроса пациентов.

## Функционал

- Запись аудиосообщений пациентов.
- Автоматическая транскрибация (ASR): GigaAM через внешний HTTP-сервис
  (`GIGAAM_API_URL`); модель в процессе medopros не загружается. Whisper через
  OpenRouter — запасной движок (`ASR_ENGINE=openrouter` включает его как основной).
- Анализ текста с помощью LLM для извлечения жалоб и симптомов.
- Интеграция с Telegram для уведомлений о новых заявках.
- Админ-панель для просмотра истории записей.

## Установка и запуск

### Локально

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Настройте переменные окружения:
   Скопируйте `.env.example` в `.env` и заполните необходимые ключи:
   ```bash
   cp .env.example .env
   ```

3. Запустите сервер:
   ```bash
   python backend.py
   ```
   Приложение будет доступно по адресу `http://localhost:8001`.

### Docker

Запуск через Docker Compose:
```bash
docker-compose up -d --build
```

## Структура проекта

- `backend.py` - Основной API сервер (FastAPI).
- `index.html` - Лендинг.
- `app/` - Фронтенд приложения ассистента.
- `assets/` - Статические файлы (картинки, стили).
- `recordings/` - Директория для хранения аудиозаписей и JSON данных (игнорируется в Git).

## ASR

По умолчанию распознавание идёт через внешний HTTP-сервис GigaAM — сам сервис
medopros модель не загружает. Настройки (`server/config.py`, переменные окружения):

| Переменная | По умолчанию | Смысл |
|---|---|---|
| `ASR_ENGINE` | `gigaam_api` | `gigaam_api` или `openrouter` (прежний Whisper) |
| `GIGAAM_API_URL` | — | URL внешнего ASR-сервиса (обязателен для `gigaam_api`) |
| `GIGAAM_API_KEY` | — | значение заголовка `X-API-Key` (если сервис требует) |
| `GIGAAM_API_FIELD` | `file` | имя multipart-поля с аудио |
| `GIGAAM_API_TIMEOUT` | `300` | таймаут запроса, с |
| `ASR_FALLBACK_OPENROUTER` | `1` | откат на Whisper, если GigaAM недоступен |

Контракт внешнего сервиса:

```http
POST $GIGAAM_API_URL
X-API-Key: $GIGAAM_API_KEY        # если задан
Content-Type: multipart/form-data

file=@audio.wav
```

Ответ — JSON с одним из полей `text`, `result` или `transcript`
(либо `text/plain` с готовым текстом):

```json
{"text": "Болит нога, боль усиливается при ходьбе"}
```

## Безопасность

Все секретные ключи должны храниться в файле `.env`. Никогда не пушьте `.env` в репозиторий! Для этого уже настроен `.gitignore`.
