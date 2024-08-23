Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/kaluginpeter/cat_charity_fund
```

```
cd cat_charity_fund
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
Создайте файл .evn:
```
touch .evn
```

Создайте переменные:
```
DATABASE_URL=sqlite+aiosqlite:///./fastapi.db # Подключение базы данных
SECRET=reallysupersecret # ключ для использования внутри приложения
FIRST_SUPERUSER_EMAIL=admin@admin.com
FIRST_SUPERUSER_PASSWORD=admin
```

Команда для создания и инициализации бд:

```
alembic upgrade head
```

Команда для запуска:

```
uvicorn app.main:app
```

### Справка по ручкам:

[![OpenApi](https://img.shields.io/badge/openapi-blue)](https://github.com/kaluginpeter/cat_charity_fund/blob/master/openapi.json)


### Stack of techonologies:
* FastAPI, FastAPI-Users, Python

### Author:
* [Kalugin Peter Sergeevich](https://github.com/kaluginpeter)