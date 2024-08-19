import requests
from requests.exceptions import RequestException


def get_api_response(iin_or_bin):
    try:
        response = requests.get(f"https://apiba.prgapp.kz/CompanyFullInfo?id={iin_or_bin}&lang=ru")
        if response.status_code == 200:
            data = response.json()

            # Проверяем наличие необходимых ключей и данных
            if (data.get('basicInfo') is None or
                data['basicInfo'].get('ceo') is None or
                data['basicInfo']['ceo'].get('value') is None or
                data['basicInfo'].get('titleRu') is None or
                data['basicInfo']['titleRu'].get('value') is None):
                return {"error": "ИИН не найден. Пожалуйста, заполните данные вручную."}

            extracted_data = {
                'iin_or_bin': iin_or_bin,
                'name_director': data['basicInfo']['ceo']['value']['title'],
                'name_ip_or_too': data['basicInfo']['titleRu']['value'],
                'city': data['basicInfo']['cityName'] if data['basicInfo'].get('cityName') else 'Алматы',
                'location': data['basicInfo']['addressRu']['value'] if data['basicInfo'].get('addressRu') else '',
                'phone': data['gosZakupContacts']['phone'][0]['value'] if data.get('gosZakupContacts') and data['gosZakupContacts'].get('phone') else '',
            }
            return extracted_data
        else:
            return {"error": "Ошибка при получении данных. Пожалуйста, заполните данные вручную."}
    except RequestException as e:
        return {"error": f"Ошибка запроса: {e}"}


