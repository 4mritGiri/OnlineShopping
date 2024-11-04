from django.core import validators
from django.utils.deconstruct import deconstructible

@deconstructible
class PhoneValidator(validators.RegexValidator):
    regex = r'^0?(?:[789]\d{9}|(?:98|97|96|95)\d{8})$'
    message = 'Enter a valid mobile number: 10 digits starting with "0" and "7", "8", or "9", or "98", "97", "96", "95".'
    flags = 0

phone_validator = PhoneValidator()
