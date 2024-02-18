FROM python:3.11

RUN apt-get update && apt-get install -y locales

# Добавляем ru_RU.UTF-8 в список генерируемых локалей, а затем генерируем её.
RUN echo "ru_RU.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

# Устанавливаем переменные среды для использования ru_RU.UTF-8
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU:ru
ENV LC_ALL ru_RU.UTF-8

ENV PYTHONBUFFERED=1

WORKDIR /agreement_generator
COPY ./requirements.txt /agreement_generator/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /agreement_generator

EXPOSE 8000
CMD echo $DATABASE_URL && python manage.py migrate && python manage.py loaddata fixtures/dump.json && python manage.py runserver 0.0.0.0:env('PORT')
