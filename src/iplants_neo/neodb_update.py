import os
import json
import logging
import datetime
from neomodel import config, match
from iplants_neo.models import Metabolite, Reaction, Enzyme, Gene, Pathway, Organism
from utils.config import PROJECT_PATH, Neo
from utils.extract import files_exist

logging.basicConfig(level=logging.DEBUG)


class DatabaseNeoUpdate:

    def __init__(self, db_version):
        """
        Class to represent the Neo4j database
        Parameters
        ----------
        db_version: Union[str, Parameter]
            version of the cyc database
        """

        self._db_version = db_version

        self.project_path = PROJECT_PATH
        self.datasource = os.path.join(self.project_path, 'json_files', self.db_version)

        neodb = Neo()

        neo4j_url = "bolt://" + neodb.username + ':' + neodb.password + '@' + neodb.host + ':' + str(neodb.port)
        config.DATABASE_URL = neo4j_url

    @property
    def db_version(self) -> str:
        return self._db_version

    @db_version.setter
    def db_version(self, value):
        self._db_version = value

    def update_metabolite(self, new_data_file):
        """
        Update database metabolites with new data. It considers four cenarios:
        1. If the metabolite already exists in the older version of that cyc database, it updates the name attribute
        2. The metabolite does not exist in the older version of that cyc database, but exists in the other cyc
        database (e.g. plantcyc vs metacyc): do nothing.
        3. The metabolite does not exist in the database, it creates a new entry
        4. It updates the state to 'deprecated' of database metabolites that are not in the new version of that database

        Parameters
        ----------
        new_data_file: str
            json file with new metabolite data
        Returns
        -------
        """
        with open(os.path.join(self.datasource, new_data_file)) as json_data:
            data = json.load(json_data)

            new_db = self.db_version.split('_')[0]

            for record in data:
                new_met = Metabolite(entry_id=record['entry_id'])

                if 'common_name' in record:
                    new_met.name = record['common_name']

                new_met.database_version = self.db_version

                try:
                    db_met = Metabolite.nodes.get(entry_id=new_met.entry_id, database_version__startswith=new_db)
                    if hash(new_met) != hash(db_met):
                        db_met.name = new_met.name
                        db_met.timestamp = datetime.datetime.now()
                        db_met.database_version = self.db_version
                        db_met.save()

                except Metabolite.DoesNotExist:

                    try:
                        db_met = Metabolite.nodes.get(entry_id=new_met.entry_id)
                        if not db_met.name and new_met.name:
                            db_met.name = new_met.name
                            db_met.save()
                        if not db_met.database_version:
                            db_met.database_version = self.db_version
                            db_met.save()

                    except Metabolite.DoesNotExist:
                        new_met.save()

                        logging.info('new metabolite ' + new_met.entry_id + ' was inserted in the database')

            new_db_ids = set([rec["entry_id"] for rec in data])

            db_mets = Metabolite.nodes.filter(database_version__startswith=new_db)
            for node in db_mets:
                if node.entry_id not in new_db_ids and not node.state:
                    node.state = 'deprecated'
                elif node.entry_id in new_db_ids and (node.database_version.startswith(new_db) or
                                                      not node.database_version):
                    node.database_version = self.db_version
                node.timestamp = datetime.datetime.now()
                node.save()

        logging.info('update of metabolites is complete')

    def update_reaction(self, new_data_file):
        """
        Update database reactions with new data. It considers four cenarios:
        1. If the reaction already exists in the older version of that cyc database, it updates the name attribute
        and the connections with reactants and products
        2. The reaction does not exist in the older version of that cyc database, but exists in the other cyc
        database (e.g. plantcyc vs metacyc): do nothing.
        3. The reaction does not exist in the database, it creates a new entry
        4. It updates the state to 'deprecated' of database reactions that are not in the new version of that database

        Parameters
        ----------
        new_data_file: str
            json file with new reaction data
        Returns
        -------
        """

        with open(os.path.join(self.datasource, new_data_file)) as json_data:
            data = json.load(json_data)

            new_db = self.db_version.split('_')[0]

            for record in data:
                new_reac = Reaction(entry_id=record['entry_id'])

                print(new_reac.entry_id)

                if 'common_name' in record:
                    new_reac.name = record['common_name']

                new_reac.database_version = self.db_version

                try:
                    db_reac = Reaction.nodes.get(entry_id=new_reac.entry_id, database_version__startswith=new_db)

                    if hash(new_reac) != hash(db_reac):
                        db_reac.name = new_reac.name
                        db_reac.timestamp = datetime.datetime.now()
                        db_reac.database_version = self.db_version
                        db_reac.save()

                    create_reaction_mets_rels(entry_data=record, reac_node=db_reac, replace=True)

                except Reaction.DoesNotExist:

                    try:
                        db_reac = Reaction.nodes.get(entry_id=new_reac.entry_id)
                        if not db_reac.name and new_reac.name:
                            db_reac.name = new_reac.name
                        if not db_reac.database_version:
                            db_reac.database_version = self.db_version
                        db_reac.save()

                        if not db_reac.reactants and not db_reac.products:
                            create_reaction_mets_rels(entry_data=record, reac_node=db_reac)

                    except Reaction.DoesNotExist:
                        new_reac.save()
                        create_reaction_mets_rels(entry_data=record, reac_node=new_reac)
                        logging.info('new reaction ' + new_reac.entry_id + ' was inserted in the database')

            new_db_ids = set([rec["entry_id"] for rec in data])

            db_reacs = Reaction.nodes.filter(database_version__startswith=new_db)
            for node in db_reacs:
                if node.entry_id not in new_db_ids and not node.state:
                    node.state = 'deprecated'
                elif node.entry_id in new_db_ids and (node.database_version.startswith(new_db) or
                                                      not node.database_version):
                    node.database_version = self.db_version
                node.timestamp = datetime.datetime.now()
                node.save()

        logging.info('update of reactions is complete')

    def update_enzyme(self, new_data_file):
        """
        Update database enzymes with new data. It considers four cenarios:
        1. If the enzyme already exists in the older version of that cyc database, it updates the name attribute
        and the connections with reactions and with components
        2. The enzyme does not exist in the older version of that cyc database, but exists in the other cyc
        database (e.g. plantcyc vs metacyc): updates the reaction connections
        3. The enzyme does not exist in the database, it creates a new entry
        4. It updates the state to 'deprecated' of database enzymes that are not in the new version of that database

        Parameters
        ----------
        new_data_file: str
            json file with new enzyme data
        Returns
        -------
        """

        with open(os.path.join(self.datasource, new_data_file)) as json_data:
            data = json.load(json_data)

            new_db = self.db_version.split('_')[0]

            for record in data:
                new_enz = Enzyme(entry_id=record['entry_id'])

                if 'common_name' in record:
                    new_enz.name = record['common_name']

                new_enz.database_version = self.db_version

                try:
                    db_enz = Enzyme.nodes.get(entry_id=new_enz.entry_id, database_version__startswith=new_db)
                    if hash(new_enz) != hash(db_enz):
                        db_enz.name = new_enz.name
                        db_enz.database_version = self.db_version
                        db_enz.timestamp = datetime.datetime.now()
                        db_enz.save()

                    create_enzyme_rels(entry_data=record, enz_node=db_enz, db=new_db)

                except Enzyme.DoesNotExist:
                    pass

                    try:
                        db_enz = Enzyme.nodes.get(entry_id=new_enz.entry_id)
                        if not db_enz.name and new_enz.name:
                            db_enz.name = new_enz.name
                            db_enz.save()
                        if not db_enz.database_version:
                            db_enz.database_version = self.db_version
                            db_enz.save()

                        create_enzyme_rels(entry_data=record, enz_node=db_enz, db=new_db)

                    except Enzyme.DoesNotExist:

                        new_enz.save()

                        create_enzyme_rels(entry_data=record, enz_node=new_enz, db=new_db)

                        new_enz.timestamp = datetime.datetime.now()
                        new_enz.save()

            new_db_ids = set([rec["entry_id"] for rec in data])

            db_enzs = Enzyme.nodes.filter(database_version__startswith=new_db)
            for node in db_enzs:
                if node.entry_id not in new_db_ids and not node.state:
                    node.state = 'deprecated'
                elif node.entry_id in new_db_ids and (node.database_version.startswith(new_db) or
                                                      not node.database_version):
                    node.database_version = self.db_version
                node.timestamp = datetime.datetime.now()
                node.save()

        logging.info('update of enzymes is complete')

    def update_gene(self, new_data_file):
        """
        Update database genes with new data. It considers four cenarios:
        1. If the gene already exists in the older version of that cyc database, it updates the name attribute
        and the connections with enzymes
        2. The gene does not exist in the older version of that cyc database, but exists in the other cyc
        database (e.g. plantcyc vs metacyc): does nothing
        3. The gene does not exist in the database, it creates a new entry
        4. It updates the state to 'deprecated' of database genes that are not in the new version of that database

        Parameters
        ----------
        new_data_file: str
            json file with new gene data
        Returns
        -------
        """
        with open(os.path.join(self.datasource, new_data_file)) as json_data:
            data = json.load(json_data)

            new_db = self.db_version.split('_')[0]

            for record in data:
                new_gene = Gene(entry_id=record['entry_id'])

                if 'common_name' in record:
                    new_gene.name = record['common_name']

                new_gene.database_version = self.db_version

                try:
                    db_gene = Gene.nodes.get(entry_id=new_gene.entry_id, database_version__startswith=new_db)
                    if hash(new_gene) != hash(db_gene):
                        db_gene.name = new_gene.name
                        db_gene.database_version = self.db_version
                        db_gene.timestamp = datetime.datetime.now()
                        db_gene.save()

                    create_gene_rels(entry_data=record, gene_node=db_gene, db=new_db)

                except Gene.DoesNotExist:

                    try:
                        db_gene = Gene.nodes.get(entry_id=new_gene.entry_id)
                        if not db_gene.name and new_gene.name:
                            db_gene.name = new_gene.name
                            db_gene.save()
                        if not db_gene.database_version:
                            db_gene.database_version = self.db_version
                            db_gene.save()

                        create_gene_rels(entry_data=record, gene_node=db_gene, db=new_db)

                    except Gene.DoesNotExist:
                        new_gene.save()

                        create_gene_rels(entry_data=record, gene_node=new_gene, db=new_db)

                        logging.info('new gene ' + new_gene.entry_id + ' was inserted in the database')

            new_db_ids = set([rec["entry_id"] for rec in data])

            db_genes = Gene.nodes.filter(database_version__startswith=new_db)
            for node in db_genes:
                if node.entry_id not in new_db_ids and not node.state:
                    node.state = 'deprecated'
                elif node.entry_id in new_db_ids and (node.database_version.startswith(new_db) or
                                                      not node.database_version):
                    node.database_version = self.db_version

                node.timestamp = datetime.datetime.now()
                node.save()

        logging.info('update of genes is complete')

    def update_pathway(self, new_data_file):
        """
        Update database pathways with new data. It considers four cenarios:
        1. If the pathway already exists in the older version of that cyc database, it updates the name attribute
        and the connections with reactions
        2. The pathway does not exist in the older version of that cyc database, but exists in the other cyc
        database (e.g. plantcyc vs metacyc): does nothing
        3. The pathway does not exist in the database, it creates a new entry
        4. It updates the state to 'deprecated' of database pathways that are not in the new version of that database

        Parameters
        ----------
        new_data_file: str
            json file with new pathway data
        Returns
        -------
        """

        with open(os.path.join(self.datasource, new_data_file)) as json_data:
            data = json.load(json_data)

            new_db = self.db_version.split('_')[0]

            for record in data:
                new_path = Pathway(entry_id=record['entry_id'])

                if 'common_name' in record:
                    new_path.name = record['common_name']

                new_path.database_version = self.db_version

                try:
                    db_path = Pathway.nodes.get(entry_id=new_path.entry_id, database_version__startswith=new_db)
                    if new_path.name and new_path.name != db_path.name:
                        db_path.name = new_path.name
                        db_path.database_version = self.db_version
                        db_path.timestamp = datetime.datetime.now()
                        db_path.save()

                    create_path_rels(entry_data=record, path_node=db_path, db=new_db)

                except Pathway.DoesNotExist:

                    try:
                        db_path = Pathway.nodes.get(entry_id=new_path.entry_id)
                        if not db_path.name and new_path.name:
                            db_path.name = new_path.name
                            db_path.save()
                        if not db_path.database_version:
                            db_path.database_version = self.db_version
                            db_path.save()

                        create_path_rels(entry_data=record, path_node=db_path, db=new_db)

                    except Pathway.DoesNotExist:

                        new_path.save()

                        create_path_rels(entry_data=record, path_node=new_path, db=new_db)

            new_db_ids = set([rec["entry_id"] for rec in data])

            db_paths = Pathway.nodes.filter(database_version__startswith=new_db)
            for node in db_paths:
                if node.entry_id not in new_db_ids and not node.state:
                    node.state = 'deprecated'
                elif node.entry_id in new_db_ids and (node.database_version.startswith(new_db) or
                                                      not node.database_version):
                    node.database_version = self.db_version
                node.timestamp = datetime.datetime.now()
                node.save()

        logging.info('update of pathways is complete')

    def update_database(self):
        """
        update all info in the database
        """

        new_files = ['metabolite.json', 'reaction.json', 'enzyme.json', 'gene.json', 'pathway.json']
        new_files_path = [os.path.join(str(self.datasource), x) for x in new_files]

        check = files_exist(new_files_path)
        if check:
            self.update_metabolite(new_data_file=new_files_path[0])
            self.update_reaction(new_data_file=new_files_path[1])
            self.update_enzyme(new_data_file=new_files_path[2])
            self.update_gene(new_data_file=new_files_path[3])
            self.update_pathway(new_data_file=new_files_path[4])

            message = 'The neo4j database was updated'

        else:
            message = 'Neo4j database cannot be updated. An error has occured. A transformed file is missing'

        outputfile = os.path.join(self.project_path, 'update_outputs',
                                  'updateneo4j_output_' + str(self.db_version) + '.txt')

        with open(outputfile, 'w') as output:
            output.write(message)

        logging.info(message)


def create_reaction_mets_rels(entry_data, reac_node, replace=False):
    if not replace:
        if 'reactants' in entry_data:
            for r in entry_data['reactants']:
                try:
                    r_node = Metabolite.nodes.get(entry_id=r)
                except Metabolite.DoesNotExist:
                    r_node = Metabolite(entry_id=r).save()

                reac_node.reactants.connect(r_node, {'stoichiometry': str(entry_data["reactants"][r])})

            reac_node.timestamp = datetime.datetime.now()
            reac_node.save()

        if 'products' in entry_data:
            for p in entry_data['products'].keys():
                try:
                    p_node = Metabolite.nodes.get(entry_id=p)
                except Metabolite.DoesNotExist:
                    p_node = Metabolite(entry_id=p).save()

                reac_node.products.connect(p_node, {'stoichiometry': str(entry_data["products"][p])})

            reac_node.timestamp = datetime.datetime.now()
            reac_node.save()

    else:
        if 'reactants' in entry_data:
            new_reactants = set(entry_data["reactants"].keys())
            db_reactants = reac_node.reactants.all()
            db_reactants_ids = set([met.entry_id for met in db_reactants])

            if new_reactants != db_reactants_ids:
                new_mets = new_reactants.difference(db_reactants_ids)
                for new_met in new_mets:
                    try:
                        new_met_node = Metabolite.nodes.get(entry_id=new_met)
                    except Metabolite.DoesNotExist:
                        new_met_node = Metabolite(entry_id=new_met).save()

                    reac_node.reactants.connect(new_met_node,
                                                {'stoichiometry': str(entry_data["reactants"][new_met])})

                old_mets = db_reactants_ids.difference(new_reactants)
                for old_met in old_mets:
                    old_met_node = Metabolite.nodes.get(entry_id=old_met)
                    reac_node.reactants.disconnect(old_met_node)

                reac_node.timestamp = datetime.datetime.now()
                reac_node.save()

        if 'products' in entry_data:
            new_products = set(entry_data["products"].keys())
            db_products = entry_data.products.all()
            db_products_ids = set([met.entry_id for met in db_products])

            if new_products != db_products_ids:
                new_prods = new_products.difference(db_products_ids)
                for new_prod in new_prods:
                    try:
                        new_prod_node = Metabolite.nodes.get(entry_id=new_prod)
                    except Metabolite.DoesNotExist:
                        new_prod_node = Metabolite(entry_id=new_prod).save()

                    reac_node.products.connect(new_prod_node,
                                               {'stoichiometry': str(entry_data["products"][new_prod])})

                old_prods = db_products_ids.difference(new_products)
                for old_prod in old_prods:
                    old_prod_node = Metabolite.nodes.get(entry_id=old_prod)
                    reac_node.products.disconnect(old_prod_node)

                reac_node.timestamp = datetime.datetime.now()
                reac_node.save()


def create_enzyme_rels(entry_data, enz_node, db):
    if 'reactions' in entry_data:
        new_reactions = set(entry_data['reactions'][db])
        db_reactions = enz_node.reactions.all()
        db_reactions_ids = set([reac.entry_id for reac in db_reactions])

        if new_reactions != db_reactions_ids:
            new_reacs = new_reactions.difference(db_reactions_ids)
            for new_reac in new_reacs:
                try:
                    new_reac_node = Reaction.nodes.get(entry_id=new_reac)
                except Reaction.DoesNotExist:
                    new_reac_node = Reaction(entry_id=new_reac).save()

                enz_node.reactions.connect(new_reac_node)

            enz_node.timestamp = datetime.datetime.now()
            enz_node.save()

    if 'components' in entry_data:
        new_comps = set(entry_data['components'][db])
        db_components = enz_node.components.all()
        db_components_ids = set([enz.entry_id for enz in db_components])

        if new_comps != db_components_ids:
            new = new_comps.difference(db_components_ids)
            for c in new:
                try:
                    comp_node = Enzyme.nodes.get(entry_id=c)
                except Enzyme.DoesNotExist:
                    comp_node = Enzyme(entry_id=c).save()

                enz_node.components.connect(comp_node, {"number": entry_data['components'][db][c]})

            enz_node.timestamp = datetime.datetime.now()
            enz_node.save()

    if 'organisms' in entry_data:
        for org in entry_data['organisms'][db]:
            try:
                org_node = Organism.nodes.get(entry_id=org)
            except Organism.DoesNotExist:
                org_node = Organism(entry_id=org)
                db = [k + '_' + str(v) for k, v in entry_data["database_version"].items()][0]
                org_node.database_version = db
                org_node.save()

            org_enzs = [enz.entry_id for enz in org_node.enzymes.all()]
            if enz_node.entry_id not in org_enzs:
                org_node.enzymes.connect(enz_node)

                enz_node.timestamp = datetime.datetime.now()
                enz_node.save()


def create_gene_rels(entry_data, gene_node, db):
    if 'enzymes' in entry_data:
        new_enzymes = set(entry_data["enzymes"][db])
        db_enzymes = gene_node.enzymes.all()
        db_enzymes_ids = set([enz.entry_id for enz in db_enzymes])

        if new_enzymes != db_enzymes_ids:
            new_enzs = new_enzymes.difference(db_enzymes_ids)
            for new_enz in new_enzs:
                try:
                    new_enz_node = Enzyme.nodes.get(entry_id=new_enz)
                    definition = dict(node_class=Organism, direction=match.INCOMING, relation_type='ORGANISM_HAS_ENZ')
                    rels_tr = match.Traversal(new_enz_node, Organism.__label__, definition)
                    orgs = rels_tr.all()

                except Enzyme.DoesNotExist:
                    new_enz_node = Enzyme(entry_id=new_enz).save()
                    orgs = []

                gene_node.enzymes.connect(new_enz_node)

                if orgs:
                    for org_node in orgs:
                        org_genes = [gene.entry_id for gene in org_node.genes.all()]
                        if gene_node.entry_id not in org_genes:
                            org_node.genes.connect(gene_node)

                    gene_node.timestamp = datetime.datetime.now()
                    gene_node.save()

                gene_node.timestamp = datetime.datetime.now()
                gene_node.save()


def create_path_rels(entry_data, path_node, db):
    if 'reactions' in entry_data:
        new_reactions = set(entry_data['reactions'][db])
        db_reactions = path_node.reactions.all()
        db_reactions_ids = set([reac.entry_id for reac in db_reactions])

        if new_reactions != db_reactions_ids:
            new_reacs = new_reactions.difference(db_reactions_ids)
            for new_reac in new_reacs:
                try:
                    new_reac_node = Reaction.nodes.get(entry_id=new_reac)
                except Reaction.DoesNotExist:
                    new_reac_node = Reaction(entry_id=new_reac).save()

                path_node.reactions.connect(new_reac_node)

            path_node.timestamp = datetime.datetime.now()
            path_node.save()

    if 'organisms' in entry_data:
        for org in entry_data['organisms'][db]:
            try:
                org_node = Organism.nodes.get(entry_id=org)
            except Organism.DoesNotExist:
                org_node = Organism(entry_id=org)
                db = [k + '_' + str(v) for k, v in entry_data["database_version"].items()][0]
                org_node.database_version = db
                org_node.save()

            org_paths = [path.entry_id for path in org_node.pathways.all()]
            if path_node.entry_id not in org_paths:
                org_node.pathways.connect(path_node)

                path_node.timestamp = datetime.datetime.now()
                path_node.save()


# if __name__ == '__main__':
#     neo = Neo()
#     neo4j_url = "bolt://" + neo.username + ':' + neo.password + '@' + neo.host + ':' + str(neo.port)
#     config.DATABASE_URL = neo4j_url

    # update_neo = DatabaseNeoUpdate(db_version='plantcyc_14.0')
    # update_neo.update_database()

    # update_meta = DatabaseNeoUpdate(db_version='metacyc_26.1')
    # update_meta.update_database()
