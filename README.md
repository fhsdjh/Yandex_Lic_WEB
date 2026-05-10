# ФотоДневник

Учебный проект из двух частей: веб-приложение на Flask и навык для
Алисы. Используется общая база SQLite и общие модели SQLAlchemy.

## Введение

Сайт-блог, в котором пользователь регистрируется, входит, добавляет
заметки с картинками и видит ленту чужих записей. Параллельно
поднимается навык Алисы «Угадай страну»: показывает картинку города,
включает звук, спрашивает страну. Ответ проверяется через API
Яндекс.Геокодера.

Цель — закрепить работу с Flask, ORM, формами, авторизацией, загрузкой
файлов, REST API и WebHook-навыком Алисы.

## Реализация

Структура:

```
main.py          веб-приложение
alice.py         навык Алисы
forms.py         формы flask-wtf
requirements.txt
data/            модели SQLAlchemy
templates/       Jinja2 + Bootstrap 5
static/          css и загрузки
```

Классы:

- `User` — пользователь (`UserMixin`, методы `set_pwd`/`check_pwd`)
- `Post` — заметка с картинкой, связана с `User`
- `Stat` — счёт игрока навыка
- `RegisterForm`, `LoginForm`, `PostForm` — формы flask-wtf

Технологии: Flask, Flask-Login, Flask-WTF, SQLAlchemy +
SQLAlchemy-serializer, Bootstrap 5 (CDN), Werkzeug (хеш паролей,
secure_filename), `requests` для API Яндекс.Геокодера.

REST API: `GET /api/posts`, `GET /api/posts/<id>`.

Запуск:

```bash
pip install -r requirements.txt
python main.py     # 5000
python alice.py    # 5001
```

Хостинг: подходит Replit, PythonAnywhere или Яндекс.Облако. Адрес
запущенного `alice.py` указывается в Webhook URL навыка на
`dialogs.yandex.ru/developer/`. Картинки городов предварительно
загружаются в раздел «Ресурсы» и их `image_id` подставляются в словарь
`CITIES`.

## Заключение

В проекте отработаны: ORM-модели, авторизация, формы, загрузка файлов,
REST API, шаблоны Bootstrap, навык Алисы с контекстом, медиа и
сторонним API.