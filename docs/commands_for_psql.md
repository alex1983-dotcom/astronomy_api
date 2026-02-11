# Настройка базы данных

## Вход в psql

- перед входом в консоль psql, ввести команду в терминале - `chcp1251`
> Вход:
```
psql -U postgres
Ввести пароль: xxxxxx
```
## Создаем базу данных с нужной кодировкой

```psql
CREATE DATABASE astronomy_db
WITH ENCODING 'UTF8'
     LC_COLLATE 'Russian_Russia.1251'
     LC_CTYPE 'Russian_Russia.1251'
     TEMPLATE template0;
```

## Создаем пользователя

```
-- Создаём пользователя (замените 'password' на свой надёжный пароль)
CREATE USER "mechanic" WITH PASSWORD 'password';

-- Даём права на базу
GRANT ALL PRIVILEGES ON DATABASE astronomy_db TO "mechanic";

-- Подключаемся к базе (обязательно!)
\c astronomy_db

-- Даём права на схему public (иначе таблицы не создадутся)
GRANT ALL ON SCHEMA public TO "mechanic";
GRANT ALL ON ALL TABLES IN SCHEMA public TO "mechanic";
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO "mechanic";
```

## Проверка подключения

> Создать в корне проектка файл `test_db.py`

```python
import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect(
        user='user',
        password='password',
        database='astronomy_db',
        host='localhost'
    )
    print("✅ Подключение успешно!")
    await conn.close()

asyncio.run(test())
```