import os
import unittest
from plantdb_neo.DatabaseNeo_update import DatabaseNeo
from transformer import TransformerMetabolite, TransformerReaction, TransformerEnzyme, TransformerPathway, \
    TransformerGene


class PipelineTestCase(unittest.TestCase):

    def testMetabolites_plant(self):
        self.input_data = "C:/Users/BiSBII/Documents/plantdb/tests/data/plant/"
        self.output_dir = "C:/Users/BiSBII/Documents/plantdb_api/tests/data/plant/jsons"

        trnf = TransformerMetabolite(data_path=self.input_data, db_version='plantcyc_15.0',
                                     output_folder=self.output_dir)
        trnf.transform()

        db = DatabaseNeo(db_version='plantcyc_15.0', data_path=self.output_dir, host='palsson.di.uminho.pt', port=1087)

        self.new_data = os.path.join(self.output_dir, 'metabolite.json')

        db.update_metabolite(new_data_file=self.new_data)

    def testMetabolites_meta(self):
        self.input_data = "C:/Users/BiSBII/Documents/plantdb/tests/data/meta/"
        self.output_dir = "C:/Users/BiSBII/Documents/plantdb_api/tests/data/meta/jsons"

        trnf = TransformerMetabolite(data_path=self.input_data, db_version='metacyc_27.0',
                                     output_folder=self.output_dir)
        trnf.transform()

        db = DatabaseNeo(db_version='metacyc_27.0', data_path=self.output_dir, host='palsson.di.uminho.pt', port=1087)

        self.new_data = os.path.join(self.output_dir, 'metabolite.json')

        db.update_metabolite(new_data_file=self.new_data)

    def deleteMetabolites_plant(self):
        self.input_data = 'C:/Users/BiSBII/Documents/Pathway Tools/ptools-local/pgdbs/registry/plantcyc/14.0/data/'
        self.output_dir = "C:/Users/BiSBII/Documents/plantdb_api/tests/data/plant/jsons"

        trnf = TransformerMetabolite(data_path=self.input_data, db_version='plantcyc_14.0',
                                     output_folder=self.output_dir)
        trnf.transform()

        db = DatabaseNeo(db_version='plantcyc_14.0', data_path=self.output_dir, host='palsson.di.uminho.pt', port=1087)

        self.new_data = os.path.join(self.output_dir, 'metabolite.json')

        db.update_metabolite(new_data_file=self.new_data)

    def testReaction_meta(self):
        self.input_data = "C:/Users/BiSBII/Documents/plantdb/tests/data/meta/"
        self.output_dir = "C:/Users/BiSBII/Documents/plantdb_api/tests/data/meta/jsons"

        trnf = TransformerReaction(data_path=self.input_data, db_version='metacyc_27.0',
                                   output_folder=self.output_dir)
        trnf.transform()

        db = DatabaseNeo(db_version='metacyc_27.0', data_path=self.output_dir, host='palsson.di.uminho.pt', port=1087)

        self.new_data = os.path.join(self.output_dir, 'reaction.json')

        db.update_reaction(new_data_file=self.new_data)

    def testReaction_plant(self):
        self.input_data = "C:/Users/BiSBII/Documents/plantdb/tests/data/plant/"
        self.output_dir = "C:/Users/BiSBII/Documents/plantdb_api/tests/data/plant/jsons"

        trnf = TransformerReaction(data_path=self.input_data, db_version='plantcyc_15.0',
                                   output_folder=self.output_dir)
        trnf.transform()

        db = DatabaseNeo(db_version='plantcyc_15.0', data_path=self.output_dir, host='palsson.di.uminho.pt', port=1087)
        #
        self.new_data = os.path.join(self.output_dir, 'reaction.json')
        #
        db.update_reaction(new_data_file=self.new_data)

    def testEnzyme_meta(self):
        self.input_data = "C:/Users/BiSBII/Documents/plantdb/tests/data/meta/"
        self.output_dir = "C:/Users/BiSBII/Documents/plantdb_api/tests/data/meta/jsons"

        trnf = TransformerEnzyme(data_path=self.input_data, db_version='metacyc_27.0',
                                   output_folder=self.output_dir)
        trnf.transform()

        db = DatabaseNeo(db_version='metacyc_27.0', data_path=self.output_dir, host='palsson.di.uminho.pt', port=1087)

        self.new_data = os.path.join(self.output_dir, 'enzymes.json')

        db.update_enzyme(new_data_file=self.new_data)

    def testEnzyme_plant(self):
        self.input_data = "C:/Users/BiSBII/Documents/plantdb/tests/data/plant/"
        self.output_dir = "C:/Users/BiSBII/Documents/plantdb_api/tests/data/plant/jsons"

        trnf = TransformerEnzyme(data_path=self.input_data, db_version='plantcyc_15.0',
                                 output_folder=self.output_dir)
        trnf.transform()

        db = DatabaseNeo(db_version='plantcyc_15.0', data_path=self.output_dir, host='palsson.di.uminho.pt', port=1087)

        self.new_data = os.path.join(self.output_dir, 'enzymes.json')

        db.update_enzyme(new_data_file=self.new_data)

    def testGene_plant(self):
        self.input_data = "C:/Users/BiSBII/Documents/plantdb/tests/data/plant/"
        self.output_dir = "C:/Users/BiSBII/Documents/plantdb_api/tests/data/plant/jsons"

        trnf = TransformerGene(data_path=self.input_data, db_version='plantcyc_15.0',
                               output_folder=self.output_dir)
        trnf.transform()

        db = DatabaseNeo(db_version='plantcyc_15.0', data_path=self.output_dir, host='palsson.di.uminho.pt', port=1087)

        self.new_data = os.path.join(self.output_dir, 'gene.json')

        db.update_gene(new_data_file=self.new_data)

    def testPath_plant(self):
        self.input_data = "C:/Users/BiSBII/Documents/plantdb/tests/data/plant/"
        self.output_dir = "C:/Users/BiSBII/Documents/plantdb_api/tests/data/plant/jsons"

        trnf = TransformerPathway(data_path=self.input_data, db_version='plantcyc_15.0',
                                  output_folder=self.output_dir)
        trnf.transform()

        db = DatabaseNeo(db_version='plantcyc_15.0', data_path=self.output_dir, host='palsson.di.uminho.pt', port=1087)

        self.new_data = os.path.join(self.output_dir, 'pathway.json')

        db.update_pathway(new_data_file=self.new_data)


if __name__ == '__main__':
    unittest.main()
