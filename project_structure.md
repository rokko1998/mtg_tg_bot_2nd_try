project/
├── docker-compose.yml
├── docker-compose.test.yml  <-- Конфигурация для тестового окружения
├── Dockerfile
├── .env
├── .gitignore
├── .dockerignore
├── nginx.conf
├── certs/
│   ├── fullchain.pem
│   └── privkey.pem
├── logs/
│   ├── <лог-файлы будут появляться тут>
├── app/
│   ├── __init__.py
│   ├── main.py  <-- код бота на aiogram
│   ├── utils.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── user_router.py
│   │   └── admin_router.py
│   ├── middlewares/
│   │   ├── __init__.py
│   │   └── log_user_actions.py
│   ├── config.py  <-- для хранения настроек
│   ├── logger_conf.py  <-- конфигурация логирования
│   ├── mw.py  <-- middleware подключения
│   ├── celery_config.py  <-- конфигурация Celery
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── redis_utils.py  <-- функции для работы с Redis
│   ├── db/
│   │   ├── __init__.py
│   │   ├── core.py
│   │   └── models.py
├── redis/
│   ├── redis.conf  <-- конфигурация Redis (если нужно)
├── .github/
│   ├── workflows/
│   │   ├── deploy.yml  <-- CI/CD для GitHub Actions
└── requirements.txt
