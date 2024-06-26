from rest_framework import serializers
from iplants_mongo.models import *


class MetaboliteSerializer(serializers.Serializer):
    """
    Serializer for the Metabolite model
    """
    model = Metabolite


class ReactionSerializer(serializers.Serializer):
    """
    Serializer for the Reaction model
    """
    model = Reaction

    entry_id = serializers.CharField(required=True)
    reactants = serializers.DictField()
    products = serializers.DictField()
    direction = serializers.CharField()
    lower_bound = serializers.IntegerField()
    upper_bound = serializers.IntegerField()
    reaction_type = serializers.CharField()
    in_pathway = serializers.ListField()
    compartment = serializers.ListField()
    models = serializers.DictField()


class EnzymeSerializer(serializers.Serializer):
    """
    Serializer for the Enzyme model
    """
    model = Enzyme


class GeneSerializer(serializers.Serializer):
    """
    Serializer for the Enzyme model
    """
    model = Gene


class PathwaySerializer(serializers.Serializer):
    """
    Serializer for the Enzyme model
    """
    model = Pathway


class OrganismSerializer(serializers.Serializer):
    """
    Serializer for the Enzyme model
    """
    model = Organism


class MetabolicModelSerializer(serializers.Serializer):
    """
    Serializer for the MetabolicModel model
    """
    model = MetabolicModel

    model_id = serializers.CharField(required=True, max_length=30)
    organism = serializers.CharField(required=True)
    taxid = serializers.IntegerField()
    year = serializers.IntegerField()
    author = serializers.CharField()