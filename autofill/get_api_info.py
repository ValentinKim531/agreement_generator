import requests
from requests.exceptions import RequestException

def get_api_response(iin_or_bin):
    try:
        response = requests.get(f"https://apiba.prgapp.kz/CompanyFullInfo?id={iin_or_bin}&lang=ru")
        if response.status_code == 200:
            data = response.json()
            extracted_data = {
                'iin_or_bin': iin_or_bin,
                'name_director': data['basicInfo']['ceo']['value']['title'],
                'name_ip_or_too': data['basicInfo']['titleRu']['value'],
                'city': data['basicInfo']['cityName'] if data['basicInfo']['cityName'] else 'Алматы',
                'location': data['basicInfo']['addressRu']['value'],
                'phone': data['gosZakupContacts']['phone'][0]['value'] if data['gosZakupContacts'] else '',
            }
            return extracted_data
        else:
            return {"error": f"Ошибка запроса: статус {response.status_code}, введите верный ИИН/БИН"}
    except RequestException as e:
        return {"error": f"Ошибка запроса: {e}"}

