# CargoGo — ЛР5 (Django, вариант 6 «Грузоперевозки»)

Веб-сайт компании, занимающейся грузоперевозками автотранспортом, реализованный
на Django 4.2 (вариант 6 индивидуального задания).

## Что внутри

| Требование ЛР5 | Реализация |
| --- | --- |
| Главная с последней новостью | `main/views.py::home` + `templates/main/home.html` |
| О компании | `main/views.py::about` + модель `CompanyInfo` |
| Новости (с картинкой, CRUD) | `main/views.py::news_*` |
| Словарь терминов / FAQ | `main/views.py::faq_list` + модель `FAQ` |
| Контакты с фото | `main/views.py::contacts_list` + модель `Contact` |
| Политика конфиденциальности | пустая страница `main/privacy.html` |
| Вакансии | `main/views.py::vacancies_*` + CRUD |
| Отзывы с формой и оценкой | `main/views.py::review_*` |
| Промокоды и купоны (действующие/архив) | `main/views.py::promocodes_*` |
| OneToOne / ForeignKey / ManyToMany | `Driver.user` (OneToOne), `Order.client` (FK), `Service.suitable_cargo` (M2M) и др. |
| CRUD во фронте через FBV | все CRUD-вьюшки — function-based |
| Admin-панель со всеми моделями | `*/admin.py`, инлайны `OrderInline` |
| Аутентификация / регистрация | `users/views.py` + `django.contrib.auth.views.LoginView` |
| Разграничение доступа | `@login_required`, `@user_passes_test(_is_superuser)`, проверки в шаблонах |
| 2+ внешних API | `quotable.io` (цитаты) + `open.er-api.com` (валюты) — на главной |
| Регулярные выражения в URL | все URLconf используют `re_path(r'…')` |
| Статистика (среднее, медиана, мода) | `cargo/views.py::statistics_view` |
| Тайм-зона пользователя + UTC | `users/middleware.py::TimezoneMiddleware`, `main/context_processors.py` |
| Текстовый календарь | `main/context_processors.py` (модуль `calendar.TextCalendar`) |
| Формат даты `DD/MM/YYYY` | фильтр `\|date:"d/m/Y"` во всех шаблонах |
| Телефон `+375 (29) XXX-XX-XX` | `users/validators.py::validate_phone` |
| Возраст 18+ | `users/validators.py::validate_age_adult` |
| Диаграмма Python | `main/services.py::render_chart_png_base64` (matplotlib) |
| Поиск и сортировка | `?q=` и `?sort=` параметры на всех list-страницах |
| Тесты | `*/tests.py` — модели, формы, view, доступ |
| Логирование с уровнями из конфига | `LOG_LEVEL` env-переменная, RotatingFileHandler |
| Серверная + клиентская валидация | `clean_*` + HTML `pattern`/`type=date` |
| SQLite локально / PostgreSQL в проде | через `USE_POSTGRES` |
| Dockerfile + docker-compose | в корне проекта |

## Быстрый старт (локально, SQLite)

```bash
cd cargo_project
python -m venv venv
source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Затем открыть http://127.0.0.1:8000/

## Запуск в Docker (Postgres в проде)

```bash
docker-compose up --build
```

Сайт будет доступен на http://localhost:8000/. После запуска можно
зайти в контейнер и засеять данные:

```bash
docker-compose exec web python manage.py seed_demo
docker-compose exec web python manage.py createsuperuser
```

## Демо-аккаунты после `seed_demo`

| Логин | Пароль | Роль |
| --- | --- | --- |
| `driver1` … `driver10` | `passdriver123` | Водитель |
| `client1` … `client11` | `passclient123` | Клиент |

Суперюзера создать отдельно через `createsuperuser`.

## Тесты

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report -m
```

## Структура моделей (упрощённо)

```
User --1:1-- UserProfile (роль/телефон/ДР/часовой пояс)
User --1:1-- Driver
User --1:1-- Client
Vehicle --FK--> VehicleType, BodyType, Driver
Order --FK--> Client, Driver?, Vehicle?, CargoType, PromoCode?
Order --M2M--> Service
Service --M2M--> CargoType
Organization --1:N--> Client
```

## Внешние API

* `https://api.quotable.io/random` — цитата дня на главной.
* `https://open.er-api.com/v6/latest/USD` — курсы валют на главной.

При недоступности API подставляются fallback-значения и пишется warning в лог.

## Лицензия

Учебный проект (БГУИР, ИГИ, ЛР5).
