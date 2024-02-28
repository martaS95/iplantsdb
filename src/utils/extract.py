import json
import os
from .protrein import UniProtProtein
from Bio import Entrez, SeqIO, Seq
import urllib
from .config import PROJECT_PATH
import xml.etree.ElementTree as ETe
import requests
from typing import Union
from configparser import RawConfigParser

db_configs = RawConfigParser()
db_configs.read('/conf/iplantdb.conf')


def data_by_record(filename: str) -> list:
    """
    Auxiliar function to read the dat file and divide the info by record
    Parameters
    ----------
    filename: str
        json_path for the dat file

    Returns
    -------
    all_records: list
        dicts where each dict has the info of each record
    """
    all_records = []
    datafile = open(filename, 'r')
    line = datafile.readline().strip()

    while line:
        if line[0] != "#" and "UNIQUE-ID" in line:
            record = []
            while line != '//':
                record.append(line)
                line = datafile.readline().strip()

            record_dic = {}
            for info in record:
                if info.count(' - ') == 1:
                    key, value = info.split(' - ')
                    if key not in record_dic:
                        record_dic[key] = [value]
                    else:
                        record_dic[key].append(value)

            all_records.append(record_dic)
        else:
            line = datafile.readline().strip()

    return all_records


def write_json(dic: list, filename: str):
    """
    Write a list of dicts in a json file
    Parameters
    ----------
    dic: list
       dicts to save in the json file
    filename: str
        name of the json file
    """
    with open(filename, 'w') as json_file:
        json.dump(dic, json_file)


def get_coeffs_reactions(reac_file: str) -> dict:
    """
    Get the coefficients of the reactions
    Parameters
    ----------
    reac_file: str
         the reaction.dat file complete path
    Returns
    -------
    records: dict
        reaction coefficients
    """

    datfile = open(reac_file, 'r')
    records = {}
    line = datfile.readline()
    unique_id = ''

    while line:
        if line[0] != "#" and "UNIQUE-ID" in line:
            unique_id = line.strip().split(" - ")[1]
            records[unique_id] = {}
            line = datfile.readline()
            records[unique_id]['LEFT'] = {}
            records[unique_id]['RIGHT'] = {}

        elif line[:4] == 'LEFT':
            substrate = line.strip().split(" - ")[1]
            line = datfile.readline()
            if line[:12] == "^COEFFICIENT":
                stoic = line.strip().split(" - ")[1]

                records[unique_id]['LEFT'][substrate] = stoic
            else:
                records[unique_id]['LEFT'][substrate] = 1.0

        elif line[:5] == "RIGHT":
            substrate = line.strip().split(" - ")[1]
            line = datfile.readline()
            if line[:12] == "^COEFFICIENT":
                stoic = line.strip().split(" - ")[1]

                records[unique_id]['RIGHT'][substrate] = stoic
            else:
                records[unique_id]['RIGHT'][substrate] = 1.0

        else:
            line = datfile.readline()

    return records


def get_enzrxn_data(db_path: str, for_rxn: bool = True) -> dict:
    """
    Get the associations between reactions and enzymes from the enzrxns.dat file
    Parameters
    ----------
    db_path: str
        json_path for the enzrxns.dat file
    for_rxn: bool
        if true it gives the enzymes for each reaction.
        if false it gives the reactions for each enzyme.
    Returns
    -------
    rxn_enz: dict
        if for_rxn is True, the function returns a dict where the keys are reactions and the values are the list of
        associated enzymes
    or
    enz_rxn: dict
        if for_rxn is False, the function returns a dict where the keys are enzymes and the values are the list of
        assiciated reactions
    """

    filename = os.path.join(db_path, 'enzrxns.dat')
    data = data_by_record(filename=filename)

    enz_rxn = {}
    rxn_enz = {}

    for record in data:
        if 'ENZYME' in record:
            enz = record['ENZYME'][0]
        else:
            continue

        if 'REACTION' in record:
            rxn = record['REACTION'][0]
        else:
            continue

        if rxn not in rxn_enz:
            rxn_enz[rxn] = [enz]
        else:
            rxn_enz[rxn].append(enz)

        if enz not in enz_rxn:
            enz_rxn[enz] = [rxn]
        else:
            enz_rxn[enz].append(rxn)

    if for_rxn:
        return rxn_enz
    else:
        return enz_rxn


def get_enz_type_genes(db_path: str) -> dict:
    """
    Get the type and genes of each enzyme to use in the TransformerReaction
    Parameters
    ----------
    db_path: str
        json_path for the proteins.dat file

    Returns
    -------
    enz_dict: dict
        type and genes of each enzyme
    """

    filename = os.path.join(db_path, 'proteins.dat')
    data = data_by_record(filename=filename)

    enz_dict = {}
    for record in data:
        enz_id = record['UNIQUE-ID'][0]
        enz_dict[enz_id] = {}
        if 'TYPES' in record:
            enz_dict[enz_id]['TYPE'] = record['TYPES'][0]
        if 'GENE' in record:
            enz_dict[enz_id]['GENES'] = record['GENE']

    return enz_dict


def get_coeffs_complexes(db_path: str) -> dict:
    """
    Get the coefficients of the protein complexes
    Parameters
    ----------
    db_path: str
        json_path for the protein.dat file

    Returns
    -------
    records: dict
        complex coefficents
    """
    datfile = open(os.path.join(db_path, 'proteins.dat'), 'r')
    records = {}
    line = datfile.readline()
    unique_id = ''

    while line:
        if line[0] != "#" and "UNIQUE-ID" in line:
            unique_id = line.strip().split(" - ")[1]
            records[unique_id] = {}
            line = datfile.readline()

        elif line[:10] == 'COMPONENTS':
            comp = line.strip().split(" - ")[1]
            line = datfile.readline()
            if line[:12] == "^COEFFICIENT":
                stoic = line.strip().split(" - ")[1]
                records[unique_id][comp] = stoic

            else:
                records[unique_id][comp] = 1.0

        else:
            line = datfile.readline()

    return records


def get_uniprot_data(protein_id: str) -> Union[dict, None]:
    """
    Get uniprot data for an enzyme, including:
    - uniprot status
    - uniprot function
    - uniprot location
    - uniprot product
    - sequence

    Parameters
    ----------
    protein_id: str
        uniprot identifier of the enzyme

    Returns
    -------
    uniport_dic: dict
        uniprot data
    """

    uniprot_dic = {}
    p = UniProtProtein(accession=protein_id)
    try:
        p.fetch()
    except ValueError:
        return
    if p.record:
        if "comment_subcellularlocation_location" in p.record.annotations.keys():
            uniprot_dic["uniprot_location"] = p.record.annotations["comment_subcellularlocation_location"]
        else:
            uniprot_dic["uniprot_location"] = []
        uniprot_dic["uniprot_function"] = p.description
        uniprot_dic["uniprot_product"] = p.function
        uniprot_dic["sequence"] = p.sequence
        if "dataset" in p.record.annotations.keys():
            if p.record.annotations['dataset'] == 'TrEMBL':
                uniprot_dic['uniprot_status'] = "unreviewed"
            elif p.record.annotations['dataset'] == 'Swiss-Prot':
                uniprot_dic['uniprot_status'] = "reviewed"
    return uniprot_dic


def get_sequence_gene(ncbi_id: str) -> Union[str, None]:
    """
    Get the sequence of a gene
    Parameters
    ----------
    ncbi_id: str
        ENTREZ or REFSEQ identifier of the gene

    Returns
    -------
    sequence: str
        gene nucleotide sequence
    """
    Entrez.email = str(db_configs.get('iplants-databases-configurations', 'biocyc_email'))
    try:
        handle = Entrez.efetch(db="nucleotide", id=ncbi_id, rettype="gb", retmode="txt")
    except urllib.error.HTTPError:
        return
    try:
        rec = SeqIO.read(handle, format="gb")
        sequence = str(rec.seq)
    except Seq.UndefinedSequenceError:
        return

    return sequence


def get_tair_protein(tair_id: str) -> Union[str, None]:
    """
    Get protein sequence from TAIR10 protein fasta file
    Parameters
    ----------
    tair_id: str
        TAIR identifier

    Returns
    -------
    sequence_dic[tair_id]: str
        sequence for the tair_id
    None if tair_id not in fasta file
    """

    data = os.path.join(PROJECT_PATH, 'protein_sequences', 'ARAPORT11_protein.fasta')

    sequence_dic = {}
    fasta_records = SeqIO.parse(data, format='fasta')
    for rec in fasta_records:
        sequence_dic[rec.id] = str(rec.seq)

    try:
        if '.' not in tair_id:
            tair_id = tair_id + '.1'
        sequence = sequence_dic[tair_id]
        return sequence
    except KeyError:
        return


def files_exist(list_of_files: list) -> bool:
    """
    Checks if a list of files exist
    Parameters
    ----------
    list_of_files: list
        files to check
    Returns
    -------
    bool:
        True if all files in the list exist
        False if at least one file does not exist
    """

    for f in list_of_files:
        if not os.path.isfile(f):
            return False
    return True


def taxid_biocyc_api(org: str) -> Union[int, None]:
    """
    Function to get the taxonomy id of the organism in the database
    Parameters
    ----------
    org: str
        organism identifier in metacyc
    Returns
    -------
    taxid: int, Optional
        taxonomy identifier for the organism

    """
    api = 'https://websvc.biocyc.org/getxml?id=META:' + org

    taxid = ''

    try:
        s = requests.Session()
        s.post('https://websvc.biocyc.org/credentials/login/',
               data={'email': str(db_configs.get('iplants-databases-configurations', 'biocyc_email')),
                     'password': str(db_configs.get('iplants-databases-configurations',
                                                    'biocyc_password'))})
        res = s.get(api)
        tree = ETe.fromstring(res.content)
        for child in tree.iter():
            if child.tag == 'Organism' and 'resource' in child.attrib:
                taxid_complete = child.attrib['frameid']
                taxid = int(taxid_complete.split('-')[1])
    except:
        taxid = None

    return taxid


def get_reac_rev_xml(filename: str) -> Union[dict, None]:
    """
    Get the reaction reversibility from the plant models to integrate in the database
    Parameters
    ----------
    filename: str
        complete path of the plant metabolic model file
    Returns
    -------
    rev_dic: dict, Optional
        returns the reversibility of each reaction in a dict
    """
    rev_dic = {}

    try:
        tree = ETe.parse(filename)
        root = tree.getroot()
        for child in root:
            for other in child:
                if other.tag.endswith('listOfReactions'):
                    for reac in other:
                        reac_id = reac.attrib['id'].replace('__45__', '-').replace('R_', '')
                        try:
                            rev = reac.attrib['reversible']
                        except KeyError:
                            rev = 'true'
                        rev_dic[reac_id] = rev

        return rev_dic

    except ETe.ParseError as e:
        print(f"Error parsing XML file: {e}")
        return None

    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
