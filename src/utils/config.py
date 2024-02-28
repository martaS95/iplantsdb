PROJECT_PATH = '/iplantsdb'
from configparser import RawConfigParser

db_configs = RawConfigParser()
db_configs.read('/conf/iplantdb.conf')


class Mongo:
    host = str(db_configs.get('iplants-databases-configurations', 'mongodb_host')),
    port = int(db_configs.get('iplants-databases-configurations', 'mongodb_port')),
    database = str(db_configs.get('iplants-databases-configurations', 'mongodb_name'))


class Neo:
    host = str(db_configs.get('iplants-databases-configurations', 'neo4j_host'))
    port = int(db_configs.get('iplants-databases-configurations', 'neo4j_port'))
    username = str(db_configs.get('iplants-databases-configurations', 'neo4j_user'))
    password = str(db_configs.get('iplants-databases-configurations', 'neo4j_pass'))


class API:
    """
    Change API base_url when updated
    """
    base_url = str(db_configs.get('iplants-databases-configurations', 'iplants_api'))
    create_node_model = '/create_model/model_node/'
    create_doc_model = '/create_model/model_doc/'
    reactions_from_enzyme = '/list/reactions/enzyme/'
    metabolites_from_reaction = '/list/metabolites/reaction/'
    pathways_from_reaction = '/list/pathways/reaction/'
    enzymes_from_reaction_mongo = '/list/enzymes/reaction/doc/'
    components_from_enzyme = '/list/components/enzyme/'
    add_enzymes_model_neo = '/create_model/add_rels_enzymes/'
    add_reactions_model_neo = '/create_model/add_rels_reactions/'
    add_metabolites_model_neo = '/create_model/add_rels_metabolites/'
    add_enzymes_model_mongo = '/create_model/add_enzymes/'
    add_reactions_model_mongo = '/create_model/add_reactions/'
    add_metabolites_model_mongo = '/create_model/add_metabolites//'
    add_pathways_model_mongo = '/create_model/add_pathways/'
    add_genes_model_mongo = '/create_model/add_genes/'
    add_annotation_model = '/create_model/add_annotation/'
    add_gprs_model = '/create_model/add_gprs/'
    add_comparts_model = '/create_model/add_compartments/'
    add_new_reactions_mongo = '/create_model/newreactions/'
    add_new_reactions_neo = '/create_model/newreactions_neo/'
    reactions_from_model = '/list/reactions/model/'
    metabolites_from_model = '/list/metabolites/model/'
    model_detail = '/detail/metabolicmodel/'
    reaction_detail = '/detail/reaction/'
    pathway_detail = '/detail/pathway/'
    metabolite_detail = '/detail/metabolite/'
    organism_detail = '/detail/organism/'
    enzyme_detail = '/detail/enzyme/'
    reaction_list = '/list/reactions/'
    pathway_list = '/list/pathways/'
    metabolite_list = '/list/metabolites/'
    organism_list = '/list/organisms/'
    enzyme_list = '/list/enzymes/'
    gene_list = '/list/genes/'
