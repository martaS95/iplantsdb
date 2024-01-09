import os
import datetime
import json
import logging

from mongoengine import connect, DoesNotExist
from iplants_mongo.models import Metabolite, Reaction, Enzyme, Gene, Pathway, Organism
from utils.extract import get_sequence_gene, get_uniprot_data, get_tair_protein
from utils.config import PROJECT_PATH, Mongo
from utils.extract import files_exist


logging.basicConfig(level=logging.DEBUG)


class DatabaseMongoUpdate:

    def __init__(self, db_version):
        """
        Class to represent the mongo database
        Parameters
        ----------
        db_version: Union[str, Parameter]
            version of the cyc database
        """

        self.db_version = db_version

        self.collections = [Metabolite, Reaction, Enzyme, Gene, Pathway, Organism]

        self.project_path = PROJECT_PATH
        self.datasource = os.path.join(self.project_path, 'json_files', self.db_version)

        mongodb = Mongo()
        connect(mongodb.database, host=mongodb.host, port=mongodb.port)

    def update_collection(self, new_data_file, collection):
        """
        Update a database collection with new data. It considers three cenarios:
        1. If the entry already exists in the older version of that cyc database, it updates all attributes
        2. The entry does not exist in the older version of that cyc database, but exists in the other cyc database
        (e.g. plantcyc vs metacyc), it updates the crossrefs of all collections, the list of enzymes, genes and
        pathways in the case of Reaction collection and the list of reactions in the case of Enzyme collection.
        3. The entry does not exist in the database, it creates a new entry and if it is an enzymes or gene, it will
        get the sequence at uniprot or ncbi, respectively.
        4. It updates the state to 'deprecated' of the database entries that are not in the new version of that database

        Parameters
        ----------
        new_data_file: str
            json file with new data
        collection:
            the collection class to update
        Returns
        -------
        """
        with open(os.path.join(self.datasource, new_data_file)) as json_data:
            data = json.load(json_data)

            new_db = self.db_version.split('_')[0]

            for record in data:
                new_doc = collection(**record)

                try:
                    db_doc = collection.objects.get(entry_id=new_doc.entry_id)

                    if len(db_doc.database_version) == 1:
                        if new_db in db_doc.database_version:
                            if hash(new_doc) != hash(db_doc):
                                db_doc.update(**record)
                                db_doc.timestamp = datetime.datetime.now()
                                db_doc.save()

                        else:
                            self.integration_function(new_doc=new_doc, db_doc=db_doc, new_db=new_db)
                            db_doc.database_version.update({new_db: self.db_version.split('_')[1]})
                            db_doc.save()

                    else:
                        self.integration_function(new_doc=new_doc, db_doc=db_doc, new_db=new_db)
                        db_doc.database_version.update({new_db: self.db_version.split('_')[1]})
                        db_doc.save()

                        if new_db == 'plantcyc':
                            new_str_attributes = new_doc.str_attributes()
                            new_str_attributes_assigned = {k: v for k, v in new_str_attributes.items() if v is not None}

                            for att in new_str_attributes_assigned:
                                if new_str_attributes_assigned[att] != getattr(db_doc, att):
                                    setattr(db_doc, att, new_str_attributes_assigned[att])
                            db_doc.save()

                            if isinstance(new_doc, Reaction):
                                if new_doc.reactants != db_doc.reactants:
                                    db_doc.reactants = new_doc.reactants
                                if new_doc.products != db_doc.products:
                                    db_doc.products = new_doc.products
                                db_doc.save()

                except DoesNotExist:

                    if isinstance(new_doc, Enzyme) and new_doc.crossrefs:
                        if 'UNIPROT' in new_doc.crossrefs:
                            uniprot_info = get_uniprot_data(protein_id=new_doc.crossrefs['UNIPROT'])
                            if uniprot_info:
                                new_doc.uniprot_product = uniprot_info['uniprot_product']
                                new_doc.uniprot_location = uniprot_info['uniprot_location']
                                new_doc.uniprot_status = uniprot_info['uniprot_status']
                                new_doc.uniprot_function = [uniprot_info['uniprot_function']]
                                new_doc.sequence = uniprot_info['sequence']

                        elif 'TAIR' in new_doc.crossrefs:
                            new_doc.sequence = get_tair_protein(tair_id=new_doc.crossrefs["TAIR"])

                    elif isinstance(new_doc, Gene) and new_doc.crossrefs:
                        ncbi_id = None
                        if 'ENTREZ' in new_doc.crossrefs:
                            ncbi_id = new_doc.crossrefs['ENTREZ']
                        elif 'REFSEQ' in new_doc.crossrefs:
                            ncbi_id = new_doc.crossrefs['REFSEQ']

                        if ncbi_id:
                            seq = get_sequence_gene(ncbi_id=ncbi_id)
                            new_doc.sequence = seq

                    new_doc.save()

            new_db_ids = [rec["entry_id"] for rec in data]

            db_recs = collection.objects.filter(database_version__startswith=new_db)
            for rec in db_recs:
                if rec.entry_id not in new_db_ids and not rec.state:
                    rec.state = 'deprecated'
                elif rec.entry_id in new_db_ids and rec.database_version.startswith(new_db):
                    rec.database_version = self.db_version
                rec.timestamp = datetime.datetime.now()
                rec.save()

        logging.info('The database collection ' + vars(collection)['_class_name'] + ' was updated')

    def update_all_collections(self):
        """
        Update all collections of the database
        """

        new_files = ['metabolite.json', 'reaction.json', 'enzyme.json', 'gene.json', 'pathway.json', 'organism.json']

        new_files_path = [os.path.join(str(self.datasource), x) for x in new_files]

        check = files_exist(new_files_path)
        if check:
            for i in range(len(self.collections)):
                self.update_collection(new_data_file=new_files_path[i], collection=self.collections[i])

            message = 'The mongo database was updated'

        else:
            message = 'Mongodb database cannot be updated. An error has occured. A transformed file is missing'

        outputfile = os.path.join(self.project_path, 'update_outputs',
                                  'updatemongo_output_' + str(self.db_version) + '.txt')

        with open(outputfile, 'w') as output:
            output.write(message)

        logging.info(message)

    @staticmethod
    def integration_function(new_doc, db_doc, new_db):
        try:
            new_list_attributes = new_doc.list_attributes()
            if new_list_attributes:
                new_list_attributes_assigned = {k: v for k, v in new_list_attributes.items() if v != {}}

                for att in new_list_attributes_assigned:
                    if getattr(db_doc, att):
                        try:
                            db_att = getattr(db_doc, att)[new_db]
                            if new_list_attributes_assigned[att] != db_att:
                                getattr(db_doc, att)[new_db] = new_list_attributes_assigned[att][new_db]
                        except KeyError:
                            getattr(db_doc, att)[new_db] = new_list_attributes_assigned[att][new_db]
                db_doc.save()
        except AttributeError:
            pass

        if (not isinstance(new_doc, Pathway) and not isinstance(new_doc, Organism) and
                new_doc.crossrefs != db_doc.crossrefs):
            for key in new_doc.crossrefs:
                if key not in db_doc.crossrefs:
                    db_doc.crossrefs[key] = new_doc.crossrefs[key]
            db_doc.save()

        try:
            new_str_attributes = new_doc.str_attributes()
            if new_str_attributes:
                new_str_attributes_assigned = {k: v for k, v in new_str_attributes.items() if v is not None}

                for att in new_str_attributes_assigned:
                    if getattr(db_doc, att) is None:
                        setattr(db_doc, att, new_str_attributes_assigned[att])
                db_doc.save()
        except AttributeError:
            pass


# if __name__ == '__main__':
#     connect('plantcyc', host='palsson.di.uminho.pt', port=1017)

    # df = pd.read_csv(os.path.join(PROJECT_PATH, 'enzs_with_seq_old.csv'))
    # for ind, row in df.iterrows():
    #     enz_id = row['entry_id']
    #     try:
    #         enz_doc = Enzyme.objects.get(entry_id=enz_id)
    #         if not enz_doc.sequence:
    #             enz_doc.sequence = row['sequence']
    #             enz_doc.save()
    #     except DoesNotExist:
    #         pass
    # update1 = DatabaseMongoUpdate(db_version='plantcyc_14.0')
    # update1.update_all_collections()
