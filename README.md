# Внутренний голос — Telegram-бот

Анонимный дневник, доступный только в помещении библиотеки.  
Пользователи оставляют записи через Telegram-бота, сообщения публикуются в канал после модерации.

---

## 📦 Состав проекта

- **Python 3.11**
- **aiogram 3**
- **SQLAlchemy + MySQL**
- **Docker + Docker Compose**
- Хранение пользователей и постов в БД

---

## 🚀 Быстрый запуск

1. Установить Docker и Docker Compose  
2. Клонировать проект:

```
git clone https://github.com/your_username/innervoice.git
cd innervoice
```

3. Создать `.env` файл (пример ниже)

```
BOT_TOKEN=your_bot_token
ADMIN_ID=your_admin_id
CHANNEL_ID=-100xxxxxxxxx
GROUP_ID=-100yyyyyyyyy

MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=innervoice
MYSQL_USER=root
MYSQL_PASSWORD=password
```

4. Запустить:

```
docker compose up -d --build
```

---

## 🧱 Структура проекта

```
app/
├── bot.py
├── handlers/
├── services/
├── texts/
└── database/
    ├── models.py
    └── db.py

main.py
config.py
Dockerfile
docker-compose.yml
requirements.txt
.env.example
```

---

## 📓 Что делает бот

- Принимает сообщения от пользователей
- Сохраняет их в базу с указанием автора
- Отправляет сообщение администратору на проверку
- После одобрения публикует пост в канал
- Отвечать можно в группе через команду `/ответить`

---

## 📌 Заметки

- Все сообщения проходят ручную модерацию
- Канал и группа должны быть созданы заранее
- Бот должен быть админом в обоих
- Данные пользователей не видны другим участникам

---

## 🧩 Лицензия

Независимая инициатива. Для некоммерческого использования.
