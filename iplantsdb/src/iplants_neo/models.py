# Create your models here.
from neomodel import StructuredNode, StringProperty, RelationshipTo, DateTimeFormatProperty, StructuredRel, \
    IntegerProperty


class StoicRel(StructuredRel):
    stoichiometry = StringProperty()


class ComponentsRel(StructuredRel):
    number = IntegerProperty()


class Metabolite(StructuredNode):
    entry_id = StringProperty(unique_index=True, required=True)
    name = StringProperty()
    database_version = StringProperty()
    state = StringProperty()
    timestamp = DateTimeFormatProperty(default_now=True, format="%Y-%m-%d %H:%M:%S")

    def __eq__(self, other):
        if isinstance(other, Metabolite):
            return self.entry_id == other.entry_id and self.name == other.name

    def __hash__(self):
        return hash((self.entry_id, self.name))

    class Meta:
        verbose_name = "Metabolite"


class Reaction(StructuredNode):

    entry_id = StringProperty(unique_index=True, required=True)
    name = StringProperty()
    reactants = RelationshipTo(Metabolite, 'REAC_USES_MET', model=StoicRel)
    products = RelationshipTo(Metabolite, 'REAC_PRODUCES_MET', model=StoicRel)
    database_version = StringProperty()
    state = StringProperty()
    timestamp = DateTimeFormatProperty(default_now=True, format="%Y-%m-%d %H:%M:%S")

    def __eq__(self, other):
        if isinstance(other, Reaction):
            return self.entry_id == other.entry_id and self.name == other.name

    def __hash__(self):
        return hash((self.entry_id, self.name))


class Enzyme(StructuredNode):

    entry_id = StringProperty(unique_index=True, required=True)
    name = StringProperty()
    reactions = RelationshipTo(Reaction, 'ENZ_CATALYSES_REAC')
    components = RelationshipTo('Enzyme', 'COMPOSED_BY', model=ComponentsRel)
    database_version = StringProperty()
    state = StringProperty()
    timestamp = DateTimeFormatProperty(default_now=True, format="%Y-%m-%d %H:%M:%S")

    def __eq__(self, other):
        if isinstance(other, Enzyme):
            return self.entry_id == other.entry_id and self.name == other.name

    def __hash__(self):
        return hash((self.entry_id, self.name))


class Gene(StructuredNode):

    entry_id = StringProperty(unique_index=True, required=True)
    name = StringProperty()
    enzymes = RelationshipTo(Enzyme, 'GENE_EXPRESSES_ENZ')
    database_version = StringProperty()
    state = StringProperty()
    timestamp = DateTimeFormatProperty(default_now=True, format="%Y-%m-%d %H:%M:%S")

    def __eq__(self, other):
        if isinstance(other, Gene):
            return self.entry_id == other.entry_id and self.name == other.name

    def __hash__(self):
        return hash((self.entry_id, self.name))


class Pathway(StructuredNode):
    entry_id = StringProperty(unique_index=True, required=True)
    name = StringProperty()
    reactions = RelationshipTo(Reaction, 'PATH_HAS_REAC')
    database_version = StringProperty()
    state = StringProperty()
    timestamp = DateTimeFormatProperty(default_now=True, format="%Y-%m-%d %H:%M:%S")

    def __eq__(self, other):
        if isinstance(other, Gene):
            return self.entry_id == other.entry_id and self.name == other.name

    def __hash__(self):
        return hash((self.entry_id, self.name))


class Organism(StructuredNode):

    entry_id = StringProperty(unique_index=True, required=True)
    enzymes = RelationshipTo(Enzyme, 'ORGANISM_HAS_ENZ')
    pathways = RelationshipTo(Pathway, 'ORGANISM_HAS_PATH')
    genes = RelationshipTo(Gene, 'ORGANISM_HAS_GENE')
    database_version = StringProperty()
    timestamp = DateTimeFormatProperty(default_now=True, format="%Y-%m-%d %H:%M:%S")

    def __eq__(self, other):
        if isinstance(other, Organism):
            return self.entry_id == other.entry_id

    def __hash__(self):
        return hash(self.entry_id)


class MetabolicModel(StructuredNode):
    model_id = StringProperty(unique_index=True, required=True)
    organism = StringProperty(required=True)
    taxid = IntegerProperty()
    year = IntegerProperty()
    author = StringProperty()
    reactions = RelationshipTo(Reaction, 'MODEL_HAS_REAC')
    metabolites = RelationshipTo(Metabolite, 'MODEL_HAS_MET')
    enzymes = RelationshipTo(Enzyme, 'MODEL_HAS_ENZ')
    belongs_to = RelationshipTo(Organism, 'BELONGS_TO')
    timestamp = DateTimeFormatProperty(default_now=True, format="%Y-%m-%d %H:%M:%S")
