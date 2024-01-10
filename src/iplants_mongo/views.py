# from django.shortcuts import render

# Create your views here.
from iplants_mongo.models import Metabolite, Reaction, Enzyme, Gene, Pathway, MetabolicModel, Organism
from iplants_mongo.serializers import *
from django.http import JsonResponse, FileResponse
from django.core.files.storage import FileSystemStorage
from mongoengine import DoesNotExist
import json
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import os
from utils.config import PROJECT_PATH
from drf_spectacular.utils import extend_schema, inline_serializer


@extend_schema(responses=MetaboliteSerializer)
@api_view(['GET'])
def get_metabolite_detail_view(request, metid):
    """
    Get data of a metabolite
    Parameters
    ----------
    request
    metid: entry_id of the metabolite

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            met = Metabolite.objects.get(entry_id=metid)

            response = {}

            for attr in met:
                value = met[attr]
                if value is not None:
                    response[attr] = value

            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=404)


@extend_schema(responses=ReactionSerializer)
@api_view(['GET'])
def get_reaction_detail_view(request, reacid):
    """
    Get data of a reaction
    Parameters
    ----------
    request
    reacid: entry_id of the metabolite

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            reac = Reaction.objects.get(entry_id=reacid)

            response = {}

            for attr in reac:
                value = reac[attr]
                if value is not None:
                    if isinstance(value, dict) and attr != 'database_version':
                        if 'plantcyc' in value or 'metacyc' in value:
                            res = []
                            for key in value:
                                res.extend(value[key])
                            response[attr] = list(set(res))
                    else:
                        response[attr] = value

            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=404)


@extend_schema(responses=EnzymeSerializer)
@api_view(['GET'])
def get_enzyme_detail_view(request, enzid):
    """
    Get data of an enzyme
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
            enz = Enzyme.objects.get(entry_id=enzid)

            response = {}

            for attr in enz:
                value = enz[attr]
                if value:
                    if isinstance(value, dict) and attr != 'database_version':
                        if 'plantcyc' in value or 'metacyc' in value:
                            res = []
                            for key in value:
                                res.extend(value[key])
                            response[attr] = list(set(res))
                    else:
                        response[attr] = value

            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=404)


@extend_schema(responses=GeneSerializer)
@api_view(['GET'])
def get_gene_detail_view(request, geneid):
    """
    Get data of a gene
    Parameters
    ----------
    request
    geneid: entry_id of the gene

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            gene = Gene.objects.get(entry_id=geneid)

            response = {}

            for attr in gene:
                value = gene[attr]
                if value:
                    if isinstance(value, dict) and attr != 'database_version':
                        if 'plantcyc' in value or 'metacyc' in value:
                            res = []
                            for key in value:
                                res.extend(value[key])
                            response[attr] = list(set(res))
                    else:
                        response[attr] = value

            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=404)


@extend_schema(responses=PathwaySerializer)
@api_view(['GET'])
def get_pathway_detail_view(request, pathid):
    """
    Get data of a pathway
    Parameters
    ----------
    request
    pathid: entry_id of the pathway

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            path = Pathway.objects.get(entry_id=pathid)

            response = {}

            for attr in path:
                value = path[attr]
                if value:
                    if isinstance(value, dict) and attr != 'database_version':
                        if 'plantcyc' in value or 'metacyc' in value:
                            res = []
                            for key in value:
                                res.extend(value[key])
                            response[attr] = list(set(res))
                    else:
                        response[attr] = value

            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=404)


@extend_schema(responses=OrganismSerializer)
@api_view(['GET'])
def get_organism_detail_view(request, orgid):
    """
    Get data of an organism
    Parameters
    ----------
    request
    orgid: entry_id of the organism

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            org = Organism.objects.get(entry_id=orgid)
            response = {}

            for attr in org:
                value = org[attr]
                if value:
                    if isinstance(value, dict) and attr != 'database_version':
                        if 'plantcyc' in value or 'metacyc' in value:
                            res = []
                            for key in value:
                                res.extend(value[key])
                            response[attr] = list(set(res))
                    else:
                        response[attr] = value

            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=404)


@extend_schema(responses=MetabolicModelSerializer)
@api_view(['GET'])
def get_metabolicmodel_detail_view(request, modelid):
    """
    Get data of a metabolic model
    Parameters
    ----------
    request
    modelid: entry_id of the model

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            mmodel = MetabolicModel.objects.get(model_id=modelid)

            response = {}

            for attr in mmodel:
                value = mmodel[attr]
                if value:
                    response[attr] = value

            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=404)


@extend_schema(responses={'200': inline_serializer('ser1', fields={'enzymes': serializers.ListField()})})
@api_view(['GET'])
def get_enzymes_of_reaction_doc_view(request, reacid):
    """
    Get the list of enzymes catalysing a reaction
    Parameters
    ----------
    request
    reacid: str
        identifier for the reaction

    Returns
    -------
    JsonResponse
    """
    if request.method == 'GET':
        try:
            reac = Reaction.objects.get(entry_id=reacid)
            enzymes = []
            for key in reac.enzymes:
                enzymes.extend(reac.enzymes[key])
            response = {'enzymes': list(set(enzymes))}
            return JsonResponse(response, safe=False, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=404)


# @api_view(['POST'])
def create_metabolicmodeldoc_view(request, modelid, organism, taxid, year, author=''):
    """
    Create the doc for a metabolic model
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
                MetabolicModel.objects.get(model_id=modelid)
                response = {modelid: 'already in the database'}
                return JsonResponse(response, status=304)

            except DoesNotExist:
                mm_doc = MetabolicModel(**data)
                mm_doc.save()

            response = {'model_id': mm_doc.model_id}
            return JsonResponse(response, status=200)
        else:
            return JsonResponse({'serializer': 'data types not valid'}, status=400)

    except:
        response = {"error": "An error has occurred"}
        return JsonResponse(response, safe=False, status=400)


# @api_view(['POST'])
def add_reacs_model_view(request, modelid, reactions):
    """
    Add reactions to metabolic model document
    Parameters
    ----------
    request
    modelid: str
        model identifier in the database
    reactions: str
        string of reactions to add to the document separated by commas
    Returns
    -------
    JsonResponse
    """
    try:
        model = MetabolicModel.objects.get(model_id=modelid)
        list_reactions = reactions.split(',')
        for reac in list_reactions:
            model.reactions.append(reac)
        model.save()

        return JsonResponse({model.id: model.reactions}, status=200)

    except:
        response = {"error": "An error has occurred"}
        return JsonResponse(response, safe=False, status=404)


# @api_view(['POST'])
def add_metabolites_model_view(request, modelid, metabolites):
    """
    Add metabolites to metabolic model document
    Parameters
    ----------
    request
    modelid: str
        model identifier in the database
    metabolites: str
        string of metabolites to add to the document separated by commas
    Returns
    -------
    JsonResponse
    """
    try:
        model = MetabolicModel.objects.get(model_id=modelid)
        list_metabolites = metabolites.split(',')
        for met in list_metabolites:
            if met not in model.metabolites:
                model.metabolites.append(met)
        model.save()

        return JsonResponse({model.id: model.metabolites}, status=200)

    except:
        response = {"error": "An error has occurred"}
        return JsonResponse(response, safe=False, status=404)


# @api_view(['POST'])
def add_enzymes_model_view(request, modelid, enzymes):
    """
    Add enzymes to metabolic model document
    Parameters
    ----------
    request
    modelid: str
        model identifier in the database
    enzymes: str
        string of enzymes to add to the document separated by commas
    Returns
    -------
    JsonResponse
    """
    try:
        model = MetabolicModel.objects.get(model_id=modelid)
        list_enzymes = enzymes.split(',')
        for enz in list_enzymes:
            model.enzymes.append(enz)
        model.save()

        return JsonResponse({model.id: model.enzymes}, status=200)

    except:
        response = {"error": "An error has occurred"}
        return JsonResponse(response, safe=False, status=404)


# @api_view(['POST'])
def add_pathways_model_view(request, modelid, pathways):
    """
    Add pathways to metabolic model document
    Parameters
    ----------
    request
    modelid: str
        model identifier in the database
    pathways: str
        string of pathways to add to the document separated by commas
    Returns
    -------
    JsonResponse
    """
    try:
        model = MetabolicModel.objects.get(model_id=modelid)
        list_pathways = pathways.split(',')
        for path in list_pathways:
            model.pathways.append(path)
        model.save()

        return JsonResponse({model.id: model.pathways}, status=200)

    except:
        response = {"error": "An error has occurred"}
        return JsonResponse(response, safe=False, status=404)


# @api_view(['POST'])
def add_genes_model_view(request, modelid, genes):
    """
    Add genes to metabolic model document
    Parameters
    ----------
    request
    modelid: str
        model identifier in the database
    genes: str
        string of genes to add to the document separated by commas
    Returns
    -------
    JsonResponse
    """
    try:
        model = MetabolicModel.objects.get(model_id=modelid)
        list_genes = genes.split(',')
        for gene in list_genes:
            model.genes.append(gene)
        model.save()

        return JsonResponse({model.id: model.genes}, status=200)

    except:
        response = {"error": "An error has occurred"}
        return JsonResponse(response, safe=False, status=404)


@csrf_exempt
def add_annotation_model_view(request, modelid):
    """
    Add the annotation file to the model document
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
            dic = json.load(uploaded_file)
            if dic:
                try:
                    model = MetabolicModel.objects.get(model_id=modelid)
                    model.annotation = dic
                    model.save()

                    return JsonResponse({'annotation added to the model': modelid}, status=200)

                except DoesNotExist:
                    response = {"error": "An error has occurred"}
                    return JsonResponse(response, safe=False, status=404)
        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=400)


@csrf_exempt
def add_gprs_model_view(request, modelid):
    """
    Add the gprs file to the model document
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
            df = pd.read_csv(uploaded_file)
            list_gprs = []
            for ind, row in df.iterrows():
                pair = (row['reaction'], row['rule'])
                list_gprs.append(pair)

            try:
                model = MetabolicModel.objects.get(model_id=modelid)
                if not model.gprs:
                    model.gprs = list_gprs
                else:
                    model.gprs.extend(list_gprs)
                model.save()

                return JsonResponse({'gprs added to the model': modelid}, status=200)

            except DoesNotExist:
                response = {"error": "An error has occurred"}
                return JsonResponse(response, safe=False, status=404)
        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=400)


@csrf_exempt
def add_comparts_model_view(request, modelid):
    """
    Add compartments file to the model document
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
            reac_compartments = json.load(uploaded_file)

            if reac_compartments:

                compart_suffix = {'cytosol': 'cyto', 'pmf': 'pmf', 'chloroplast': 'chlo', 'mitochondrion': 'mito',
                                  'endoplasmatic reticulum': 'er', 'endoplasmic reticulum': 'er', 'peroxisome': 'pero',
                                  'golgi': 'golgi', 'vacuole': 'vacu', 'extracellular': 'extr', 'secreted': 'extr',
                                  'lumen': 'lum'}

                for reac in reac_compartments:
                    try:
                        reac_doc = Reaction.objects.get(entry_id=reac)
                        new_reac_ids = []
                        for compart in reac_compartments[reac]:
                            new_id = reac + '__' + compart_suffix[compart]
                            new_reac_ids.append((new_id, compart))
                        reac_doc.models[modelid] = new_reac_ids
                        reac_doc.save()

                        reac_mets = list(reac_doc.reactants.keys()) + list(reac_doc.products.keys())
                        for met in reac_mets:
                            try:
                                met_doc = Metabolite.objects.get(entry_id=met)
                            except DoesNotExist:
                                met_doc = Metabolite(entry_id=met).save()

                            compart_names = {}
                            for compart in reac_compartments[reac]:
                                new_id = met + '__' + compart_suffix[compart]

                                if new_id not in compart_names:
                                    compart_names[new_id] = compart

                            if modelid not in met_doc.models:
                                met_doc.models[modelid] = compart_names
                            else:
                                met_doc.models[modelid].update(compart_names)
                            met_doc.save()
                    except DoesNotExist:
                        pass

                return JsonResponse({'compartments added to the model': modelid}, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=400)


@csrf_exempt
def add_update_reaction_doc_view(request, modelid):
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
    compart_suffix = {'cytosol': 'cyto', 'pmf': 'pmf', 'chloroplast': 'chlo', 'mitochondrion': 'mito',
                      'endoplasmatic reticulum': 'er', 'endoplasmic reticulum': 'er', 'peroxisome': 'pero',
                      'golgi': 'golgi', 'vacuole': 'vacu', 'extracellular': 'extr', 'secreted': 'extr',
                      'lumen': 'lum'}

    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        try:
            mm_doc = MetabolicModel.objects.get(model_id=modelid)
            new_reactions = json.load(uploaded_file)

            if 'metabolites' in new_reactions:
                comparts_mets = new_reactions['metabolites']
                del new_reactions['metabolites']
                has_mets_comps = True
            else:
                has_mets_comps = False
                comparts_mets = {}

            for new_reac in new_reactions:
                data = new_reactions[new_reac].copy()
                data['entry_id'] = new_reac
                serializer = ReactionSerializer(data=data)

                if serializer.is_valid():
                    try:
                        reac_doc = Reaction.objects.get(entry_id=new_reac)
                        reac_doc.update(**new_reactions[new_reac])
                    except DoesNotExist:

                        reac_doc = Reaction(entry_id=new_reac, **new_reactions[new_reac])
                        reac_doc.save()

                    if new_reac not in mm_doc.reactions:
                        mm_doc.reactions.append(new_reac)

                        reac_mets = set(list(reac_doc.reactants.keys()) + list(reac_doc.products.keys()))

                        if not has_mets_comps:
                            comparts_mets = {}
                            reac_comparts = data['compartment']
                            for met in reac_mets:
                                for comp in reac_comparts:
                                    new_met_id = met + '__' + compart_suffix[comp]
                                    comparts_mets[met] = {new_met_id: comp}

                        for met in reac_mets:
                            try:
                                met_doc = Metabolite.objects.get(entry_id=met.split('__')[0])
                            except DoesNotExist:
                                met_doc = Metabolite(entry_id=met.split('__')[0]).save()

                            if modelid in met_doc.models:
                                met_doc.models[modelid].update(comparts_mets[met.split('__')[0]])
                            else:
                                met_doc.models[modelid] = comparts_mets[met.split('__')[0]]
                            met_doc.save()

                            if met.split('__')[0] not in mm_doc.metabolites:
                                mm_doc.metabolites.append(met.split('__')[0])
                    mm_doc.save()
                else:
                    return JsonResponse({"error": "data types not valid"}, status=400)

            return JsonResponse({"sucess": 'new reactions were added to the database'}, status=200)

        except:
            response = {"error": "An error has occurred"}
            return JsonResponse(response, safe=False, status=400)


@api_view(['GET'])
def download_aa_sequences(request):
    """
    Get the protein sequences in the database
    Parameters
    ----------
    request
    """
    seq_records = []
    enzs = Enzyme.objects.all()
    for enz in enzs:
        if enz.sequence:
            seq = Seq(enz.sequence)
            new_rec = SeqRecord(seq, id=enz.entry_id, description='')
            seq_records.append(new_rec)

    SeqIO.write(seq_records, os.path.join(PROJECT_PATH, 'protein_sequences.fasta'), 'fasta')

    fs = FileSystemStorage(PROJECT_PATH)
    response = FileResponse(fs.open('protein_sequences.fasta', 'rb'),
                            content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="protein_sequences.fasta"'
    return response
