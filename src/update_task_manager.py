import os
import subprocess

from background_task import background
import luigi
from transformer import TransformerMetabolite, TransformerReaction, TransformerEnzyme, TransformerGene, \
    TransformerPathway, TransformerOrganism
from iplants_mongo.mongodb_update import DatabaseMongoUpdate
from iplants_neo.neodb_update import DatabaseNeoUpdate
from download_database import DownloadPMNDatabase
import logging
from utils.config import PROJECT_PATH

logging.basicConfig(level=logging.DEBUG)


class DownloadData(luigi.Task):
    db = luigi.Parameter()
    version = luigi.Parameter()

    @property
    def db_version(self):
        return str(self.db) + '_' + str(self.version)

    def requires(self):
        return None

    def output(self):
        output_file = os.path.join(PROJECT_PATH, 'update_outputs', self.db_version + '_downloaded.txt')
        return luigi.LocalTarget(output_file)

    def run(self):
        if self.db not in ['biocyc', 'metacyc']:
            db = DownloadPMNDatabase(db_name=self.db, version=self.version)
            db.download()
        else:
            # db = DownloadMetaDatabase(db_name=self.db, version=self.version)
            logging.info('Download of metacyc or biocyc databases requires paid subscription since Jan 1st 2024')


class TransformData(luigi.Task):
    db = luigi.Parameter()
    version = luigi.Parameter()

    @property
    def db_version(self):
        return str(self.db) + '_' + str(self.version)

    def requires(self):
        # return DownloadData(db=self.db, version=self.version)
        return None

    def output(self):
        output_file = os.path.join(PROJECT_PATH, 'update_outputs', 'transformed_' + self.db_version + '.txt')
        return luigi.LocalTarget(output_file)

    def run(self):
        if self.db not in ['biocyc', 'metacyc']:
            data_path = os.path.join(PROJECT_PATH, 'downloads', str(self.db), str(self.db), str(self.version),
                                     'data')
        else:
            data_path = os.path.join(PROJECT_PATH, 'downloads', str(self.db), str(self.version), 'data')

        transfmet = TransformerMetabolite(data_path=data_path, db_version=self.db_version)
        transfmet.transform()

        transfreac = TransformerReaction(data_path=data_path, db_version=self.db_version)
        transfreac.transform()

        transfenz = TransformerEnzyme(data_path=data_path, db_version=self.db_version)
        transfenz.transform()

        transgene = TransformerGene(data_path=data_path, db_version=self.db_version)
        transgene.transform()

        transpath = TransformerPathway(data_path=data_path, db_version=self.db_version)
        transpath.transform()

        transorg = TransformerOrganism(data_path=data_path, db_version=self.db_version)
        transorg.transform()

        logging.info('New data is transformed and json files were created for each collection')

        with self.output().open('w') as outfile:
            outfile.write('data was transformed into json files')


class LoadDataMongo(luigi.Task):
    db = luigi.Parameter()
    version = luigi.Parameter()

    @property
    def db_version(self):
        return str(self.db) + '_' + str(self.version)

    def requires(self):
        return TransformData(version=self.version, db=self.db)

    def output(self):
        output_file = os.path.join(PROJECT_PATH, 'update_outputs',
                                   'updatemongo_output_' + self.db_version + '.txt')
        return luigi.LocalTarget(output_file)

    def run(self):
        database = DatabaseMongoUpdate(db_version=self.db_version)
        database.update_all_collections()


class LoadDataNeo4j(luigi.Task):
    db = luigi.Parameter()
    version = luigi.Parameter()

    @property
    def db_version(self):
        return str(self.db) + '_' + str(self.version)

    def requires(self):
        return TransformData(db=self.db, version=self.version)

    def output(self):
        output_file = os.path.join(PROJECT_PATH, 'update_outputs', 'updateneo4j_' + self.db_version + '.txt')
        return luigi.LocalTarget(output_file)

    def run(self):
        database = DatabaseNeoUpdate(db_version=self.db_version)
        database.update_database()


@background()
def execute_update_pipeline(dbname, version):
    p = subprocess.Popen('luigid', stdout=subprocess.PIPE, shell=False)
    logging.info('starting the update pipeline')
    luigi.build([LoadDataMongo(db=dbname, version=version), LoadDataNeo4j(db=dbname, version=version)])
    p.kill()

# if __name__ == '__main__':
# luigi.build([LoadDataNeo4j(cyc_folder=meta_cyc, version='metacyc_26.0', json_path=meta_path)])
# luigi.build([LoadDataMongo(db='plantcyc', version=14.0)])
# luigi.build([LoadDataNeo4j(db='metacyc', version=26.1)])
# luigi.build([TransformData(db='metacyc', version='26.1')])
# execute_update_pipeline(dbname='plantcyc', version=14.0)
