import json
from rest_framework.decorators import api_view
from update_task_manager import execute_update_pipeline
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from iplants_mongo.serializers import MetabolicModelSerializer
from plant_models.model_integration import ModelIntegrationNeo, ModelIntegrationMongo


@api_view(['POST'])
def UpdatedbView(request, dbname, version):
    """
    Parameters
    ----------
    request: request
        API request to perform the update
    dbname: str
        name of the database: 'plantcyc' or 'metacyc'
    version: str
        database version number
    """
    execute_update_pipeline(dbname=dbname, version=version)
    return HttpResponse('database update has started')


@csrf_exempt
def integrate_plant_model(request, modelid, organism, taxid, year, author=''):
    """
    Create the doc and node for a metabolic model
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
            if request.method == 'POST':
                uploaded_files = request.FILES.getlist('file')

                mets = json.load(uploaded_files[0])
                reacs = json.load(uploaded_files[1])

                model_int_neo = ModelIntegrationNeo(modelid=data["model_id"], organism=data["organism"],
                                                    taxid=data['taxid'], year=data["year"], author=data["author"],
                                                    metabolite_json=mets, reaction_json=reacs)
                model_int_neo.integrate_model()

                model_int_mongo = ModelIntegrationMongo(modelid=data["model_id"], organism=data["organism"],
                                                        taxid=data['taxid'], year=data["year"], author=data["author"],
                                                        metabolite_json=mets, reaction_json=reacs)
                model_int_mongo.integrate_model()

                return JsonResponse({"sucess": 'new model was integrated to the database'}, status=200)

        else:
            return JsonResponse({"error": "data types not valid"}, status=400)

    except:
        response = {"error": "An error has occurred"}
        return JsonResponse(response, safe=False, status=400)


