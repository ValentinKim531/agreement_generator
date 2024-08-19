from django.shortcuts import render, redirect
from .forms import InitialForm, AdditionalDataForm
from .get_api_info import get_api_response
from .utils import (
    generate_and_download_document,
    inflect_fio_in_genitive,
    format_location,
    fio_to_initials,
    determine_entity_type_and_name,
    format_phone_number
)
from django.contrib import messages


def initial_request(request):
    if request.method == "POST":
        form = InitialForm(request.POST)
        if form.is_valid():
            iin_or_bin = form.cleaned_data["iin_or_bin"]
            response_data = get_api_response(iin_or_bin)
            if "error" in response_data:
                if not messages.get_messages(request):
                    messages.warning(request, "Данные по ИИН не найдены. Пожалуйста, заполните информацию вручную.")
            request.session["iin_or_bin"] = iin_or_bin
            request.session["response_data"] = response_data
            return redirect("fill_additional_data")
    else:
        form = InitialForm()
    return render(request, "initial_request.html", {"form": form})


def fill_additional_data(request):
    iin_or_bin = request.session.get('iin_or_bin', None)
    initial_data = request.session.get("response_data", {}).copy()

    if iin_or_bin:
        initial_data['iin_or_bin'] = iin_or_bin

    is_too_template, name_ip_or_too_value = False, ''
    if initial_data:
        is_too_template, name_ip_or_too_value = determine_entity_type_and_name(initial_data)
        initial_data.update({
            "city": initial_data.get("city", "").replace("Г.", "").strip().title(),
            "name_ip_or_too": name_ip_or_too_value,
            "name_director": inflect_fio_in_genitive(initial_data.get("name_director", "")),
            "initials": fio_to_initials(initial_data.get("name_director", "")),
            "location": format_location(initial_data.get("location", "")),
            "phone": format_phone_number(initial_data.get("phone", "")),
        })

    form = AdditionalDataForm(request.POST or None, initial=initial_data)

    if request.method == "POST" and form.is_valid():
        edited_data = form.cleaned_data
        if edited_data.get('bank') == 'other' and 'other_bank' in edited_data:
            edited_data['bank'] = edited_data['other_bank']

        if edited_data.get('action') == 'other':
            edited_data['action_text'] = edited_data['other_action']
        else:
            action_choices = dict(form.fields['action'].choices)
            edited_data['action_text'] = action_choices.get(edited_data['action'], '')

        edited_data['iin_or_bin'] = iin_or_bin or edited_data.get('iin_or_bin', '')
        edited_data.pop('other_bank', None)
        edited_data.pop('action', None)
        edited_data.pop('other_action', None)

        return generate_and_download_document(edited_data)

    return render(request, "additional_data.html", {
        "form": form,
        "is_too_template": is_too_template,
    })







