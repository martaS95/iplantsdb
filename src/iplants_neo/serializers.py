from rest_framework import serializers
from iplants_neo.models import MetabolicModel


class MetabolicModelSerializer(serializers.Serializer):
    """
    Serializer for the MetabolicModel object
    """
    model = MetabolicModel

    model_id = serializers.CharField(required=True, max_length=10)
    organism = serializers.CharField(required=True)
    taxid = serializers.IntegerField()
    year = serializers.IntegerField()
    author = serializers.CharField()
