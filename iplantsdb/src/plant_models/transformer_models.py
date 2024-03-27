import os
import json
import logging
import pandas as pd
from cobra.io import read_sbml_model
from utils.config import PROJECT_PATH
from utils.extract import get_reac_rev_xml

logging.basicConfig(level=logging.DEBUG)


class TransformModels:

    def __init__(self, modelid: str, modelfile: str, met_csvfile: str, met_jsonfile: str, met_map: str,
                 reac_csvfile: str, reac_jsonfile: str):
        """
        Class for transforming data of plant metabolic models into csvs and jsons
        Parameters
        ----------
        modelid: str
            identifier of the model
        modelfile: str
            name of the sbml / xml file of the model
        met_csvfile: str
            name of the csv file where to save metabolite info
        met_jsonfile: str
            name of the json file where to save metabolite info
        met_map: str
            name of the json file where to save the mapping between metabolite identifiers in the model and database
            identifiers
        reac_csvfile: str
            name of the csv file where to save reaction info
        reac_jsonfile: str
            name of the json file where to save reaction info
        """
        self.modelid = modelid
        self.modelfile = os.path.join(PROJECT_PATH, 'model_files', modelfile)
        self.met_csv = os.path.join(PROJECT_PATH, 'model_files', met_csvfile)
        self.met_json = os.path.join(PROJECT_PATH, 'model_jsons', met_jsonfile)
        self.met_map = os.path.join(PROJECT_PATH, 'model_files', met_map)
        self.reac_csv = os.path.join(PROJECT_PATH, 'model_files', reac_csvfile)
        self.reac_json = os.path.join(PROJECT_PATH, 'model_jsons', reac_jsonfile)

    def create_mets_csv(self):
        """
        Creates a CSV file with metabolite info from the model, including metabolite identifiers in the model, name,
        compartment and formula. Then, a manual analysis is required to include in this CSV file a column with
        biocyc identifiers
        """
        model = read_sbml_model(self.modelfile)

        lista = []
        for met in model.metabolites:
            line = [met.id, met.name, met.compartment, met.formula]
            lista.append(line)

        df = pd.DataFrame(lista, columns=['model_id', 'name', 'compartment', 'formula'])
        df.to_csv(self.met_csv)

    def create_mets_json(self):
        """
        Creates a JSON file with metabolite info from the CSV file. This CSV needs to be manually completed
        to include biocyc identifiers. Only after including that column manually is possible to execute this function.
        """
        met_summary = pd.read_csv(self.met_csv, encoding="ISO-8859-1")
        mets_info = []
        ids = []

        try:
            met_summary['biocyc']
        except KeyError:
            return

        mapping_ids = {}

        for ind, row in met_summary.iterrows():
            met_info = {}
            if not isinstance(row['biocyc'], float):
                entry_id = row['biocyc']
            else:
                entry_id = row['other']

            metid_in_model = row['model_id']
            compartment = row['compartment']

            mapping_ids[metid_in_model] = entry_id

            if entry_id not in ids:

                met_info['entry_id'] = entry_id

                if not isinstance(row['name'], float):
                    met_info['common_name'] = row['name']

                if not isinstance(row['formula'], float):
                    met_info['formula'] = row['formula']

                if not isinstance(row['inchi'], float):
                    met_info['inchi'] = row['inchi']

                if not isinstance(row['smiles'], float):
                    met_info['smiles'] = row['smiles']

                if not isinstance(row['kegg'], float):
                    met_info['crossrefs'] = {'LIGAND-CPD': row['kegg']}

                met_info['models'] = {self.modelid: {metid_in_model: compartment}}

                mets_info.append(met_info)

                ids.append(entry_id)

            else:
                obj = [elem for elem in mets_info if elem["entry_id"] == entry_id][0]
                obj["models"][self.modelid][metid_in_model] = compartment

        fic_json = open(self.met_json, 'w')
        json.dump(mets_info, fic_json)

        fic_json = open(self.met_map, 'w')
        json.dump(mapping_ids, fic_json)

        logging.info('metabolite data in the model was transformed')

    def create_reacs_csv(self, bounds=False):
        """
        Creates a CSV file with reaction info from the model, including reaction identifiers in the model, name,
        direction, bounds, reactants, and products. Then, a manual analysis is performed and this CSV file will
        include a column with biocyc identifiers for the reactions
        """
        model = read_sbml_model(self.modelfile)

        map_file = open(self.met_map, 'r')
        mets_map = json.load(map_file)

        if not bounds:
            reac_rev = get_reac_rev_xml(self.modelfile)
        else:
            reac_rev = None

        lista = []
        for reac in model.reactions:
            if reac.id not in model.exchanges:
                new_reactants = {}
                new_products = {}
                for met in reac.metabolites:
                    new_id = mets_map[met.id]

                    if reac.metabolites[met] < 0:
                        new_reactants[new_id] = reac.metabolites[met]
                    else:
                        new_products[new_id] = reac.metabolites[met]

                if not bounds:
                    if reac_rev[reac.id] == 'true':
                        lower_bound = -10000
                        rev = 'REVERSIBLE'
                    else:
                        lower_bound = 0
                        rev = 'IRREVERSIBLE'
                    upper_bound = 10000
                else:
                    lower_bound = reac.bounds[0]
                    upper_bound = reac.bounds[1]

                    if reac.reversibility:
                        rev = 'REVERSIBLE'
                    else:
                        rev = 'IRREVERSIBLE'

                line = [reac.id, reac.name, rev, lower_bound, upper_bound, new_reactants, new_products]
                lista.append(line)

        df = pd.DataFrame(lista, columns=['model_id', 'name', 'direction', 'lower_bound', 'upper_bound',
                                          'reactants', 'products'])
        df.to_csv(self.reac_csv)

    def create_reacs_json(self):
        """
        Creates a JSON file with reaction info from the CSV file. This CSV is manually completed to include biocyc
        identifiers. Only after including that column manually is possible to execute this function.
        """
        reac_summary = pd.read_csv(self.reac_csv, encoding="ISO-8859-1")
        reacs_info = []
        ids = []

        try:
            reac_summary['biocyc']
        except KeyError:
            return

        for ind, row in reac_summary.iterrows():
            reac_info = {}
            if not isinstance(row['biocyc'], float):
                entry_id = row['biocyc']
            else:
                entry_id = row['other']

            reac_in_model = row['model_id']
            compartment = row['compartment']

            if entry_id not in ids:

                reac_info['entry_id'] = entry_id

                if not isinstance(row['name'], float):
                    reac_info['common_name'] = row['name']

                if not isinstance(row['direction'], float):
                    reac_info['direction'] = row['direction']

                if not isinstance(row['ECnumber'], float):
                    reac_info['ecnumber'] = row['ECnumber']

                if not isinstance(row['lower_bound'], float):
                    reac_info['lower_bound'] = row['lower_bound']

                if not isinstance(row['upper_bound'], float):
                    reac_info['upper_bound'] = row['upper_bound']

                if not isinstance(row['reactants'], float):
                    reac_info['reactants'] = json.loads(row['reactants'].replace("\'", "\""))

                if not isinstance(row['products'], float):
                    reac_info['products'] = json.loads(row['products'].replace("\'", "\""))

                if not isinstance(row['kegg'], float):
                    reac_info['crossrefs'] = {'LIGAND-RXN': row['kegg']}

                reac_info['models'] = {self.modelid: {reac_in_model: compartment}}

                reacs_info.append(reac_info)

                ids.append(entry_id)

            else:
                obj = [elem for elem in reacs_info if elem["entry_id"] == entry_id][0]
                obj["models"][self.modelid][reac_in_model] = compartment

        fic_json = open(self.reac_json, 'w')
        json.dump(reacs_info, fic_json)

        logging.info('reaction data in the model was transformed')


# if __name__ == "__main__":
    # models_dir = os.path.join(PROJECT_PATH, 'model_files')
    # models_dir = os.path.join(PROJECT_PATH, 'reconstruction_results', 'vvinif2023')

    # model_id = 'athaliana2013'
    # model_file = 'Athaliana_cheung13.xml'
    # csv_mets_file = 'athaliana_cheung13_mets.csv'
    # mets_map_file = 'athaliana_cheung13_metps_map.json'
    # csv_reac_file = 'athaliana_cheung13_reacs.csv'
    # json_mets = 'athaliana_cheung13_mets.json'
    # json_reacs = 'athaliana_cheung13_reacs.json'
    # model_cls = TransformModels(modelid=model_id, modelfile=model_file, met_csvfile=csv_mets_file,
    #                             met_jsonfile=json_mets, reac_csvfile=csv_reac_file, reac_jsonfile=json_reacs,
    #                             met_map=mets_map_file)
    # model_cls.create_mets_json()

    # model_id = 'athaliana2009'
    # model_file = os.path.join(models_dir, 'Athaliana_Poolman2009.xml')
    # csv_mets_file = os.path.join(models_dir, 'athaliana2009_mets.csv')
    # mets_map_file = os.path.join(models_dir, 'athaliana2009_mets_map.json')
    # csv_reac_file = os.path.join(models_dir, 'athaliana2009_reacs.csv')
    # json_mets = os.path.join(models_dir, 'athaliana2009_mets.json')
    # json_reacs = os.path.join(models_dir, 'athaliana2009_reacs.json')

    # model_id = 'rice2013'
    # model_file = os.path.join(models_dir, 'Rice_Poolman.sbml')
    # csv_mets_file = os.path.join(models_dir, 'rice2013_mets.csv')
    # mets_map_file = os.path.join(models_dir, 'rice2013_mets_map.json')
    # csv_reac_file = os.path.join(models_dir, 'rice2013_reacs.csv')
    # json_mets = os.path.join(models_dir, 'rice2013_mets.json')
    # json_reacs = os.path.join(models_dir, 'rice2013_reacs.json')

    # model_id = 'rice2017'
    # model_file = os.path.join(models_dir, 'Rice_OSI1136.sbml')
    # csv_mets_file = os.path.join(models_dir, 'rice2017_mets.csv')
    # mets_map_file = os.path.join(models_dir, 'rice2017_mets_map.json')
    # csv_reac_file = os.path.join(models_dir, 'rice2017_reacs.csv')
    # json_mets = os.path.join(models_dir, 'rice2017_mets.json')
    # json_reacs = os.path.join(models_dir, 'rice2017_reacs.json')

    # model_id = 'tomato2015'
    # model_file = os.path.join(models_dir, 'tomato.xml')
    # csv_mets_file = os.path.join(models_dir, 'tomato2015_mets.csv')
    # mets_map_file = os.path.join(models_dir, 'tomato2015_mets_map.json')
    # csv_reac_file = os.path.join(models_dir, 'tomato2015_reacs.csv')
    # json_mets = os.path.join(models_dir, 'tomato2015_mets.json')
    # json_reacs = os.path.join(models_dir, 'tomato2015_reacs.json')

    # model_id = 'maize2016'
    # model_file = os.path.join(models_dir, 'Maize_iEB5204.xml')
    # csv_mets_file = os.path.join(models_dir, 'maize2016_mets.csv')
    # mets_map_file = os.path.join(models_dir, 'maize2016_mets_map.json')
    # csv_reac_file = os.path.join(models_dir, 'maize2016_reacs.csv')
    # json_mets = os.path.join(models_dir, 'maize2016_mets.json')
    # json_reacs = os.path.join(models_dir, 'maize2016_reacs.json')

    # model_id = 'soybean2019'
    # model_file = os.path.join(models_dir, 'Soybean_GSMM.xml')
    # csv_mets_file = os.path.join(models_dir, 'soybean2019_mets.csv')
    # mets_map_file = os.path.join(models_dir, 'soybean2019_mets_map.json')
    # csv_reac_file = os.path.join(models_dir, 'soybean2019_reacs.csv')
    # json_mets = os.path.join(models_dir, 'soybean2019_mets.json')
    # json_reacs = os.path.join(models_dir, 'soybean2019_reacs.json')

    # model_id = 'medicago2018'
    # model_file = 'MedicagoTruncatula.xml'
    # csv_mets_file = 'medicago2018_mets.csv'
    # mets_map_file = 'medicago2018_mets_map.json'
    # csv_reac_file = 'medicago2018_reacs.csv'
    # json_mets = 'medicago2018_mets.json'
    # json_reacs = 'medicago2018_reacs.json'
    #
    # model_cls = TransformModels(modelid=model_id, modelfile=model_file, met_csvfile=csv_mets_file,
    #                             met_jsonfile=json_mets, reac_csvfile=csv_reac_file, reac_jsonfile=json_reacs,
    #                             met_map=mets_map_file)
    # model_cls.create_reacs_json()

    # model_id = 'setaria2019'
    # model_file = os.path.join(models_dir, 'Setaria_GSMM.xlsx')
    # csv_mets_file = os.path.join(models_dir, 'setaria2019_mets.csv')
    # mets_map_file = os.path.join(models_dir, 'setaria2019_mets_map.json')
    # csv_reac_file = os.path.join(models_dir, 'setaria2019_reacs.csv')
    # json_mets = os.path.join(models_dir, 'setaria2019_mets.json')
    # json_reacs = os.path.join(models_dir, 'setaria2019_reacs.json')

    # create_mets_csv(modelfile=model_file, csvfile=csv_mets_file)
    # create_mets_json(csv_mets_file, model_id, mets_map_file, json_mets)
    # create_reacs_csv(model_file, mets_map_file, csv_reac_file)
    # create_reacs_json(csv_reac_file, model_id, json_reacs)

    # model_id = 'vvinif2023'
    # model_file = 'vvinif2023_FINAL.xml'
    # csv_mets_file = 'vvinif2023_mets.csv'
    # mets_map_file = 'vvinif2023_metps_map.json'
    # csv_reac_file = 'vvinif2023_reacs.csv'
    # json_mets = 'vvinif2023_mets.json'
    # json_reacs = 'vvinif2023_reacs.json'
    # model_cls = TransformModels(modelid=model_id, modelfile=model_file, met_csvfile=csv_mets_file,
    #                             met_jsonfile=json_mets, reac_csvfile=csv_reac_file, reac_jsonfile=json_reacs,
    #                             met_map=mets_map_file)
    # model_cls.create_mets_csv()
    # model_cls.create_mets_json()
    # model_cls.create_reacs_csv(bounds=True)
    # model_cls.create_reacs_json()
