import requests_mock
import requests


def get_mock_api_response(iin_or_bin):
    mock_response = {
        "IIN": "761001450167",
        "name_director": "ЮСУПОВА ЖАНАРГУЛЬ КОСМАНОВНА",
        "name_IP": "ИП ЮСУПОВА",
        "Location": "ПАВЛОДАРСКАЯ ОБЛАСТЬ, ПАВЛОДАР Г.А., Г.ПАВЛОДАР",
    }

    with requests_mock.Mocker() as m:
        m.get(f"https://stat.gov.kz/api/juridical?bin={iin_or_bin}&lang=ru", json=mock_response)
        response = requests.get(f"https://stat.gov.kz/api/juridical?bin={iin_or_bin}&lang=ru")
        return response.json()

