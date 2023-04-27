from django.core.validators import RegexValidator

uzb_phone_number_validation = RegexValidator(
    regex=r'^[+]998\d{9}$',
    message='Phone number must be entered in the format: "+998976543210". Up to 13 digits allowed.',
    code='invalid_phone_number'
)
