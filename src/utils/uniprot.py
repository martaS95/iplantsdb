import io
from typing import Dict, Tuple, Union
from xml.etree import ElementTree
import pandas as pd
from Bio import SeqIO

from .api_requests import request, read_response

import os


def write_file(string, file_path):
    """
    Grava a string em file_path
    """
    fd = open(file_path, "w")
    fd.write(string)
    os.fsync(fd)
    fd.close()


def extract_uniprot_info(entry):
    """
    Extrai a informação que necessitamos da uniprot.
    """
    # dataset
    ds = entry.get("dataset")

    if ds == "Swiss-Prot":
        status = "reviewed"
    elif ds == "TrEMBL":
        status = "unreviewed"
    else:
        print("Não conheço a db " + ds)
        status = "unknown"

    # accessions
    accessions = [a.text for a in entry.findall(".//accession")]
    accession = accessions[0]

    # short name
    short_name = entry.find("name").text

    # full name
    full_name = entry.find(".//fullName").text

    # encontrar o texto função que costuma estar no início da
    # página da uniprot
    comment_functions = [c.find("text").text for c in entry.findall(".//comment[@type='function']")]

    # encontrar GO - Molecular Function
    # e GO - Biological process
    locations = []
    GO = entry.findall(".//dbReference[@type='GO']")
    for go in GO:
        value = go.find("property[@type='term']").get("value")
        is_location = value.startswith("C:")

        value = value[2:]

        if is_location:
            locations.append(value)

    dictionary = {"status": status, "accessions": accessions, "short_name": short_name, "product": full_name,
                  "comment_functions": comment_functions, "locations": locations}

    return accession, dictionary


def wrap_file(start_line, end_line, file_path):
    """
    Adiciona uma linha no início do ficheiro e outra no fim.
    """
    fd = open(file_path, "r")
    lines = [start_line] + fd.readlines() + [end_line]
    fd.close()
    fd = open(file_path, "w")
    fd.writelines(lines)
    os.fsync(fd)
    fd.close()


def truncate_file(start, end, file_path):
    """
    Remove as 'start' primeiras linhas
    e as 'end' últimas linahs de um ficheiro.
    """
    fd = open(file_path, "r")
    lines = fd.readlines()
    fd.close()
    fd = open(file_path, "w")
    fd.writelines(lines[start:-end])
    os.fsync(fd)
    fd.close()


def parse_xml(file_path, add_root=False, start=0, end=0):
    """
    Faz parsing de um ficheiro xml e retorna um 'ElementTree'.
    """
    if start > 0 or end > 0:
        truncate_file(start, end, file_path)

    if add_root:
        wrap_file("<root>", "</root>", file_path)

    fd = open(file_path, "r")
    tree = ElementTree.parse(fd)
    fd.close()

    return tree


class UniProtAPI:
    api = "https://www.uniprot.org/uniprot"
    mapping = "https://www.uniprot.org/uploadlists"
    query_fields = ('accession', 'ec', 'gene', 'gene_exact', 'id', 'organism', 'taxonomy')
    formats = ('html', 'tab', 'xls', 'fasta', 'gff', 'txt', 'xml', 'rdf', 'list', 'rss')
    column_names = ('id', 'entry name', 'comment(SUBCELLULAR LOCATION)', 'genes', 'genes(PREFERRED)', 'genes(ALTERNATIVE)', 'genes(OLN)', 'organism',
                    'organism-id', 'protein names')
    custom_columns = ('id', 'entry name', 'comment(SUBCELLULAR LOCATION)', 'genes', 'genes(PREFERRED)', 'organism', 'organism-id')
    custom_df_columns = ('Entry', 'Entry name', 'location', 'Gene names', 'Gene names  (primary )', 'Organism', 'Organism ID')
    mapping_terms = ('P_GI', 'P_ENTREZGENEID', 'REFSEQ_NT_ID', 'P_REFSEQ_AC', 'EMBL', 'EMBL_ID',
                     'ACC', 'ACC+ID', 'SWISSPROT', 'ID')


def fetch_uniprot_record(uniprot_accession: str, format_: str = 'xml'):
    if format_ not in UniProtAPI.formats:
        format_ = 'xml'

    url = f'{UniProtAPI.api}/{uniprot_accession}.{format_}'

    response = request(url)

    if not response.text:
        return

    if format_ == 'xml':
        handle = io.StringIO(response.text)
        return SeqIO.read(handle, 'uniprot-xml')
        # file_path = 'unicenas/' + uniprot_accession + ".xml"
        # write_file(response.text, file_path)
        # uniprots = {}
        # tree = parse_xml(file_path, add_root=True, start=2, end=1)
        # entries = tree.findall(".//entry")
        # for entry in entries:
        #     (uniprot_id, info) = extract_uniprot_info(entry)
        #     uniprots[uniprot_id] = info
        # return uniprots

    return response.text


def query_uniprot(query: Dict[str, str],
                  format_: str = 'tab',
                  columns: Tuple[str] = None,
                  limit: str = 5,
                  sort: bool = True,
                  output: str = 'dataframe') -> Union[None, Dict, pd.DataFrame]:
    query_str = ''

    for key, val in query.items():

        if key in UniProtAPI.query_fields:
            query_str += f'{key}:{val}+AND+'

        else:
            query_str += f'{val}+AND+'

    if not query_str:
        return

    # remove +AND+
    query_str = query_str[:-5]

    if format_ not in UniProtAPI.formats:
        format_ = 'tab'

    if not columns:
        columns = UniProtAPI.custom_columns

    else:
        columns = [col for col in columns if col in UniProtAPI.column_names]

        if not columns:
            columns = UniProtAPI.custom_columns

    columns_str = ','.join(columns)

    if sort:
        url = f'{UniProtAPI.api}/?query={query_str}&format={format_}&columns={columns_str}&limit={limit}&sort=score'

    else:
        url = f'{UniProtAPI.api}/?query={query_str}&format={format_}&columns={columns_str}&limit={limit}'

    response = request(url)

    if format_ == 'tab':
        sep = '\t'

        if output == 'dataframe':
            return read_response(response, sep=sep)

        elif output == 'dict':
            return read_response(response, sep=sep).to_dict()

    return response


def map_uniprot_identifiers(identifiers: Tuple[str],
                            from_: str,
                            to: str,
                            format_: str = 'tab',
                            output: str = 'dataframe') -> Union[None, Dict, pd.DataFrame]:

    if from_ not in UniProtAPI.mapping_terms:
        return

    if to not in UniProtAPI.mapping_terms:
        return

    query = ' '.join(identifiers)

    params = {'from': from_,
              'to': to,
              'format': format_,
              'query': query}

    url = f'{UniProtAPI.mapping}/'

    response = request(url, params=params)

    if format_ == 'tab':
        sep = '\t'

        if output == 'dataframe':
            return read_response(response, sep=sep)

        elif output == 'dict':
            return read_response(response, sep=sep).to_dict()

    return response
