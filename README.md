# 🌍 Agreement Generator

Проект `Agreement Generator` представляет собой веб-приложение 
для генерации документов на основе предоставленных пользователем данных.

## Технологии

- Python 3.11
- Django
- Docker
- PostgreSQL

## Локальный запуск проекта

Для запуска проекта локально необходимо иметь установленные Docker и Docker Compose.

### Шаги для запуска:

1. Клонирование репозитория:

```
git clone https://github.com/ValentinKim531/agreement_generator.git
```
```
cd agreement_generator
```


2. Запуск Docker контейнеров:

```
docker-compose up --build
```

3. После того, как контейнеры будут запущены, приложение будет доступно по адресу:

`http://localhost:8013/initial/`


### Использование приложения:

1. Перейдите по ссылке `http://localhost:8013/initial/` для начала работы с приложением.
2. Введите ИИН/БИН и нажмите "Отправить".
3. Заполните дополнительные данные, предложенные формой.
4. Нажмите "Заполнить документ" для генерации документа.


### Примечание:

- Убедитесь, что все переменные окружения (`DB_NAME`, `DB_USER`, `DB_PASSWORD` и другие) корректно заданы в файле `.env` перед запуском приложения.
- Если вы вносите изменения в код приложения, может потребоваться пересборка Docker образов для применения изменений.

