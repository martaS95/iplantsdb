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


class MetaboliteListSerializer(serializers.Serializer):

    metabolites = serializers.ListField()


class ReactionListSerializer(serializers.Serializer):

    reactions = serializers.ListField()


class EnzymesListSerializer(serializers.Serializer):

    enzymes = serializers.ListField()


class PathwayListSerializer(serializers.Serializer):

    pathways = serializers.ListField()
