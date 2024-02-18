import locale
from datetime import datetime
from docxtpl import DocxTemplate
import io
from django.http import FileResponse
import os
from django.conf import settings
from pymorphy3 import MorphAnalyzer
import requests
import xml.etree.ElementTree as ET
import re


locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")


def generate_and_download_document(data):
    iin_or_bin = data.get("iin_or_bin", "")

    doc, is_too_template = get_document_template_and_path(iin_or_bin)
    action_text = get_action_text(
        data.get("action"), data.get("other_action", "").strip()
    )
    deistvuushego = get_deistvuushego(iin_or_bin)

    # Формирование контекста
    context = {
        "City": data.get("city", ""),
        "str_date": get_formatted_date(),
        "name_IP": data.get("name_ip_or_too", "")
        if not is_too_template
        else "",
        "name_TOO": data.get("name_ip_or_too", "")
        if is_too_template
        else "",
        "deistvuushego": deistvuushego,
        "action": action_text,
        "IIN": iin_or_bin,
        "BIN": iin_or_bin,
        "name_director": data.get("name_director", ""),
        "Location": data.get("location", ""),
        "IIK": data.get("IIK", ""),
        "BIK": data.get("BIK", "").upper(),
        "bank": data.get("bank", ""),
        "phone": data.get("phone", ""),
        "initials": data.get("initials", ""),
        "is_too_template": is_too_template,
    }

    # Заполнение шаблона и сохранение документа
    doc.render(context)
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)

    # Название файла с учетом наименования ИП/ТОО
    name_ip_or_too = (
        data.get("name_ip_or_too", "")
        .replace('"', "")
        .replace("/", "")
        .replace("\\", "")
    )  # Удаление потенциально проблемных символов
    filename = f"{name_ip_or_too} Согласие.docx"

    # Возврат файла пользователю
    return FileResponse(bio, as_attachment=True, filename=filename)


def determine_entity_type_and_name(initial_data):
    """
    Определяет тип субъекта (ИП или ТОО) и очищает название.
    Возвращает флаг is_too_template
    и очищенное название name_ip_or_too_value.
    """
    if initial_data.get("iin_or_bin", "")[4] in ("4", "5"):
        is_too_template = True
        name_ip_or_too_value = extract_title_too(
            initial_data.get("name_ip_or_too", "")
        )
    else:
        is_too_template = False
        name_ip_or_too_value = extract_title_ip(
            initial_data.get("name_ip_or_too", "")
        )

    return is_too_template, name_ip_or_too_value


def get_action_text(action, other_action):
    if action == "other" and other_action:
        return other_action
    elif action == "charter":
        return "Устава"
    elif action == "founding_contract":
        return "Учредительного договора"
    return ""


def get_deistvuushego(iin_or_bin):
    morph = MorphAnalyzer()
    gender_digit = iin_or_bin[6] if len(iin_or_bin) > 6 else "1"
    gender = (
        "masc" if gender_digit in ("1", "3", "5", "0") else "femn"
    )
    word_deistvuushego = morph.parse("действующий")[0]
    return word_deistvuushego.inflect({gender, "sing", "gent"}).word


def get_document_template_and_path(iin_or_bin):
    template_filename = (
        "TOO.docx" if iin_or_bin[4] in ("4", "5") else "IP.docx"
    )
    template_path = os.path.join(
        settings.BASE_DIR, "agreements_templates", template_filename
    )
    doc = DocxTemplate(template_path)
    is_too_template = template_filename == "TOO.docx"
    return doc, is_too_template


def get_formatted_date():
    now = datetime.now()
    month_ru = now.strftime("%B")
    formatted_date = (
        now.strftime(f"«%d» {month_ru} %Y года")
        .lstrip("0")
        .replace(" 0", " ")
    )

    return formatted_date


def inflect_fio_in_genitive(full_name):
    encoded_name = full_name.replace(" ", "%20")
    headers = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(
        f"https://ws3.morpher.ru/russian/declension?s={encoded_name}",
        headers=headers,
    )

    if response.status_code == 200:
        root = ET.fromstring(response.content)
        genitive = root.find(".//Р")
        if genitive is not None:
            genitive_text = genitive.text.replace("%", " ").title()
            return genitive_text
        else:
            print("Родительный падеж не найден в ответе")
            return None
    else:
        print(f"Ошибка запроса: {response.status_code}")
        return None


def extract_title_ip(original_string):
    # Удаление "ИП " из строки, даже если оно находится внутри кавычек
    cleaned_string = re.sub(r'(^|\s)"?ИП\s+', r'\1"', original_string)

    # Поиск и возвращение строки в кавычках, если они присутствуют
    match = re.search(r'"?([^"]+)"?$', cleaned_string)
    if match:
        # Возвращаем результат в двойных кавычках
        return f'"{match.group(1)}"'
    else:
        # Если кавычек нет, возвращаем всю строку в двойных кавычках
        return f'"{cleaned_string}"'


def extract_title_too(original_string):
    # Удаление "ТОО " из начала строки, если оно присутствует,
    # включая кавычки вокруг ТОО
    cleaned_string = re.sub(
        r'^"ТОО\s+(.*?)"$', r"\1", original_string
    )

    # Удаление "ТОО " без кавычек в начале, если оно присутствует
    if not cleaned_string.startswith('"'):
        cleaned_string = re.sub(r"^ТОО\s+", "", cleaned_string)

    # Удаление лишних кавычек по краям
    cleaned_string = cleaned_string.strip('"')

    # Возвращение результата в двойных кавычках
    return f'"{cleaned_string}"'


def format_location(location):
    # 1. Удаление "Г.А." и предшествующего слова
    location = re.sub(r"\b[А-Яа-я]+\s+Г\.А\.\,?\s*", "", location)

    # 2. Приведение аббревиатур к нижнему регистру
    abbreviations = [
        "Д\.",
        "Мкр\.",
        "Ул\.",
        "Пр\.",
        "С\.О\.",
        "Н\.П\.",
        "Зд\.",
        "Ст-Е",
        "Кв\.",
    ]
    for abbr in abbreviations:
        location = re.sub(
            rf"\b{abbr}",
            lambda x: x.group(0).lower(),
            location,
            flags=re.IGNORECASE,
        )

    # 3. Сокращение "ГОРОД" до "г." и обработка "Г."
    # в нижнем регистре с пробелом после точки
    location = re.sub(
        r"\bГОРОД\b", "г.", location, flags=re.IGNORECASE
    )
    location = re.sub(
        r"\bГ\.\s*", "г. ", location, flags=re.IGNORECASE
    )

    # Добавление "Республика Казахстан", если отсутствует
    if not location.startswith("Республика Казахстан"):
        location = "Республика Казахстан, " + location

    # Приведение первого символа каждого слова к верхнему регистру,
    # кроме специальных слов и аббревиатур
    location = " ".join(
        word.title()
        if not re.match(
            r"^(г\.|д\.|мкр\.|ул\.|пр\.|с\.о\.|н\.п\.|зд\.|ст-е|кв\.)$",
            word.lower(),
        )
        else word
        for word in location.split()
    )

    return location


def fio_to_initials(full_name):
    # Разделяем полное имя на компоненты
    name_parts = re.split(r"\s+", full_name.strip())
    # Формируем фамилию и инициалы
    if len(name_parts) == 3:  # Фамилия Имя Отчество
        initials = (
            f"{name_parts[0]} {name_parts[1][0]}.{name_parts[2][0]}."
        )
    elif len(name_parts) == 2:  # Фамилия Имя
        initials = f"{name_parts[0]} {name_parts[1][0]}."
    else:  # Только Фамилия или однословное имя
        initials = full_name
    return initials.title()
