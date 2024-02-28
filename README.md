# iplantsdb
API to get data from iplants repository.
Searches are performed using biocyc identifiers.
https://iplantsdb.bio.di.uminho.pt/

## API functions

**LIST**

- list of all metabolites in the repository
- list of all reactions in the repository
- list of all enzymes in the repository
- list of all pathways in the repository
- list of all genes in the repository
- list of all organisms in the repository
- list of all components of an enzyme (search for enzyme identifier)
- list of all enzymes catalysing a reaction (search for reaction identifier)
- list of all metabolites participating in a reaction (search for reaction identifier)
- list of all pathways a reaction participates in (search for reaction identifier)
- list of all reactions catalysed by an enzyme (search for enzyme identifier)
- list of all metabolites in a metabolic model (search for model identifier)
- list of all reactions in a metabolic model (search for model identifier)
- list of all enzymes in a metabolic model (search for model identifier)
- list of all protein sequences in the repository

**DETAIL**

- metadata of a metabolite (search for metabolite identifier)
- metadata of a reaction (search for reaction identifier)
- metadata of an enzyme (search for enzyme identifier)
- metadata of a pathway (search for pathway identifier)
- metadata of a gene (search for gene identifier)
- metadata of an organism (search for organism identifier)
- metadata of a metabolic model (search for metabolic model identifier)

**DATABASE UPDATE**