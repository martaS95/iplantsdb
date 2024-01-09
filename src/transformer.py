import os
import re
import logging
from abc import ABCMeta, abstractmethod
from pydantic import BaseModel
from utils.extract import data_by_record, write_json, get_coeffs_reactions, get_enzrxn_data, get_coeffs_complexes, \
    get_enz_type_genes
import taxoniq

logging.basicConfig(level=logging.DEBUG)

from utils.config import PROJECT_PATH
from utils.extract import taxid_biocyc_api


class Metabolite(BaseModel):
    entry_id: str
    common_name: str = None
    synonyms: list = None
    crossrefs: dict = None
    met_type: list = None
    formula: str = None
    inchi: str = None
    inchikey: str = None
    smiles: str = None
    database_version: str = None


class Reaction(BaseModel):
    entry_id: str
    common_name: str = None
    synonyms: list = None
    crossrefs: dict = None
    direction: str = None
    reactants: dict = None
    products: dict = None
    ecnumber: str = None
    lower_bound: float = None
    upper_bound: float = None
    in_pathway: dict = None
    enzymes: dict = None
    genes: dict = None
    reaction_type: str = None
    by_complex: bool = None
    sub_reactions: dict = None
    compartment: dict = None
    database_version: str = None


class Enzyme(BaseModel):
    entry_id: str
    common_name: str = None
    synonyms: list = None
    crossrefs: dict = None
    reactions: dict = None
    genes: dict = None
    organisms: dict = None
    protein_type: str = None
    components: dict = None
    component_of: dict = None
    database_version: str = None
    uniprot_product: str = None
    uniprot_status: str = None
    uniprot_function: str = None
    uniprot_location: list = None
    sequence: str = None


class Gene(BaseModel):
    entry_id: str
    common_name: str = None
    synonyms: list = None
    crossrefs: dict = None
    reactions: dict = None
    enzymes: dict = None
    database_version: str = None
    sequence: str = None


class Pathway(BaseModel):
    entry_id: str
    common_name: str = None
    synonyms: list = None
    reactions: dict = None
    organisms: dict = None
    pathway_links: dict = None
    super_pathways: list = None
    database_version: str = None


class Organism(BaseModel):
    entry_id: str
    common_name: str = None
    scientific_name: str = None
    taxid: int = None
    species: str = None
    genus: str = None
    family: str = None
    order: str = None
    org_class: str = None
    phylum: str = None
    kingdom: str = None
    superkingdom: str = None
    pathways: dict = None
    genes: dict = None
    enzymes: dict = None
    database_version: str = None


class Transformer(metaclass=ABCMeta):
    """
    Abstract base class for all transformers
    """

    def __init__(self, data_path, db_version):
        """
        A transformer must implement the transform method that will transform the data to load to the database.
        The data to transform should in a file enconded in the source attribute.
        The transformed data is saved into a json file

        Parameters
        ----------
        data_path: Union[str, Parameter]
            the json_path of the file containing the information to extract from the cyc database
        db_version: Union[str, Parameter]
            version of the source database (e.g. Plantcyc_15.0)
        """

        self._datasource = data_path
        self._db_version = db_version
        self.db_name = self.db_version.split('_')[0]

        self.project_path = PROJECT_PATH

        self.output_folder = os.path.join(self.project_path, 'json_files', self.db_version)
        if not os.path.isdir(self.output_folder):
            os.mkdir(self.output_folder)

    @property
    def datasource(self) -> str:
        return self._datasource

    @datasource.setter
    def datasource(self, value):
        self._datasource = value

    @property
    def db_version(self) -> str:
        return self._db_version

    @db_version.setter
    def db_version(self, value):
        self._db_version = value

    @abstractmethod
    def transform(self):
        """
        Abstract method to transform the input data into json file to load into the database
        Returns
        -------
        """
        pass


class TransformerMetabolite(Transformer):

    def __init__(self, data_path, db_version):
        """
        Transforms the metabolite data of the cyc database. It reads the compounds.dat file and saves the information
        of each metabolite in a structured Metabolite object.
        Parameters
        ----------
        data_path: Union[str, Parameter]
            the json_path of the compounds.dat file of the cyc database
        db_version: Union[str, Parameter]
            version of the database
        """

        super().__init__(data_path, db_version)

    def transform(self):
        """
        Reads the compounds.dat file to extract the following info and
        writes a json file with metabolite instances:
        - entry_id
        - common_name
        - synonyms
        - crossrefs
        - formula
        - inchi
        - inchikey
        - smiles

        Returns
        -------
        all_metabolites: list
            list of dicts with metabolite information
        """

        filepath = os.path.join(self.datasource, 'compounds.dat')

        data = data_by_record(filepath)

        all_metabolites = []
        for met_dic in data:
            met_id = met_dic['UNIQUE-ID'][0]
            new_met = Metabolite(entry_id=met_id)

            new_met.database_version = {self.db_name: self.db_version.split('_')[1]}

            if 'COMMON-NAME' in met_dic:
                new_met.common_name = re.sub('<[^<]+?>', '', met_dic['COMMON-NAME'][0])

            if 'SYNONYMS' in met_dic:
                new_met.synonyms = [re.sub('<[^<]+?>', '', x) for x in met_dic['SYNONYMS']]

            if 'DBLINKS' in met_dic:
                new_met.crossrefs = {}
                for dblink in met_dic['DBLINKS']:
                    ref = dblink.split('NIL')[0][:-1]
                    db = re.search('\((.*?) ', ref).group()[1:-1]
                    db_id = re.search('"(.*?)"', ref).group()[1:-1]
                    new_met.crossrefs[db] = db_id

            if 'CHEMICAL-FORMULA' in met_dic:
                form = ''.join(met_dic['CHEMICAL-FORMULA']).replace('(', '').replace(')', '').replace(' ', '')
                new_met.formula = form
            if 'INCHI' in met_dic:
                new_met.inchi = met_dic['INCHI'][0]
            if 'INCHI-KEY' in met_dic:
                new_met.inchikey = met_dic['INCHI-KEY'][0]
            if 'SMILES' in met_dic:
                new_met.smiles = met_dic['SMILES'][0]

            if 'TYPES' in met_dic:
                new_met.met_type = met_dic['TYPES']

            new_met_json = new_met.dict()
            new_met_json = {k: v for k, v in new_met_json.items() if v is not None}

            all_metabolites.append(new_met_json)

        output_file = os.path.join(self.output_folder, 'metabolite.json')
        write_json(all_metabolites, output_file)

        logging.info('metabolite data was transformed and ' + output_file + ' was written')

        return all_metabolites


class TransformerReaction(Transformer):

    def __init__(self, data_path, db_version):
        """
        Transforms the reaction data of the cyc database. It reads the reactions.dat file and saves the information
        of each reaction in a structured Reaction object.
        Parameters
        ----------
        data_path: Union[str, Parameter]
            the folder of the reactions.dat file of the cyc database
        db_version: Union[str, Parameter]
            version of the database
        """

        super().__init__(data_path, db_version)

    def transform(self):
        """
        Reads the reactions.dat file to extract the following info and
        writes a json file with reaction instances:
        - entry_id
        - common_name
        - synonyms
        - crossrefs
        - direction
        - reactants
        - products
        - ecnumber
        - reaction_type
        - isozymes
        - by_complex
        - lower_bound
        - upper_bound
        - in_pathway
        - enzymes
        - genes
        - instance reactions
        - sub reactions

        Returns
        -------
        all_reactions: list
            list of dicts with reaction information
        """

        try:
            filepath = os.path.join(self.datasource, 'reactions.dat')
            data = data_by_record(filepath)
        except FileNotFoundError:
            filepath = os.path.join(self.datasource, '#reactions.dat#')
            data = data_by_record(filepath)

        all_reactions = []

        coeffs = get_coeffs_reactions(reac_file=filepath)

        enzs = get_enzrxn_data(db_path=self.datasource, for_rxn=True)

        enz_data = get_enz_type_genes(self.datasource)

        for reac_dic in data:
            reac_id = reac_dic['UNIQUE-ID'][0]
            new_reac = Reaction(entry_id=reac_id)

            new_reac.database_version = {self.db_name: self.db_version.split('_')[1]}

            if 'COMMON-NAME' in reac_dic:
                new_reac.common_name = re.sub('<[^<]+?>', '', reac_dic['COMMON-NAME'][0])

            if 'SYNONYMS' in reac_dic:
                new_reac.synonyms = [re.sub('<[^<]+?>', '', x) for x in reac_dic['SYNONYMS']]

            if 'DBLINKS' in reac_dic:
                new_reac.crossrefs = {}
                for dblink in reac_dic['DBLINKS']:
                    ref = dblink.split('NIL')[0][:-1]
                    db = re.search('\((.*?) ', ref).group()[1:-1]
                    db_id = re.search('"(.*?)"', ref).group()[1:-1]
                    new_reac.crossrefs[db] = db_id

            if 'EC-NUMBER' in reac_dic:
                new_reac.ecnumber = reac_dic['EC-NUMBER'][0]

            new_reac.upper_bound = 100000

            if 'REACTION-DIRECTION' in reac_dic:
                dire = reac_dic['REACTION-DIRECTION'][0]

                if dire == 'REVERSIBLE':
                    new_reac.direction = dire
                    new_reac.lower_bound = -100000

                else:
                    new_reac.direction = 'IRREVERSIBLE'
                    new_reac.lower_bound = 0

            else:
                new_reac.direction = 'REVERSIBLE'

            if 'LEFT' in reac_dic:
                mets_left = {m: coeffs[reac_id]['LEFT'][m] for m in reac_dic['LEFT']}
            else:
                mets_left = None

            if 'RIGHT' in reac_dic:
                mets_right = {m: coeffs[reac_id]['RIGHT'][m] for m in reac_dic['RIGHT']}
            else:
                mets_right = None

            if new_reac.direction == 'REVERSIBLE' or 'LEFT-TO-RIGHT' in reac_dic['REACTION-DIRECTION'][0]:
                new_reac.reactants = mets_left
                new_reac.products = mets_right

            else:
                new_reac.products = mets_left
                new_reac.reactants = mets_right

            if 'IN-PATHWAY' in reac_dic:
                new_reac.in_pathway = {self.db_name: [x for x in reac_dic['IN-PATHWAY'] if 'RXN' not in x]}

            if 'TYPES' in reac_dic:
                if 'Transport-Reactions' in reac_dic['TYPES']:
                    new_reac.reaction_type = 'TRANSPORT'
                else:
                    new_reac.reaction_type = 'ENZYMATIC'

            if 'REACTION-LIST' in reac_dic:
                new_reac.sub_reactions = {self.db_name: reac_dic['REACTION-LIST']}

            if 'RXN-LOCATIONS' in reac_dic:
                new_reac.compartment = {self.db_name: reac_dic['RXN-LOCATIONS']}

            if reac_id in enzs:
                new_reac.enzymes = {self.db_name: enzs[reac_id]}
            else:
                new_reac.enzymes = {self.db_name: []}

            genes = []

            for enz in new_reac.enzymes[self.db_name]:
                if 'GENES' in enz_data[enz]:
                    enz_genes = enz_data[enz]['GENES']
                    genes.extend(enz_genes)

                if 'TYPE' in enz_data[enz]:
                    enz_type = enz_data[enz]['TYPE']

                    if enz_type == 'Protein-Complexes':
                        new_reac.by_complex = True

            new_reac.genes = {self.db_name: list(set(genes))}
            if not new_reac.by_complex:
                new_reac.by_complex = False

            new_reac_json = new_reac.dict()
            new_reac_json = {k: v for k, v in new_reac_json.items() if v is not None}

            all_reactions.append(new_reac_json)

        output_file = os.path.join(self.output_folder, 'reaction.json')
        write_json(all_reactions, output_file)

        logging.info('reaction data was transformed and ' + output_file + ' was written')

        return all_reactions


class TransformerEnzyme(Transformer):

    def __init__(self, data_path, db_version):
        """
        Transforms the enzyme data of the cyc database. It reads the proteins.dat file and saves the information
        of each enzyme in a structured Enzyme object.
        Parameters
        ----------
        data_path: Union[str, Parameter]
            the folder of the proteins.dat file of the cyc database
        db_version: Union[str, Parameter]
            version of the database
        """

        super().__init__(data_path, db_version)

    def transform(self):
        """
        Reads the proteins.dat file to extract the following info and
        writes a json file with enzymes instances:
        - entry_id
        - common_name
        - synonyms
        - crossrefs
        - protein_type
        - genes
        - reactions
        - components
        - component_of
        - organisms
        - database version

        Returns
        -------
        all_enzymes: list
            list of dicts with enzyme information
        """

        filepath = os.path.join(self.datasource, 'proteins.dat')

        data = data_by_record(filepath)

        rxns = get_enzrxn_data(db_path=self.datasource, for_rxn=False)

        all_enzymes = []
        for enz_dic in data:
            enz_id = enz_dic['UNIQUE-ID'][0]
            new_enz = Enzyme(entry_id=enz_id)

            new_enz.database_version = {self.db_name: self.db_version.split('_')[1]}

            if 'COMMON-NAME' in enz_dic:
                new_enz.common_name = re.sub('<[^<]+?>', '', enz_dic['COMMON-NAME'][0])

            if 'SYNONYMS' in enz_dic:
                new_enz.synonyms = [re.sub('<[^<]+?>', '', x) for x in enz_dic['SYNONYMS']]

            if 'TYPES' in enz_dic:
                new_enz.protein_type = enz_dic['TYPES'][0]

            if 'DBLINKS' in enz_dic and new_enz.protein_type != 'Protein-Complexes':
                new_enz.crossrefs = {}
                for dblink in enz_dic['DBLINKS']:
                    ref = dblink.split('NIL ')[0][:-1]
                    db = re.search('\((.*?) ', ref).group()[1:-1].strip()
                    db_id = re.search('"(.*?)"', ref).group()[1:-1].strip()
                    new_enz.crossrefs[db] = db_id

            if 'GENE' in enz_dic:
                new_enz.genes = {self.db_name: enz_dic['GENE']}

            if 'SPECIES' in enz_dic:
                new_enz.organisms = {self.db_name: enz_dic['SPECIES']}

            if 'COMPONENT-OF' in enz_dic:
                new_enz.component_of = {self.db_name: enz_dic['COMPONENT-OF']}

            if 'COMPONENTS' in enz_dic:
                comp_coeffs = get_coeffs_complexes(self.datasource)
                new_enz.components = {self.db_name: comp_coeffs[enz_id]}

            if enz_id in rxns:
                new_enz.reactions = {self.db_name: rxns[enz_id]}
            else:
                new_enz.reactions = {self.db_name: []}

            if new_enz.component_of:
                complex_reacs = []
                for cplx in new_enz.component_of[self.db_name]:
                    if cplx in rxns:
                        complex_reacs.extend(rxns[cplx])

                new_enz.reactions[self.db_name].extend(list(set(complex_reacs)))

            new_enz_json = new_enz.dict()
            new_enz_json = {k: v for k, v in new_enz_json.items() if v is not None}

            all_enzymes.append(new_enz_json)

        output_file = os.path.join(self.output_folder, 'enzyme.json')
        write_json(all_enzymes, output_file)

        logging.info('enzyme data was transformed and ' + output_file + ' was written')

        return all_enzymes


class TransformerGene(Transformer):

    def __init__(self, data_path, db_version):
        """
        Transforms the gene data of the cyc database. It reads the genes.dat file and saves the information
        of each gene in a structured Gene object.
        Parameters
        ----------
        data_path: Union[str, Parameter]
            the folder of the genes.dat file of the cyc database
        db_version: Union[str, Parameter]
            version of the database
        """

        super().__init__(data_path, db_version)

    def transform(self):
        """
        Reads the genes.dat file to extract the following info and
        writes a json file with genes instances:
        - entry_id
        - common_name
        - synonyms
        - crossrefs
        - enzymes
        - reactions
        - database version

        Returns
        -------
        all_genes: list
            list of dicts with gene information
        """

        filepath = os.path.join(self.datasource, 'genes.dat')

        data = data_by_record(filepath)

        enz_rxns = get_enzrxn_data(db_path=self.datasource, for_rxn=False)

        all_genes = []
        for gene_dic in data:
            gene_id = gene_dic['UNIQUE-ID'][0]
            new_gene = Gene(entry_id=gene_id)

            new_gene.database_version = {self.db_name: self.db_version.split('_')[1]}

            if 'COMMON-NAME' in gene_dic:
                new_gene.common_name = re.sub('<[^<]+?>', '', gene_dic['COMMON-NAME'][0])
            if 'SYNONYMS' in gene_dic:
                new_gene.synonyms = [re.sub('<[^<]+?>', '', x) for x in gene_dic['SYNONYMS']]
            if 'DBLINKS' in gene_dic:
                new_gene.crossrefs = {}
                for dblink in gene_dic['DBLINKS']:
                    ref = dblink.split('NIL')[0][:-1]
                    try:
                        db = re.search('\((.*?) ', ref).group()[1:-1]
                        db_id = re.search('"(.*?)"', ref).group()[1:-1]
                        if ',' in db_id:
                            db_id = db_id.split(',')[0]
                    except AttributeError:
                        continue
                    new_gene.crossrefs[db] = db_id

            if 'PRODUCT' in gene_dic:
                new_gene.enzymes = {self.db_name: gene_dic['PRODUCT']}

                reactions = []

                for enz in new_gene.enzymes[self.db_name]:
                    if enz in enz_rxns:
                        reactions.extend(enz_rxns[enz])

                new_gene.reactions = {self.db_name: list(set(reactions))}

            new_gene_json = new_gene.dict()
            new_gene_json = {k: v for k, v in new_gene_json.items() if v is not None}

            all_genes.append(new_gene_json)

        output_file = os.path.join(self.output_folder, 'gene.json')
        write_json(all_genes, output_file)

        logging.info('gene data was transformed and ' + output_file + ' was written')

        return all_genes


class TransformerPathway(Transformer):

    def __init__(self, data_path, db_version):
        """
        Transforms the pathway data of the cyc database. It reads the pathways.dat file and saves the information
        of each pathway in a structured Pathway object.
        Parameters
        ----------
        data_path: Union[str, Parameter]
            the folder of the pathways.dat file of the cyc database
        db_version: Union[str, Parameter]
            version of the database
        """

        super().__init__(data_path, db_version)

    def transform(self):
        """
        Reads the pathways.dat file to extract the following info and
        writes a json file with genes instances:
        - entry_id
        - common_name
        - synonyms
        - crossrefs
        - enzymes
        - reactions
        - database version

        Returns
        -------
        all_paths: list
            list of dicts with pathway information
        """

        filepath = os.path.join(self.datasource, 'pathways.dat')

        data = data_by_record(filepath)

        all_paths = []
        for path_dic in data:
            path_id = path_dic['UNIQUE-ID'][0]
            new_path = Pathway(entry_id=path_id)

            new_path.database_version = {self.db_name: self.db_version.split('_')[1]}

            if 'COMMON-NAME' in path_dic:
                new_path.common_name = re.sub('<[^<]+?>', '', path_dic['COMMON-NAME'][0])
            if 'SYNONYMS' in path_dic:
                new_path.synonyms = [re.sub('<[^<]+?>', '', x) for x in path_dic['SYNONYMS']]

            if 'REACTION-LIST' in path_dic:
                new_path.reactions = {self.db_name: path_dic['REACTION-LIST']}

            if 'SPECIES' in path_dic:
                new_path.organisms = {self.db_name: path_dic['SPECIES']}

            if 'SUPER-PATHWAYS' in path_dic:
                new_path.super_pathways = path_dic['SUPER-PATHWAYS']

            if 'PATHWAY-LINKS' in path_dic:
                path_links = {}
                for link in path_dic['PATHWAY-LINKS']:
                    if '"' in link:
                        match = re.search('"(.*?)"', link).group().replace(' ', '_')[1:-1]
                        link = re.sub('"(.*?)"', match, link)

                    if 'OUTGOING' in link:
                        info = link[1:-1].replace(' . :OUTGOING)', '').replace('(', '').split(" ")
                    elif 'INCOMING' in link:
                        info = link[1:-1].replace(' . :INCOMING)', '').replace('(', '').split(" ")
                    else:
                        info = link[1:-1].split(' ')

                    met = info[0].replace('|', '')
                    paths = info[1:]
                    path_links[met] = [x.replace('|', '') for x in paths]

                new_path.pathway_links = path_links

            new_path_json = new_path.dict()
            new_path_json = {k: v for k, v in new_path_json.items() if v is not None}

            all_paths.append(new_path_json)

        output_file = os.path.join(self.output_folder, 'pathway.json')
        write_json(all_paths, output_file)

        logging.info('pathway data was transformed and ' + output_file + ' was written')

        return all_paths


class TransformerOrganism(Transformer):

    def __init__(self, data_path, db_version):
        """
        Transforms the organism data of the cyc database. It reads the pathways.dat and proteins.dat file and gets
        the organisms in the database. Then, it uses the organism identifiers to get metadata from biocyc API.
        No organism metadata is available on the dat files.
        Parameters
        ----------
        data_path: Union[str, Parameter]
            the folder of the pathways.dat and proteins.dat files of the cyc database
        db_version: Union[str, Parameter]
            version of the database
        """

        super().__init__(data_path, db_version)

    def transform(self):
        """
        Reads the pathways.dat and proteins.dat files to extract organism identifiers. Then, uses the biocyc API to
        get the following info and writes a json file with organism instances:
        - entry_id
        - common_name
        - scientific_name
        - taxid
        - species: str = None
        - genus
        - family
        - order
        - org_class
        - phylum
        - kingdom
        - superkingdom
        - genes
        - enzymes
        - database version

        Returns
        -------
        all_orgs: list
            list of dicts with organism information
        """

        file_path = os.path.join(self.datasource, 'pathways.dat')
        file_enz = os.path.join(self.datasource, 'proteins.dat')

        paths = data_by_record(file_path)
        enzs = data_by_record(file_enz)

        orgs_ids = []
        org_paths = {}
        org_enzs = {}
        org_genes = {}

        for path_dic in paths:
            if 'SPECIES' in path_dic:
                path_id = path_dic['UNIQUE-ID'][0]
                organisms = path_dic['SPECIES']
                for o in organisms:
                    if o not in orgs_ids:
                        orgs_ids.append(o)
                    if o in org_paths:
                        org_paths[o].append(path_id)
                    else:
                        org_paths[o] = [path_id]

        for enz_dic in enzs:
            if 'SPECIES' in enz_dic:
                enz_id = enz_dic['UNIQUE-ID'][0]
                organisms = enz_dic['SPECIES']
                for o in organisms:
                    if o not in orgs_ids:
                        orgs_ids.append(o)
                    if o in org_enzs:
                        org_enzs[o].append(enz_id)
                    else:
                        org_enzs[o] = [enz_id]

                if 'GENE' in enz_dic:
                    genes = enz_dic['GENE']
                    for o in organisms:
                        for gene in genes:
                            if o in org_genes:
                                org_genes[o].append(gene)
                            else:
                                org_genes[o] = [gene]

        all_orgs = []

        for org in orgs_ids:

            new_org = Organism(entry_id=org)
            try:
                new_org.pathways = {self.db_name: org_paths[org]}
            except KeyError:
                new_org.pathways = {self.db_name: []}

            try:
                new_org.enzymes = {self.db_name: org_enzs[org]}
            except KeyError:
                new_org.enzymes = {self.db_name: []}

            try:
                new_org.genes = {self.db_name: org_genes[org]}
            except KeyError:
                new_org.genes = {self.db_name: []}

            new_org.database_version = {self.db_name: self.db_version.split('_')[1]}

            if org.startswith('TAX-'):
                new_org.taxid = org.split('-')[1]
            else:
                new_org.taxid = taxid_biocyc_api(org)

            lineage_data = {}
            if new_org.taxid:
                try:
                    taxon = taxoniq.Taxon(new_org.taxid)
                except KeyError:
                    continue
                try:
                    new_org.common_name = taxon.common_name
                except taxoniq.NoValue:
                    new_org.common_name = ''

                new_org.scientific_name = taxon.scientific_name

                lineage = [(t.rank.name, t.scientific_name) for t in taxon.ranked_lineage]

                for pair in lineage:
                    lineage_data[pair[0]] = pair[1]

            new_org_json = new_org.dict()
            new_org_json = {k: v for k, v in new_org_json.items() if v is not None}

            if new_org.taxid:
                for k in lineage_data:
                    if k == 'class':
                        new_org_json['org_class'] = lineage_data[k]
                    else:
                        new_org_json[k] = lineage_data[k]

            all_orgs.append(new_org_json)

        output_file = os.path.join(self.output_folder, 'organism.json')
        write_json(all_orgs, output_file)

        logging.info('organism data was transformed and ' + output_file + ' was written')

        return all_orgs


# if __name__ == '__main__':
#     db_data = "C:/Users/BiSBII/Documents/Pathway Tools/ptools-local/pgdbs/registry/plantcyc/14.0.1/data/"
    # db_data = 'C:/Users/BiSBII/Documents/Pathway Tools/ptools-local/pgdbs/registry/metacyc/26.0/data/'
    # transf = TransformerReaction(data_path=db_data, db_version='plantcyc_14.0', output_folder='json_files')
    # mets = transf.transform()

    # start = time.time()
    #
    # transf = TransformerGene(data_path=db_data, db_version='metacyc_26.0')
    # transf.transform()
    #
    # end = time.time() - start
    # print(end)
