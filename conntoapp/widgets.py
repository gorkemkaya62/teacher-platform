from django import forms

from .phone_data import COUNTRY_ISO_BY_CODE, country_flag_url


class PhoneCountryCodeWidget(forms.Select):
    template_name = 'conntoapp/widgets/phone_country_code.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        selected = value or context['widget']['value']
        iso = COUNTRY_ISO_BY_CODE.get(selected, 'TR')
        context['widget']['selected_iso'] = iso.lower()
        context['widget']['selected_flag'] = country_flag_url(iso, size=40)
        context['widget']['selected_code'] = selected or '+90'
        return context

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )
        if value:
            iso = COUNTRY_ISO_BY_CODE.get(value, 'TR')
            option['attrs']['data_iso'] = iso.lower()
            option['attrs']['data_flag'] = country_flag_url(iso, size=40)
        return option

    class Media:
        js = ('adminstatic/js/phone-field.js',)
