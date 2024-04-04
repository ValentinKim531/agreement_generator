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
    action_text = data.get("action_text", "Не указано")
    deistvuushego = get_deistvuushego(iin_or_bin)

    context = {
        "City": " " + data.get("city", ""),
        "str_date": get_formatted_date(),
        "name_IP": "«" + data.get("name_ip_or_too", "") + "»"
        if not is_too_template
        else "",
        "name_TOO": "«" + data.get("name_ip_or_too", "") + "»"
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

    doc.render(context)
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)

    name_ip_or_too = (
        data.get("name_ip_or_too", "")
        .replace('"', "")
        .replace("/", "")
        .replace("\\", "")
    )
    filename = f"{name_ip_or_too} Согласие.docx"

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
    if len(iin_or_bin) >= 5:
        template_filename = "TOO.docx" if iin_or_bin[4] in ("4", "5") else "IP.docx"
    else:
        template_filename = "IP.docx"

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
    cleaned_string = re.sub(r'(^|\s)"?ИП\s+', r'\1"', original_string)

    match = re.search(r'"?([^"]+)"?$', cleaned_string)
    if match:
        return f'{match.group(1)}'
    else:
        return f'{cleaned_string}'


def extract_title_too(original_string):
    cleaned_string = re.sub(
        r'^"ТОО\s+(.*?)"$', r"\1", original_string
    )

    if not cleaned_string.startswith('"'):
        cleaned_string = re.sub(r"^ТОО\s+", "", cleaned_string)

    cleaned_string = cleaned_string.strip('"')

    return f'{cleaned_string}'


def format_location(location):
    if not location or location.isspace():
        return ""

    location = re.sub(r"\b[А-Яа-я]+\s+Г\.А\.\,?\s*", "", location)

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

    location = re.sub(r"\bГОРОД\b", "г.", location, flags=re.IGNORECASE)
    location = re.sub(r"\bГ\.\s*", "г. ", location, flags=re.IGNORECASE)

    # Добавляем "Республика Казахстан" только если location не пуста
    if not location.startswith("Республика Казахстан") and location:
        location = "Республика Казахстан, " + location

    location = " ".join(
        word.title() if not re.match(
            r"^(г\.|д\.|мкр\.|ул\.|пр\.|с\.о\.|н\.п\.|зд\.|ст-е|кв\.)$",
            word.lower(),
        ) else word for word in location.split()
    )

    return location



def fio_to_initials(full_name):
    name_parts = re.split(r"\s+", full_name.strip())

    if len(name_parts) == 3:
        initials = (
            f"{name_parts[0]} {name_parts[1][0]}.{name_parts[2][0]}."
        )
    elif len(name_parts) == 2:
        initials = f"{name_parts[0]} {name_parts[1][0]}."
    else:
        initials = full_name
    return initials.title()


def format_phone_number(phone_number):
    if not phone_number:
        return ""

    phone_number = phone_number.replace(" ", "")

    if phone_number.startswith('+7') and len(phone_number) == 12:
        formatted_number = (f"+{phone_number[1]} {phone_number[2:5]} "
                            f"{phone_number[5:8]} {phone_number[8:10]} "
                            f"{phone_number[10:]}")
    elif phone_number.startswith('8') and len(phone_number) == 11:
        formatted_number = (f"+7 {phone_number[1:4]} {phone_number[4:7]} "
                            f"{phone_number[7:9]} {phone_number[9:]}")
    else:
        formatted_number = phone_number

    return formatted_number

