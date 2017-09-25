from waffle.utils import get_setting
from rest_framework import serializers as ser

from api.base.serializers import (JSONAPISerializer, TypeField)


class WaffleSwitchSerializer(JSONAPISerializer):
    id = ser.CharField(source='name', required=True, help_text='The name of the Switch')
    type = TypeField()
    name = ser.CharField(required=True, help_text='The name of the Switch')
    note = ser.CharField(required=False, allow_blank=True, help_text='Describe where the Switch is used.')
    active = ser.BooleanField(read_only=True, help_text='Is the Switch active or inactive.')

    class Meta:
        type_ = 'waffle-switch',
