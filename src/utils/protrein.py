import pandas as pd

from .bioapi import BioAPI
from .uniprot import fetch_uniprot_record, query_uniprot


class UniProtProtein(BioAPI):

    def __init__(self,
                 accession: str = None,
                 taxonomy: str = None,
                 locus_tag: str = None,
                 name: str = None):

        super().__init__()

        self._accession = accession
        self._taxonomy = taxonomy
        self._locus_tag = locus_tag
        self._name = name

    @property
    def accession(self):
        return getattr(self.record, 'id', self._accession)

    @property
    def taxonomy(self):
        dbxrefs = getattr(self.record, 'dbxrefs')

        if dbxrefs:
            for ref in dbxrefs:
                if 'NCBI Taxonomy:' in ref:
                    return ref.split(':')[1]

        return self._taxonomy

    @property
    def locus_tag(self):

        annotations = getattr(self.record, 'annotations', {})

        if annotations:
            loci = annotations.get('gene_name_ordered locus', [])

            for locus in loci:
                return locus

        return self._locus_tag

    @property
    def name(self):
        annotations = getattr(self.record, 'annotations', {})

        if annotations:
            return annotations.get('gene_name_primary', self._name)

        if self.locus_tag:
            return self.locus_tag

        return self._name

    @property
    def function(self):
        annotations = getattr(self.record, 'annotations', {})

        if annotations:
            funcs = annotations.get('recommendedName_fullName', [])

            for func in funcs:
                return func

        return

    @property
    def description(self):
        annotations = getattr(self.record, 'annotations', {})

        if annotations:
            funcs = annotations.get('comment_function', [])

            for func in funcs:
                return func

        return

    @property
    def synonyms(self):

        synonyms = []

        if self.locus_tag:
            synonyms.append(self.locus_tag)

        if self.name:
            synonyms.append(self.name)

        annotations = getattr(self.record, 'annotations', {})

        if annotations:
            loci = annotations.get('gene_name_ordered locus', [])
            synonyms.extend(loci)

        return synonyms

    @property
    def sequence(self):
        return str(getattr(self.record, 'seq', ''))

    @property
    def location(self):
        GO = self.record.findall(".//dbReference[@type='GO']")
        locs = []
        for go in GO:
            value = go.find("property[@type='term']").get("value")
            is_location = value.startswith("C:")
            locs.append(is_location)
        return locs

    def parse_uniprot_query(self, query: pd.DataFrame):

        if self._taxonomy:
            tax_mask = query.loc[:, 'Organism ID'] == self._taxonomy

            query = query[tax_mask]

        if self._locus_tag:

            loci = query.loc[:, 'Gene names']
            loci_mask = []

            for value in loci:

                mask_value = False

                values = value.split()

                for text in values:
                    text = ''.join(letter for letter in text if letter.isalnum())

                    if self._locus_tag.lower() in text.lower() or text.lower() in self._locus_tag.lower():
                        mask_value = True
                        break

                loci_mask.append(mask_value)

            accessions = query.loc[loci_mask, 'Entry']

            if accessions.size == 1:
                self._accession = accessions[0]

            else:
                self._accession = None

            return

        if self._name:

            loci = query.loc[:, 'Gene names  (primary )']
            loci_mask = []

            for value in loci:

                if self._name.lower() in value.lower() or value.lower() in self._name.lower():
                    loci_mask.append(True)

                else:
                    loci_mask.append(False)

            accessions = query.loc[loci_mask, 'Entry']

            if accessions.size == 1:
                self._accession = accessions[0]

            else:
                self._accession = None

            return

    def fetch(self):

        if not self._accession:

            if self._locus_tag and self._taxonomy:

                query = {'gene': self._locus_tag, 'taxonomy': self._taxonomy}

            elif self._locus_tag and not self._taxonomy:

                query = {'gene': self._locus_tag, 'taxonomy': self._taxonomy}

            elif self._name and self._taxonomy:

                query = {'gene': self._name, 'taxonomy': self._taxonomy}

            else:
                query = {}

            if query:
                uniprot_query = query_uniprot(query=query)

                # it sets up the uniprot accession
                self.parse_uniprot_query(uniprot_query)

        if not self._accession:
            return

        self.record = fetch_uniprot_record(self._accession, 'xml')
