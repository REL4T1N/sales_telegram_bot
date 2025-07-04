```bash
sales_bot/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── alembic/  # (опционально, для миграций)
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── src/
│   ├── main.py            # Точка входа
│   ├── config.py          # Конфигурация приложения
│   ├── bot/               # Основной бот и диспетчер
│   │   ├── __init__.py
│   │   ├── bot.py         # Инициализация бота
│   │   └── dispatcher.py  # Инициализация диспетчера
│   ├── handlers/          # Обработчики
│   │   ├── __init__.py
│   │   ├── common.py      # Общие хендлеры (start, help и т.д.)
│   │   ├── admin.py       # Админские команды
│   │   └── ...           # Другие группы хендлеров
│   ├── middlewares/       # Мидлвари
│   │   ├── __init__.py
│   │   └── database.py    # Мидлварь для инжекта сессии БД
│   ├── database/          # Работа с БД
│   │   ├── __init__.py
│   │   ├── models.py      # ORM модели
│   │   ├── repository/    # Паттерн Repository
│   │   │   ├── __init__.py
│   │   │   ├── user.py    # Репозиторий для пользователей
│   │   │   └── ...        # Другие репозитории
│   │   └── session.py     # Async session maker
│   ├── schemas/           # Pydantic схемы
│   │   ├── __init__.py
│   │   ├── user.py        # Схемы для пользователя
│   │   └── ...           # Другие схемы
│   ├── services/          # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── ...           # Другие сервисы
│   ├── utils/             # Вспомогательные утилиты
│   │   ├── __init__.py
│   │   ├── logger.py      # Логгер
│   │   └── ...           # Другие утилиты
│   └── keyboards/         # Клавиатуры (опционально)
│       ├── __init__.py
│       ├── builders.py     # Билдеры клавиатур
│       └── ...           # Разметки клавиатур
└── tests/                 # Тесты
    ├── __init__.py
    ├── conftest.py
    └── ...               # Модульные тесты
```
