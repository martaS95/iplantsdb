# from django.shortcuts import render

import json

import neomodel
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from neomodel import match
from iplants_neo.models import Metabolite, Reaction, Enzyme, Gene, Pathway, Organism, MetabolicModel
from iplants_neo.serializers import MetabolicModelSerializer


@api_view(['GET'])
def list_all_metabolites_view(request):
    """
    Get all metabolites in the neo4j database
    Parameters
    ----------
    request

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            metabolites = Metabolite.nodes.all()
            response = []
            for met in metabolites:
                obj = {"met_id": met.entry_id}
                if met.name:
                    obj["name"] = met.name
                response.append(obj)

            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=404)


@api_view(['GET'])
def list_all_reactions_view(request):
    """
    Get all reactions in the neo4j database
    Parameters
    ----------
    request

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            reactions = Reaction.nodes.all()
            response = []
            for reac in reactions:
                obj = {"reac_id": reac.entry_id}
                if reac.name:
                    obj["name"] = reac.name
                response.append(obj)

            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=404)


@api_view(['GET'])
def list_all_enzymes_view(request):
    """
    Get all enzymes in the neo4j database
    Parameters
    ----------
    request

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            enzymes = Enzyme.nodes.all()
            response = []
            for enz in enzymes:
                obj = {"enz_id": enz.entry_id}
                if enz.name:
                    obj["name"] = enz.name
                response.append(obj)

            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=404)


@api_view(['GET'])
def list_all_genes_view(request):
    """
    Get all genes in the neo4j database
    Parameters
    ----------
    request

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            genes = Gene.nodes.all()
            response = []
            for gene in genes:
                obj = {"gene_id": gene.entry_id}
                if gene.name:
                    obj["name"] = gene.name

                response.append(obj)

            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=404)


@api_view(['GET'])
def list_all_pathways_view(request):
    """
    Get all pathways in the neo4j database
    Parameters
    ----------
    request

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            paths = Pathway.nodes.all()
            response = []
            for path in paths:
                obj = {"path_id": path.entry_id}
                if path.name:
                    obj["name"] = path.name

                response.append(obj)

            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=404)


@api_view(['GET'])
def list_all_organisms_view(request):
    """
    Get all organisms in the neo4j database
    Parameters
    ----------
    request

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            orgs = Organism.nodes.all()
            response = []
            for org in orgs:
                obj = {"org_id": org.entry_id}

                response.append(obj)

            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=404)


@api_view(['GET'])
def get_reactions_of_enzyme_view(request, enzid):
    """
    Get reactions catalysed by an enzyme
    Parameters
    ----------
    request
    enzid: entry_id of the enzyme

    Returns
    -------
    JsonResponse
    """

    if request.method == 'GET':
        try:
            enz = Enzyme.nodes.get(entry_id=enzid)
            reactions = [reac.entry_id for reac in enz.reactions.all()]

            response = {"reactions": reactions}

            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred. Enzyme not found!"}
            return JsonResponse(response, safe=False, status=404)


@api_view(['GET'])
def get_metabolites_of_reaction_view(request, reacid):
    """
    Get metabolites of a reaction
    Parameters
    ----------
    request
    reacid: entry_id of the reaction

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            reac = Reaction.nodes.get(entry_id=reacid)

            reactants = [met.entry_id for met in reac.reactants.all()]
            products = [met.entry_id for met in reac.products.all()]

            all_mets = set(reactants + products)
            print(all_mets)

            response = {"metabolites": list(all_mets)}
            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred. Reaction not found!"}
            return JsonResponse(response, safe=False, status=404)


@api_view(['GET'])
def get_enzymes_of_reaction_view(request, reacid):
    """
    Get enzymes of a reaction
    Parameters
    ----------
    request
    reacid: entry_id of the reaction

    Returns
    -------
    JsonResponse
    """

    if request.method == 'GET':
        try:
            reac = Reaction.nodes.get(entry_id=reacid)

            definition_enzs = dict(node_class=Enzyme, direction=match.INCOMING, relation_type='ENZ_CATALYSES_REAC')

            enz_rels = match.Traversal(reac, Enzyme.__label__, definition_enzs)
            enzs = enz_rels.all()
            enzs_id = [e.entry_id for e in enzs]

            response = {"enzymes": enzs_id}
            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred. Reaction not found!"}
            return JsonResponse(response, safe=False, status=404)


@api_view(['GET'])
def get_pathways_of_reaction_view(request, reacid):
    """
    Get pathways the reaction is part of
    Parameters
    ----------
    request
    reacid: entry_id of the reaction

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            reac = Reaction.nodes.get(entry_id=reacid)

            definition_paths = dict(node_class=Pathway, direction=match.INCOMING, relation_type='PATH_HAS_REAC')

            path_rels = match.Traversal(reac, Pathway.__label__, definition_paths)
            paths = path_rels.all()
            pathways = [p.entry_id for p in paths]

            response = {"pathways": pathways}
            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred. Reaction not found!"}
            return JsonResponse(response, safe=False, status=404)


@api_view(['GET'])
def get_components_of_enzyme_view(request, enzid):
    """
    Get components of an enzyme
    Parameters
    ----------
    request
    enzid: entry_id of the enzyme

    Returns
    -------
    JsonResponse
    """

    if request.method == 'GET':
        try:
            enz = Enzyme.nodes.get(entry_id=enzid)
            components = [comp.entry_id for comp in enz.components.all()]

            response = {"components": components}

            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred. Enzyme not found!"}
            return JsonResponse(response, safe=False, status=404)


@api_view(['GET'])
def get_metabolites_of_model_view(request, modelid):
    """
    Get the metabolites of a model
    Parameters
    ----------
    request
    modelid: model identifier

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            model = MetabolicModel.nodes.get(model_id=modelid)

            metabolites = [met.entry_id for met in model.metabolites.all()]

            response = {"metabolites": metabolites}
            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred. Model not found"}
            return JsonResponse(response, safe=False, status=404)


@api_view(['GET'])
def get_reactions_of_model_view(request, modelid):
    """
    Get the reactions of a model
    Parameters
    ----------
    request
    modelid: model identifier

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            model = MetabolicModel.nodes.get(model_id=modelid)

            reactions = [reac.entry_id for reac in model.reactions.all()]

            response = {"reactions": reactions}
            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred. Model not found"}
            return JsonResponse(response, safe=False, status=404)


@api_view(['GET'])
def get_enzymes_of_model_view(request, modelid):
    """
    Get the enzymes of a model
    Parameters
    ----------
    request
    modelid: model identifier

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            model = MetabolicModel.nodes.get(model_id=modelid)

            enzymes = [enz.entry_id for enz in model.enzymes.all()]

            response = {"enzymes": enzymes}
            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred. Model not found!"}
            return JsonResponse(response, safe=False, status=404)


# @api_view(['POST'])
def create_metabolicmodelnode_view(request, modelid, organism, taxid, year='', author=''):
    """
    Create the node for a metabolic model
    Parameters
    ----------
    request
    modelid: str
        identifier for the model
    organism: str
        name of the organism
    taxid: int
        taxonomy id of the organism
    year: int
        year of the reconstruction
    author: str
        name of the model author
    Returns
    -------
    JsonResponse
    """
    try:
        data = {"model_id": modelid, "organism": organism, "taxid": taxid, "year": year, "author": author}
        serializer = MetabolicModelSerializer(data=data)
        if serializer.is_valid():
            try:
                MetabolicModel.nodes.get(model_id=modelid)
                response = {modelid: 'already in the database'}
                return JsonResponse(response)

            except MetabolicModel.DoesNotExist:
                metabolic_model = MetabolicModel(model_id=modelid, organism=organism, taxid=taxid, year=year,
                                                 author=author)
                org_node = Organism.nodes.get(taxid=taxid)
                metabolic_model.belongs_to.connect(org_node)
                metabolic_model.save()
                response = {'model_id': metabolic_model.model_id}
                return JsonResponse(response, status=200)

        else:
            return JsonResponse({'serializer': 'data types not valid'}, status=400)

    except:
        response = {"error": "An error has occurred"}
        return JsonResponse(response, safe=False, status=400)


# @api_view(['POST'])
def add_rels_reactions_model_view(request, modelid, reactions):
    """
    Create relationships between the model and the reactions in the model
    Parameters
    ----------
    request
    modelid: str
        model identifier in the database
    reactions: str
        string of reactions to link to the model separated by commas (',')

    Returns
    -------
    JsonResponse
    """
    try:
        mm_node = MetabolicModel.nodes.get(model_id=modelid)

        list_reactions = reactions.split(',')

        for reac in list_reactions:
            try:
                reac_node = Reaction.nodes.get(entry_id=reac)
                mm_node.reactions.connect(reac_node)
            except neomodel.DoesNotExist:
                pass

        return JsonResponse({modelid: [reac.entry_id for reac in mm_node.reactions.all()]}, status=200)

    except (MetabolicModel.DoesNotExist, Reaction.DoesNotExist):
        response = {"error": "An error has occurred. Model or Reaction not found!"}
        return JsonResponse(response, safe=False, status=404)


# @api_view(['POST'])
def add_rels_metabolites_model_view(request, modelid, metabolites):
    """
    Create relationships between the model and the metabolites in the model
    Parameters
    ----------
    request
    modelid: str
        model identifier in the database
    metabolites: str
        string of metabolites to link to the model separated by commas (',')

    Returns
    -------
    JsonResponse
    """
    try:
        mm_node = MetabolicModel.nodes.get(model_id=modelid)

        list_metabolites = metabolites.split(',')

        for met in list_metabolites:
            try:
                met_node = Metabolite.nodes.get(entry_id=met)
                mm_node.metabolites.connect(met_node)
            except neomodel.DoesNotExist:
                pass

        return JsonResponse({modelid: [met.entry_id for met in mm_node.metabolites.all()]}, status=200)

    except (MetabolicModel.DoesNotExist, Metabolite.DoesNotExist):
        response = {"error": "An error has occurred. Model or Metabolite not found!"}
        return JsonResponse(response, safe=False, status=404)


# @api_view(['POST'])
def add_rels_enzymes_model_view(request, modelid, enzymes):
    """
    Create relationships between the model and the enzymes in the model
    Parameters
    ----------
    request
    modelid: str
        model identifier in the database
    enzymes: str
        string of enzymes to link to the model separated by commas (',')

    Returns
    -------
    JsonResponse
    """
    try:
        mm_node = MetabolicModel.nodes.get(model_id=modelid)

        list_enzymes = enzymes.split(',')

        print(list_enzymes, 'LISTAAAAAA')

        for enz in list_enzymes:
            print(enz)
            enz_node = Enzyme.nodes.get(entry_id=enz)
            mm_node.enzymes.connect(enz_node)

        return JsonResponse({modelid: [enz.entry_id for enz in mm_node.enzymes.all()]}, status=200)

    except (MetabolicModel.DoesNotExist, Enzyme.DoesNotExist):
        response = {"error": "An error has occurred. Model or Enzyme not found!"}
        return JsonResponse(response, safe=False, status=404)


@csrf_exempt
def add_update_reaction_node_view(request, modelid):
    """
    Add a new reaction or update existing reaction in the database and add it to the model
    Parameters
    ----------
    request
    modelid: str
        model identifier

    Returns
    -------
    JsonResponse
    """
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        try:
            mm_node = MetabolicModel.nodes.get(model_id=modelid)
            new_reactions = json.load(uploaded_file)
            if 'metabolites' in new_reactions:
                del new_reactions['metabolites']

            for new_reac in new_reactions:
                if '__' in new_reac:
                    new_reac_id = new_reac.split('__')[0]
                else:
                    new_reac_id = new_reac
                try:
                    reac_doc = Reaction.nodes.get(entry_id=new_reac_id)

                    db_reactants = reac_doc.reactants.all()
                    for db_reactant in db_reactants:
                        reac_doc.reactants.disconnect(db_reactant)
                    db_prods = reac_doc.products.all()
                    for db_prod in db_prods:
                        reac_doc.products.disconnect(db_prod)

                except Reaction.DoesNotExist:
                    reac_doc = Reaction(entry_id=new_reac_id)
                    reac_doc.save()

                if 'reactants' in new_reactions[new_reac]:
                    for reactant in new_reactions[new_reac]['reactants']:
                        if '__' in reactant:
                            reactant_id = reactant.split('__')[0]
                        else:
                            reactant_id = reactant
                        try:
                            new_met_node = Metabolite.nodes.get(entry_id=reactant_id)
                        except Metabolite.DoesNotExist:
                            new_met_node = Metabolite(entry_id=reactant_id).save()

                        reac_doc.reactants.connect(new_met_node,
                                                   {'stoichiometry': str(
                                                       new_reactions[new_reac]['reactants'][reactant])})

                        if reactant_id not in [m.id for m in mm_node.metabolites.all()]:
                            mm_node.metabolites.connect(new_met_node)

                if 'products' in new_reactions[new_reac]:
                    for product in new_reactions[new_reac]['products']:
                        if '__' in product:
                            product_id = product.split('__')[0]
                        else:
                            product_id = product
                        try:
                            new_met_node = Metabolite.nodes.get(entry_id=product_id)
                        except Metabolite.DoesNotExist:
                            new_met_node = Metabolite(entry_id=product_id).save()

                        reac_doc.products.connect(new_met_node,
                                                  {'stoichiometry': str(new_reactions[new_reac]['products'][product])})

                        if product_id not in [m.id for m in mm_node.metabolites.all()]:
                            mm_node.metabolites.connect(new_met_node)

                mm_node.reactions.connect(reac_doc)

            return JsonResponse({"success": 'new reactions were added to the database'}, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=400)

