# Luneria CRM

Внутренняя операционная система агентства Luneria.

## Структура проекта
- `/backend` - FastAPI приложение, SQLAlchemy модели.
- `/frontend` - Next.js приложение, React, Tailwind CSS, shadcn/ui.

## Запуск проекта

### 1. Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Если requirements.txt еще не создан, зависимости устанавливаются вручную.
```

**Применение миграций:**
```bash
alembic upgrade head
```

**Заполнение тестовыми данными (Seed):**
```bash
python seed.py
```

**Запуск сервера:**
```bash
uvicorn app.main:app --reload --port 8000
```
Backend будет доступен по адресу: http://localhost:8000
Документация API: http://localhost:8000/docs

### 2. Frontend
```bash
cd frontend
npm install
```

**Запуск сервера:**
```bash
npm run dev
```
Frontend будет доступен по адресу: http://localhost:3000

---

## Тестовые логины (После выполнения Seed Database)

- **Owner**: `owner@luneria.local` / `password123`
- **Curator**: `curator1@luneria.local` / `password123`
- **Admin**: `admin1@luneria.local` / `password123`
- **Finance**: `finance@luneria.local` / `password123`

## Разработка
Для локального запуска одной командой можно использовать скрипт:
```bash
./run.sh
```
 