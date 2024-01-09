# Create your models here.

import datetime
from mongoengine import Document, fields


class Metabolite(Document):

    entry_id = fields.StringField(primary_key=True)
    common_name = fields.StringField()
    synonyms = fields.ListField(fields.StringField())
    crossrefs = fields.DictField()
    met_type = fields.ListField(fields.StringField())
    formula = fields.StringField()
    inchi = fields.StringField()
    inchikey = fields.StringField()
    smiles = fields.StringField()
    database_version = fields.DictField()
    models = fields.DictField()
    timestamp = fields.DateTimeField(required=True, default=datetime.datetime.utcnow)
    state = fields.StringField()

    def __eq__(self, other):
        if isinstance(other, Metabolite):
            return self.entry_id == other.entry_id and self.common_name == other.common_name and \
                self.crossrefs == other.crossrefs and self.formula == other.formula and \
                self.inchi == other.inchi and self.inchikey == other.inchikey \
                and self.smiles == other.smiles

    def __hash__(self):
        return hash((self.entry_id, self.common_name, map(tuple, self.crossrefs), self.formula, self.inchi,
                     self.inchikey, self.smiles))

    def str_attributes(self):
        return {"formula": self.formula, "inchi": self.inchi, "inchikey": self.inchikey, "smiles": self.smiles}


class Reaction(Document):

    entry_id = fields.StringField(primary_key=True)
    common_name = fields.StringField()
    synonyms = fields.ListField(fields.StringField())
    crossrefs = fields.DictField()
    direction = fields.StringField()
    ecnumber = fields.StringField()
    in_pathway = fields.DictField()
    reactants = fields.DictField()
    products = fields.DictField()
    genes = fields.DictField()
    enzymes = fields.DictField()
    database_version = fields.DictField()
    timestamp = fields.DateTimeField(required=True, default=datetime.datetime.utcnow)
    models = fields.DictField()
    state = fields.StringField()
    reaction_type = fields.StringField()
    by_complex = fields.BooleanField()
    sub_reactions = fields.DictField()
    lower_bound = fields.IntField(default=0)
    upper_bound = fields.IntField(default=10000)
    compartment = fields.DictField()

    def __eq__(self, other):
        if isinstance(other, Reaction):
            return self.entry_id == other.entry_id and self.common_name == other.common_name and \
                self.crossrefs == other.crossrefs and self.direction == other.direction and \
                self.ecnumber == other.ecnumber and self.in_pathway == self.in_pathway and \
                self.reactants == other.reactants and self.products == other.products and \
                self.genes == other.genes and self.enzymes == other.enzymes

    def __hash__(self):
        return hash((self.entry_id, self.common_name, map(tuple, self.crossrefs), self.direction, self.ecnumber,
                     map(tuple, self.in_pathway), map(tuple, self.reactants), map(tuple, self.products),
                     map(tuple, self.genes), map(tuple, self.enzymes)))

    def str_attributes(self):
        return {"direction": self.direction, "ecnumber": self.ecnumber}

    def list_attributes(self):
        return {"in_pathway": self.in_pathway, "genes": self.genes, "enzymes": self.enzymes,
                "sub_reactions": self.sub_reactions, "compartment": self.compartment}


class Enzyme(Document):

    entry_id = fields.StringField(primary_key=True)
    common_name = fields.StringField()
    synonyms = fields.ListField(fields.StringField())
    crossrefs = fields.DictField()
    uniprot_status = fields.StringField()
    uniprot_product = fields.StringField()
    uniprot_function = fields.ListField()
    uniprot_location = fields.ListField()
    genes = fields.DictField()
    reactions = fields.DictField()
    organisms = fields.DictField()
    database_version = fields.DictField()
    timestamp = fields.DateTimeField(required=True, default=datetime.datetime.utcnow)
    state = fields.StringField()
    sequence = fields.StringField()
    protein_type = fields.StringField()
    component_of = fields.DictField()
    components = fields.DictField()

    def __eq__(self, other):
        if isinstance(other, Enzyme):
            return self.entry_id == other.entry_id and self.common_name == other.common_name and \
                self.crossrefs == other.crossrefs and self.genes == other.genes and \
                self.reactions == other.reactions and self.organisms == other.organisms and \
                self.protein_type == other.protein_type and self.component_of == other.component_of and \
                self.components == other.components

    def __hash__(self):
        return hash((self.entry_id, self.common_name, map(tuple, self.crossrefs), map(tuple, self.genes),
                     map(tuple, self.reactions), map(tuple, self.organisms), self.protein_type,
                     map(tuple, self.component_of), map(tuple, self.components)))

    def str_attributes(self):
        return {'uniprot_status': self.uniprot_status, 'uniprot_product': self.uniprot_product,
                'protein_type': self.protein_type, 'sequence': self.sequence}

    def list_attributes(self):
        return {"genes": self.genes, "reactions": self.reactions, "organisms": self.organisms,
                "component_of": self.component_of, "components": self.components}


class Gene(Document):

    entry_id = fields.StringField(primary_key=True)
    common_name = fields.StringField()
    synonyms = fields.ListField(fields.StringField())
    crossrefs = fields.DictField()
    reactions = fields.DictField()
    enzymes = fields.DictField()
    database_version = fields.DictField()
    timestamp = fields.DateTimeField(required=True, default=datetime.datetime.utcnow)
    state = fields.StringField()
    sequence = fields.StringField()

    def __eq__(self, other):
        if isinstance(other, Gene):
            return self.entry_id == other.entry_id and self.common_name == other.common_name and \
                self.synonyms == other.synonyms and self.crossrefs == other.crossrefs and \
                self.reactions == other.reactions and self.enzymes == other.enzymes

    def __hash__(self):
        return hash((self.entry_id, self.common_name, map(tuple, self.synonyms), map(tuple, self.crossrefs),
                     map(tuple, self.reactions), map(tuple, self.enzymes)))

    def str_attributes(self):
        return {'sequence': self.sequence}

    def list_attributes(self):
        return {"reactions": self.reactions, "enzymes": self.enzymes}


class Pathway(Document):

    entry_id = fields.StringField(primary_key=True)
    common_name = fields.StringField()
    synonyms = fields.ListField(fields.StringField())
    organisms = fields.DictField()
    reactions = fields.DictField()
    super_pathways = fields.ListField(fields.StringField())
    pathway_links = fields.DictField()
    database_version = fields.DictField()
    timestamp = fields.DateTimeField(required=True, default=datetime.datetime.utcnow)
    state = fields.StringField()

    def __eq__(self, other):
        if isinstance(other, Pathway):
            return self.entry_id == other.entry_id and self.common_name == other.common_name and \
                self.synonyms == other.synonyms and self.organisms == other.organisms and \
                self.reactions == other.reactions and self.super_pathways == other.super_pathways and \
                self.pathway_links == other.pathway_links

    def __hash__(self):
        return hash((self.entry_id, self.common_name, map(tuple, self.synonyms), map(tuple, self.organisms),
                     map(tuple, self.reactions), map(tuple, self.super_pathways), map(tuple, self.pathway_links)))

    def str_attributes(self):
        return {'common_name': self.common_name}

    def list_attributes(self):
        return {"organisms": self.organisms, "reactions": self.reactions}


class MetabolicModel(Document):

    model_id = fields.StringField(primary_key=True)
    organism = fields.StringField()
    taxid = fields.IntField()
    year = fields.IntField()
    author = fields.StringField()
    annotation = fields.DictField()
    genes = fields.ListField(fields.StringField())
    enzymes = fields.ListField(fields.StringField())
    reactions = fields.ListField(fields.StringField())
    metabolites = fields.ListField(fields.StringField())
    pathways = fields.ListField(fields.StringField())
    gprs = fields.ListField()
    timestamp = fields.DateTimeField(required=True, default=datetime.datetime.utcnow)

    def __eq__(self, other):
        if isinstance(other, MetabolicModel):
            return self.model_id == other.model_id and self.organism == other.organism and \
                self.year == other.year and self.genes == other.genes and self.metabolites == other.metabolites and \
                self.reactions == other.reactions and self.enzymes == other.enzymes

    def __hash__(self):
        return hash((self.model_id, self.organism, self.year, map(tuple, self.genes),
                     map(tuple, self.enzymes), map(tuple, self.reactions), map(tuple, self.metabolites)))


class Organism(Document):

    entry_id = fields.StringField(primary_key=True)
    common_name = fields.StringField()
    scientific_name = fields.StringField()
    taxid = fields.IntField()
    species = fields.StringField()
    genus = fields.StringField()
    family = fields.StringField()
    order = fields.StringField()
    org_class = fields.StringField()
    phylum = fields.StringField()
    kingdom = fields.StringField()
    superkingdom = fields.StringField()
    pathways = fields.DictField()
    genes = fields.DictField()
    enzymes = fields.DictField()
    database_version = fields.DictField()
    timestamp = fields.DateTimeField(required=True, default=datetime.datetime.utcnow)

    def __eq__(self, other):
        if isinstance(other, Organism):
            return (self.entry_id == other.entry_id and self.taxid == other.taxid and
                    self.scientific_name == other.scientific_name and self.species == other.species and
                    self.pathways == other.pathways and self.enzymes == other.enzymes)

    def __hash__(self):
        return hash((self.entry_id, self.taxid, self.scientific_name, self.species,
                     map(tuple, self.pathways), map(tuple, self.enzymes)))

    def str_attributes(self):
        return {"scientific_name": self.scientific_name, "species": self.species, "genus": self.genus,
                "family": self.family, "order": self.order, "org_class": self.org_class, "phylum": self.phylum,
                "kingdom": self.kingdom, "superkingdom": self.superkingdom}

    def list_attributes(self):
        return {"pathways": self.pathways, "enzymes": self.enzymes, "genes": self.genes}


class Transcriptomics(Document):

    database = fields.StringField()
    title = fields.StringField()
    data_type = fields.StringField(required=True)
    organism = fields.StringField(required=True)
    accession_number = fields.StringField(primary_key=True)
    platform_id = fields.ListField(fields.StringField())
    contributors = fields.ListField(fields.StringField())
    last_update_date = fields.DateTimeField(required=True, default=datetime.datetime.utcnow)
    overall_design = fields.StringField()
    samples = fields.DictField()
