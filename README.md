# 🏫 School Support CRM

Минималистичная CRM система для службы поддержки школы.

## Стек технологий

- **Backend**: FastAPI (Python)
- **Database**: SQLite + SQLModel (ORM)
- **Frontend**: HTML + Jinja2 Templates + HTMX + Tailwind CSS
- **Server**: Uvicorn

## Функционал (MVP)

### Заявки (Tickets)
- Создание, просмотр, редактирование, удаление заявок
- Приоритеты: Low, Medium, High
- Статусы: Open, In Progress, Resolved, Closed
- Категории заявок
- Комментарии к заявкам

### Пользователи (Users)
- Роли: User, Support, Admin
- История активности

### Категории (Categories)
- Группировка заявок по категориям
- Описание категорий

## Структура проекта

```
/workspace
├── main.py                 # Точка входа приложения
├── app/
│   ├── models/
│   │   └── db.py          # Модели базы данных
│   ├── routes/
│   │   ├── tickets.py     # API маршруты для заявок
│   │   ├── users.py       # API маршруты для пользователей
│   │   ├── categories.py  # API маршруты для категорий
│   │   └── comments.py    # API маршруты для комментариев
│   ├── schemas/
│   │   └── schemas.py     # Pydantic схемы
│   ├── templates/         # HTML шаблоны
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── tickets.html
│   │   ├── ticket_detail.html
│   │   ├── ticket_form.html
│   │   └── categories.html
│   └── database.py        # Настройки БД
├── school_crm.db          # SQLite база данных
└── README.md
```

## Запуск

```bash
# Установка зависимостей
pip install fastapi uvicorn sqlmodel jinja2 python-multipart aiosqlite

# Запуск сервера
python main.py
```

Сервер запустится на http://localhost:8000

## API Endpoints

### Tickets
- `GET /api/tickets/` - Список всех заявок
- `GET /api/tickets/{id}` - Детали заявки
- `POST /api/tickets/` - Создать заявку
- `PATCH /api/tickets/{id}` - Обновить заявку
- `DELETE /api/tickets/{id}` - Удалить заявку

### Users
- `GET /api/users/` - Список пользователей
- `GET /api/users/{id}` - Детали пользователя
- `POST /api/users/` - Создать пользователя

### Categories
- `GET /api/categories/` - Список категорий
- `GET /api/categories/{id}` - Детали категории
- `POST /api/categories/` - Создать категорию

### Comments
- `GET /api/comments/ticket/{ticket_id}` - Комментарии к заявке
- `POST /api/comments/` - Добавить комментарий

## Web Routes

- `/` - Dashboard (статистика и последние заявки)
- `/tickets` - Список всех заявок
- `/tickets/new` - Создание новой заявки
- `/tickets/{id}` - Детали заявки
- `/tickets/{id}/edit` - Редактирование заявки
- `/categories` - Список категорий

## Начальные данные

При первом запуске создаются:
- 3 пользователя (Admin, Support Team, John Teacher)
- 3 категории (Technical Issues, Facilities, Academic Support)
- 1 тестовая заявка

## Особенности

- Минималистичный дизайн с использованием Tailwind CSS
- Динамические обновления через HTMX (без перезагрузки страниц)
- RESTful API для интеграции
- Адаптивный интерфейс
