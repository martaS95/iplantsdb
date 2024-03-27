import json
import logging
import os
from abc import ABCMeta, abstractmethod
import datetime
from neomodel import config
from mongoengine import connect, DoesNotExist
from iplants_mongo.models import MetabolicModel as MetabolicModelMongo
from iplants_mongo.models import Metabolite as MetaboliteMongo
from iplants_mongo.models import Reaction as ReactionMongo
from iplants_neo.models import MetabolicModel as MetabolicModelNeo
from iplants_neo.models import Metabolite as MetaboliteNeo
from iplants_neo.models import Reaction as ReactionNeo
from iplants_neo.models import Organism
from utils.config import Mongo, Neo, PROJECT_PATH

logging.basicConfig(level=logging.DEBUG)


class ModelIntegration(metaclass=ABCMeta):
    """
    Abstract class for integration of plant metabolic models into the database
    """
    def __init__(self, modelid: str, organism: str, taxid: int, year: int, author: str, metabolite_json: str,
                 reaction_json: str):
        """
        A modelintegration class must implement the integrate_metabolites, integrate_reactios and integrate_all methods
        that will integrate the metabolites and reactions of plant metabolic models into the database.
        Parameters
        ----------
        modelid: str
            the identifier for the metabolic model
        organism: str
            the name of the organism of the metabolic model
        taxid: int
            the taxonomy id of the organism
        year: int
            the year the metabolic model was reconstructed
        author: str
            the name of the first author who reconstructed the model
        metabolite_json: str
            json file with the metabolites in the metabolic model
        reaction_json: str
            json file with the reactions in the metabolic model
        """

        self.modelid = modelid
        self.organism = organism
        self.taxid = taxid
        self.year = year
        self.author = author
        self.metabolites = metabolite_json
        self.reactions = reaction_json

        project_path = PROJECT_PATH
        self.input_folder = os.path.join(project_path, 'model_jsons')

    @abstractmethod
    def create_MetabolicModel(self):
        """
        Abstract method to create the object for the Metabolic Model in the database
        Returns
        -------
        """
        pass

    @abstractmethod
    def integrate_metabolites(self):
        """
        Abstract method to integrate the metabolites of the model
        Returns
        -------
        """
        pass

    @abstractmethod
    def integrate_reactions(self):
        """
        Abstract method to integrate the reactions of the model
        Returns
        -------
        """
        pass

    @abstractmethod
    def integrate_model(self):
        """
        Abstract method to integrate the metabolites and reactions of the model, running the two methods:
        integrate_metabolites and integrate_reactions
        Returns
        -------
        """
        pass


class ModelIntegrationNeo(ModelIntegration):
    """
    Class to integrate the metabolic models into neo4j
    It takes two addional arguments (username and password) which are the credentials to access the database
    """

    def __init__(self, modelid: str, organism: str, taxid: int, year: int, author: str, metabolite_json: str,
                 reaction_json: str):

        super(ModelIntegrationNeo, self).__init__(modelid, organism, taxid, year, author, metabolite_json,
                                                  reaction_json)

        neodb = Neo()

        neo4j_url = "bolt://" + neodb.username + ':' + neodb.password + '@' + neodb.host + ':' + str(neodb.port)
        config.DATABASE_URL = neo4j_url

    def create_MetabolicModel(self):
        """
        Method to create the node for the Metabolic Model
        Returns
        -------

        """
        try:
            MetabolicModelNeo.nodes.get(model_id=self.modelid)
            logging.info('The node for the metabolic model ' + self.modelid + ' already exists!')

        except MetabolicModelNeo.DoesNotExist:
            mm_node = MetabolicModelNeo(model_id=self.modelid, organism=self.organism, taxid=self.taxid, year=self.year,
                                        author=self.author)

            org_node = Organism.nodes.get(taxid=self.taxid)
            mm_node.belongs_to.connect(org_node)
            mm_node.save()

            logging.info('The node for the metabolic model ' + self.modelid + ' was created!')

    def integrate_metabolites(self):
        file_path = os.path.join(self.input_folder, self.metabolites)

        file_f = open(file_path, 'r')
        mets = json.load(file_f)

        for met in mets:
            model_met = MetaboliteNeo(entry_id=met['entry_id'])

            if 'common_name' in met:
                model_met.name = met['common_name']

            try:
                met_node = MetaboliteNeo.nodes.get(entry_id=model_met.entry_id)

            except MetaboliteNeo.DoesNotExist:
                met_node = model_met
                met_node.save()

            mm_node = MetabolicModelNeo.nodes.get(model_id=self.modelid)
            mm_node.metabolites.connect(met_node)

        logging.info('The metabolites of the model ' + self.modelid + ' were integrated into the database')

    def integrate_reactions(self):
        file_path = os.path.join(self.input_folder, self.reactions)

        file_f = open(file_path, 'r')
        reacs = json.load(file_f)

        for reac in reacs:
            model_reac = ReactionNeo(entry_id=reac["entry_id"])

            if 'common_name' in reac:
                model_reac.name = reac['common_name']

            try:
                reac_node = ReactionNeo.nodes.get(entry_id=model_reac.entry_id)

            except ReactionNeo.DoesNotExist:
                reac_node = model_reac
                reac_node.save()

                reactants = reac['reactants']
                products = reac['products']

                if reactants:
                    for sub in reactants:
                        met_node = MetaboliteNeo.nodes.get(entry_id=sub)
                        reac_node.reactants.connect(met_node)

                if products:
                    for prod in products:
                        met_node = MetaboliteNeo.nodes.get(entry_id=prod)
                        reac_node.products.connect(met_node)

            mm_node = MetabolicModelNeo.nodes.get(model_id=self.modelid)
            mm_node.reactions.connect(reac_node)

        logging.info('The reactions of the model ' + self.modelid + ' were integrated into the database')

    def integrate_model(self):

        self.create_MetabolicModel()
        self.integrate_metabolites()
        self.integrate_reactions()

        logging.info('The integration of the model ' + self.modelid + ' is complete')


class ModelIntegrationMongo(ModelIntegration):
    """
    Class to integrate the metabolic models into mongodb
    It takes an additional argument (dbname), which represents the name of the mongodb
    """

    def __init__(self, modelid: str, organism: str, taxid: int, year: int, author: str, metabolite_json: str,
                 reaction_json: str):

        super(ModelIntegrationMongo, self).__init__(modelid, organism, taxid, year, author, metabolite_json,
                                                    reaction_json)

        mongodb = Mongo()

        connect(mongodb.database, host=mongodb.host, port=mongodb.port)

    def create_MetabolicModel(self):
        try:
            MetabolicModelMongo.objects.get(model_id=self.modelid)

            logging.info('The instance for the metabolic model ' + self.modelid + ' already exists!')

        except DoesNotExist:
            mm_doc = MetabolicModelMongo(model_id=self.modelid, organism=self.organism, taxid=self.taxid,
                                         year=self.year, author=self.author)
            mm_doc.save()

            logging.info('The instance for the metabolic model ' + self.modelid + ' was created!')

    def integrate_metabolites(self):

        file_path = os.path.join(self.input_folder, self.metabolites)

        file_f = open(file_path, 'r')
        mets_list = json.load(file_f)

        model_mets = []

        for met in mets_list:
            model_met = MetaboliteMongo(**met)
            model_mets.append(model_met.entry_id)

            try:
                met_doc = MetaboliteMongo.objects.get(entry_id=model_met.entry_id)
                met_doc.models[self.modelid] = model_met["models"][self.modelid]
                met_doc.timestamp = datetime.datetime.now()
                met_doc.save()

            except DoesNotExist:
                model_met.save()

        mm_model = MetabolicModelMongo.objects.get(model_id=self.modelid)
        mm_model.metabolites = model_mets
        mm_model.timestamp = datetime.datetime.now()
        mm_model.save()

        logging.info('The metabolites of the model ' + self.modelid + ' were integrated into the mongo database')

    def integrate_reactions(self):
        file_path = os.path.join(self.input_folder, self.reactions)

        file_f = open(file_path, 'r')
        reacs_list = json.load(file_f)

        model_reacs = []

        for reac in reacs_list:
            model_reac = ReactionMongo(**reac)
            model_reacs.append(model_reac.entry_id)

            try:
                reac_doc = ReactionMongo.objects.get(entry_id=model_reac.entry_id)
                reac_doc.models[self.modelid] = model_reac["models"][self.modelid]
                reac_doc.timestamp = datetime.datetime.now()
                reac_doc.save()

            except DoesNotExist:
                model_reac.save()

        mm_model = MetabolicModelMongo.objects.get(model_id=self.modelid)
        mm_model.reactions = model_reacs
        mm_model.timestamp = datetime.datetime.now()
        mm_model.save()

        logging.info('The reactions of the model ' + self.modelid + ' were integrated into the mongo database')

    def integrate_model(self):
        self.create_MetabolicModel()
        self.integrate_metabolites()
        self.integrate_reactions()

        logging.info('The integration of the model ' + self.modelid + ' to mongo database is complete')


if __name__ == '__main__':
    pass

    # # # FILES # # #
    # metjson = 'athaliana_cheung13_mets.json'
    # rsjson = 'athaliana_cheung13_reacs.json'

    # metjson = 'athaliana2009_mets.json'
    # rsjson = 'athaliana2009_reacs.json'

    # metjson = 'maize2016_mets.json'
    # rsjson = 'maize2016_reacs.json'

    # metjson = 'medicago2018_mets.json'
    # rsjson = 'medicago2018_reacs.json'

    # metjson = 'rice2013_mets.json'
    # rsjson = 'rice2013_reacs.json'

    # metjson = 'rice2017_mets.json'
    # rsjson = 'rice2017_reacs.json'

    # metjson = 'setaria2019_mets.json'
    # rsjson = 'setaria2019_reacs.json'

    # metjson = 'soybean2019_mets.json'
    # rsjson = 'soybean2019_reacs.json'

    # metjson = 'tomato2015_mets.json'
    # rsjson = 'tomato2015_reacs.json'

    # metjson = 'vvinif2023_mets.json'
    # rsjson = 'vvinif2023_reacs.json'

    # # # MAIZE 2016 # # #

    # mongo = ModelIntegrationMongo(modelid='maize2016', organism='Zea mays', taxid=4577, year=2016,
    #                               author='Bogart', metabolite_json=metjson, reaction_json=rsjson)

    # mongo.integrate_model()
    # mongo.integrate_reactions()

    # neo = ModelIntegrationNeo(modelid='maize2016', organism='Zea mays', taxid=4577,  year=2016, author='Bogart',
    #                           metabolite_json=metjson, reaction_json=rsjson)
    # neo.integrate_model()

    # # # MEDICAGO 2018 # # #

    # mongo = ModelIntegrationMongo(modelid='medicago2018', organism='Medicago truncatula', taxid=3880, year=2018,
    #                               author='Pfau', metabolite_json=metjson, reaction_json=rsjson)
    # mongo.integrate_model()
    # mongo.integrate_reactions()

    # neo = ModelIntegrationNeo(modelid='medicago2018', organism='Medicago truncatula', taxid=3880, year=2018,
    #                           author='Pfau', metabolite_json=metjson, reaction_json=rsjson)
    # neo.integrate_model()

    # # # TOMATO 2015 # # #
    #
    # mongo = ModelIntegrationMongo(modelid='tomato2015', organism='Solanum lycopersicum', taxid=4577, year=2015,
    #                               author='Yuan', metabolite_json=metjson, reaction_json=rsjson)
    # mongo.integrate_model()
    # mongo.integrate_reactions()

    # neo = ModelIntegrationNeo(modelid='tomato2015', organism='Solanum lycopersicum', taxid=4577, year=2015,
    #                           author='Yuan', metabolite_json=metjson, reaction_json=rsjson)
    #
    # neo.integrate_model()

    # # # ATHALIANA 2009 # # #

    # mongo = ModelIntegrationMongo(modelid='athaliana2009', organism='Arabidopsis thaliana', taxid=3702, year=2009,
    #                               author='Poolman', metabolite_json=metjson, reaction_json=rsjson)
    # mongo.integrate_reactions()
    #
    # mongo.integrate_model()

    # neo = ModelIntegrationNeo(modelid='athaliana2009', organism='Arabidopsis thaliana', taxid=3702, year=2009,
    #                           author='Poolman', metabolite_json=metjson, reaction_json=rsjson)
    #
    # neo.integrate_model()

    # # # ATHALIANA 2013 # # #

    # mongo = ModelIntegrationMongo(modelid='athaliana2013', organism='Arabidopsis thaliana', taxid=3702, year=2013,
    #                               author='Cheung', metabolite_json=metjson, reaction_json=rsjson)
    # mongo.integrate_reactions()
    #
    # mongo.integrate_model()

    # neo = ModelIntegrationNeo(modelid='athaliana2013', organism='Arabidopsis thaliana', taxid=3702, year=2013,
    #                           author='Cheung', metabolite_json=metjson, reaction_json=rsjson)
    #
    # neo.integrate_model()

    # # # RICE 2013 # # #

    # mongo = ModelIntegrationMongo(modelid='rice2013', organism='Oryza sativa', taxid=4530, year=2013,
    #                               author='Poolman', metabolite_json=metjson, reaction_json=rsjson)
    # mongo.integrate_reactions()
    #
    # mongo.integrate_model()

    # neo = ModelIntegrationNeo(modelid='rice2013', organism='Oryza sativa', taxid=4530, year=2013,
    #                           author='Poolman', metabolite_json=metjson, reaction_json=rsjson)
    #
    # neo.integrate_model()

    # # # RICE 2017 # # #

    # mongo = ModelIntegrationMongo(modelid='rice2017', organism='Oryza sativa', taxid=4530, year=2017,
    #                               author='Chatterjee', metabolite_json=metjson, reaction_json=rsjson)
    # mongo.integrate_reactions()

    # mongo.integrate_model()

    # neo = ModelIntegrationNeo(modelid='rice2017', organism='Oryza sativa', taxid=4530, year=2017,
    #                           author='Chatterjee', metabolite_json=metjson, reaction_json=rsjson)
    #
    # neo.integrate_model()

    # # # SOYBEAN 2019 # # #

    # mongo = ModelIntegrationMongo(modelid='soybean2019', organism='Glycine max', taxid=3847, year=2019,
    #                               author='Moreira', metabolite_json=metjson, reaction_json=rsjson)
    # mongo.integrate_reactions()

    # mongo.integrate_model()

    # neo = ModelIntegrationNeo(modelid='soybean2019', organism='Glycine max', taxid=3847, year=2019,
    #                           author='Moreira', metabolite_json=metjson, reaction_json=rsjson)
    #
    # neo.integrate_model()

    # # # SETARIA 2019 # # #

    # mongo = ModelIntegrationMongo(modelid='setaria2019', organism='Setaria viridis', taxid=4556, year=2019,
    #                               author='Shaw', metabolite_json=metjson, reaction_json=rsjson)
    # mongo.integrate_reactions()
    #
    # mongo.integrate_model()
    #
    # neo = ModelIntegrationNeo(modelid='setaria2019', organism='Setaria viridis', taxid=4556, year=2019,
    #                           author='Shaw', metabolite_json=metjson, reaction_json=rsjson)
    #
    # neo.integrate_model()
