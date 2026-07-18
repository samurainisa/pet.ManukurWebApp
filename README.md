# ManikurWebApp (freelance project)

Рабочий MVP для автоматизации маникюрного мастера: клиенты, услуги, расписание, визиты, оплаты и аналитика в одном кабинете.

Стек:
- Backend: Django + DRF (Token auth), PostgreSQL или SQLite для dev
- Frontend: Vue 3 + TypeScript + Tailwind CSS + Vite

## Интерфейс

Кабинет мастера собран вокруг бокового меню: **Дашборд, Клиенты, Услуги, Расписание, Аналитика, График**.

### Вход

Отдельная страница входа для мастера. Логин и пароль, ссылка на регистрацию.

![Вход](frontend/screens/login.png)

### Дашборд

Сводка на сегодня: записи за день и за период, отмены, неявки. Быстрые действия (новая запись, новый клиент, новая услуга), список сегодняшних и ближайших визитов со статусами.

![Дашборд](frontend/screens/main-page.png)

### Услуги

Справочник услуг с длительностью, ценой и статусом. Справа форма создания, у каждой карточки — редактирование и удаление.

![Услуги](frontend/screens/услуги.png)

### Карта клиента

История визитов и оплат по конкретному клиенту: заметки, общая сумма оплат, таблица визитов со статусом и оплатой.

![Карта клиента](frontend/screens/история_клиента.png)

### Аналитика

Период с фильтром по датам. Визиты, отмены, неявки, выручка, топ услуг по записям и выручка по дням в виде столбиков.

![Аналитика](frontend/screens/дешборд.png)

### График работы

Базовый график по дням недели (рабочий день, время начала и конца) и разовые блокировки времени с причиной.

![График работы](frontend/screens/график.png)

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
  - `/login`, `/register`
  - `/dashboard`
  - `/clients`, `/clients/:id`
  - `/services`
  - `/schedule`
  - `/appointments/:id`
  - `/analytics`
  - `/settings/schedule`
- Кабинет клиента (роль `client`):
  - `/client/book`
  - `/client/appointments`
  - `/client/notifications`
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
  users/          # auth API, роли мастер/клиент
  clients/        # клиентская база
  services/       # справочник услуг
  scheduling/     # график, блокировки, записи, публичные слоты
  visits/         # результат визита + фото
  payments/       # учет оплат
  analytics/      # read-only агрегаты
  core/           # интеграционные тесты MVP

frontend/
  src/app         # роутер, провайдеры, App.vue
  src/entities    # сущности (client, service, appointment, ...) с api и store
  src/pages       # страницы мастера и публичной записи
  src/widgets     # app-shell (боковое меню + шапка)
  src/shared      # ui-компоненты, http-клиент, утилиты, типы
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

### 3. Демо-данные (опционально)

Заполнить базу клиентами, записями, визитами и оплатами за месяц:

```bash
cd backend
python manage.py generate_demo_month_data --month 2026-07 --clients 40 --appointments 95
```

Параметры: `--month YYYY-MM`, `--clients`, `--appointments`, `--seed`.

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
- без WebSocket/realtime
- без мульти-мастера и мультифилиальности

## Примечания

- Для медиазагрузок (фото визита) используется локальная папка `backend/media`.
- В dev можно работать на SQLite (если не заданы переменные PostgreSQL).
- Для целевого режима укажите PostgreSQL переменные в `.env` backend.
