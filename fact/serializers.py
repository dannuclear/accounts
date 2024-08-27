from rest_framework import serializers
from .models import Fact

class FactSerializer (serializers.ModelSerializer):

    class Meta:
        model = Fact
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', )
