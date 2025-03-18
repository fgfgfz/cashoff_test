# Парсер данных профиля и избранного с сайта https://siriust.ru/

### Используемые инструменты
* Python 3.13.2 `https://www.python.org/downloads/`
* PostgreSQL 16 `https://www.enterprisedb.com/downloads/postgres-postgresql-downloads`

### Подготовка и запуск
1. Создать папку дял проект **(последующие python команды использовать в консоли в папке проекта)**
2. Скачать проект из репозитория в папку проекта (`<> Code -> Download ZIP` и распаковать или, например в PyCharm, `Get from VCS` -> `https://github.com/fgfgfz/cashoff_test.git`)
3. Создать виртуальное окружение `python -m venv [название]` и запустить его `[название]/Scripts/activate` если не запустилось автоматически
4. Загрузить библиотеки `pip install -r requirements.txt`
5. Создать в postgres базу данных или использовать существующую
6. В файл `.env` заполнить поля для подключения к базе данных:
   ```
   LOGIN=[login]
   PASSWORD=[password]
   HOST=[host]
   PORT=[port]
   DATABASE=[database]
   SCHEMA=[schema]
   ```
7. Запустить файл `main.py` командой `python main.py`
8. Ввести в консоль логин и пароль от сайта

### Результатом работы будет:
* Папка `users_data` с текстовым файлом вида `[email]_[%Y-%m-%d_%H-%M-%S].txt`, содержащем данные о пользователе и товарах из списка желаемого в формате JSON (далее в этой папке при следующих запусках будут создаваться подобные текстовики)
* Те же данные, занесённые в базу данных
* Также создастся файл с логами `logs.log`