# ManikurWebApp

Простой рабочий MVP для автоматизации маникюрного сервиса.

Стек:
- Backend: Django + DRF + PostgreSQL
- Frontend: Vue 3 + TypeScript + Tailwind CSS + Vite

## Что реализовано

### Backend
- Авторизация мастера: login/register/logout/me (Token auth)
- Клиенты: список, поиск, создание, редактирование, история визитов
- Услуги: список, создание, редактирование, активация/деактивация
- Расписание:
  - календарь день/неделя
  - создание записи вручную
  - перенос, отмена, неявка
  - проверка пересечений слотов
  - рабочие правила по дням недели
  - разовые блокировки времени
- Публичная запись:
  - список активных услуг
  - свободные слоты
  - создание записи без авторизации
  - honeypot-поле `website` против простого спама
- Визит:
  - фиксация результата
  - загрузка/удаление фото результата
- Оплата:
  - фиксация суммы, способа, статуса
  - связь 1:1 с записью
- Аналитика:
  - summary по визитам/отменам/неявкам/выручке
  - популярные услуги
  - повторные визиты
  - выручка по дням
- Swagger/OpenAPI: `/api/docs/swagger/`, `/api/docs/redoc/`

### Frontend
- Публичные страницы:
  - `/book`
  - `/book/success`
- Приватные страницы мастера:
  - `/login`
  - `/dashboard`
  - `/clients`
  - `/clients/:id`
  - `/services`
  - `/schedule`
  - `/appointments/:id`
  - `/analytics`
  - `/settings/schedule`
- В формах и списках:
  - loading states
  - error states
  - empty states
  - disabled submit во время отправки
  - success feedback

## Архитектура

```text
backend/
  config/         # settings, urls, api router
  users/          # auth API
  clients/        # клиентская база
  services/       # справочник услуг
  scheduling/     # график, блокировки, записи, публичные слоты
  visits/         # результат визита + фото
  payments/       # учет оплат
  analytics/      # read-only агрегаты
  core/           # интеграционные тесты MVP

frontend/
  src/api         # typed API client + entity API
  src/types       # DTO типы
  src/router      # маршруты и auth guard
  src/components  # shell и UI блоки
  src/pages       # страницы мастера и публичной записи
  src/test        # frontend test setup
```

## Быстрый запуск (локально)

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py create_master_demo
python manage.py runserver
```

Backend по умолчанию: `http://localhost:8000`

Демо-данные мастера:
- `username`: `master`
- `password`: `master12345`

### 2. Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend по умолчанию: `http://localhost:5173`

## Docker (опционально)

```bash
docker compose up --build
```

При старте backend автоматически:
- ждет доступности PostgreSQL
- выполняет `python manage.py migrate`
- выполняет `python manage.py create_master_demo`
- запускает сервер

Если контейнер уже был запущен до этого фикса, выполните один раз:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py create_master_demo
```

Сервисы:
- backend: `http://localhost:8000`
- frontend: `http://localhost:5173`
- db: PostgreSQL `localhost:5432`

## Переменные окружения

См. файлы:
- `backend/.env.example`
- `frontend/.env.example`
- корневой `.env.example` (сводный)

## API (базовый префикс)

`/api/v1/`

Ключевые endpoint'ы:
- Auth: `/auth/login/`, `/auth/register/`, `/auth/logout/`, `/auth/me/`
- Clients: `/clients/`, `/clients/{id}/`, `/clients/{id}/history/`
- Services: `/services/`, `/services/{id}/`
- Appointments:
  - `/appointments/`, `/appointments/{id}/`
  - `/appointments/{id}/cancel/`
  - `/appointments/{id}/reschedule/`
  - `/appointments/{id}/mark-no-show/`
  - `/calendar/day/`, `/calendar/week/`, `/available-slots/`
- Public:
  - `/public/services/`
  - `/public/available-slots/`
  - `/public/bookings/`
- Visit:
  - `/appointments/{id}/result/`
  - `/appointments/{id}/photos/`
  - `/appointments/{id}/photos/{photo_id}/`
- Payment:
  - `/appointments/{id}/payment/`
- Analytics:
  - `/analytics/summary/`
  - `/analytics/services/`
  - `/analytics/visits/`
  - `/analytics/revenue/`

## Тесты

### Backend

```bash
cd backend
python manage.py test
```

Покрыты критичные сценарии:
- логин мастера
- создание клиента/услуги
- создание записи на свободный слот
- запрет пересечения
- перенос/отмена/неявка
- фиксация результата визита
- фиксация оплаты
- публичная запись
- поиск клиентов

### Frontend

```bash
cd frontend
npm run test
```

Smoke/component tests:
- `LoginPage`
- `PublicBookingPage`

## Ограничения MVP (выполнено)

- без PWA / service worker / offline
- без SMS
- без email-уведомлений
- без онлайн-оплаты
- без client auth/личного кабинета
- без WebSocket/realtime
- без мульти-мастера и мультифилиальности

## Примечания

- Для медиазагрузок (фото визита) используется локальная папка `backend/media`.
- В dev можно работать на SQLite (если не заданы переменные PostgreSQL).
- Для целевого режима укажите PostgreSQL переменные в `.env` backend.
