"""iplants_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]

"""plantdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from iplants_mongo.views import *
from iplants_neo.views import *
from .views import *
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("schema", SpectacularAPIView.as_view(), name='schema'),
    path("", SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path("list/metabolites", list_all_metabolites_view),
    path("list/reactions", list_all_reactions_view),
    path("list/enzymes", list_all_enzymes_view),
    path("list/pathways", list_all_pathways_view),
    path("list/genes", list_all_genes_view),
    path("list/organisms", list_all_organisms_view),

    path("detail/metabolite/<metid>", get_metabolite_detail_view),
    path("detail/reaction/<reacid>", get_reaction_detail_view),
    path("detail/enzyme/<enzid>", get_enzyme_detail_view),
    path("detail/gene/<geneid>", get_gene_detail_view),
    path("detail/pathway/<pathid>", get_pathway_detail_view),
    path("detail/organism/<orgid>", get_organism_detail_view),
    path("detail/metabolicmodel/<modelid>", get_metabolicmodel_detail_view),

    path("list/reactions/enzyme/<str:enzid>", get_reactions_of_enzyme_view),
    path("list/components/enzyme/<str:enzid>", get_components_of_enzyme_view),
    path("list/metabolites/reaction/<str:reacid>", get_metabolites_of_reaction_view),
    path("list/enzymes/reaction/<str:reacid>", get_enzymes_of_reaction_view),
    path("list/enzymes/reaction/doc/<str:reacid>", get_enzymes_of_reaction_doc_view),
    path("list/pathways/reaction/<str:reacid>", get_pathways_of_reaction_view),
    path("list/metabolites/model/<str:modelid>", get_metabolites_of_model_view),
    path("list/reactions/model/<str:modelid>", get_reactions_of_model_view),
    path("list/enzymes/model/<str:modelid>", get_enzymes_of_model_view),

    path("create_model/model_node/<modelid>/<organism>/<taxid>/<year>/<author>", create_metabolicmodelnode_view),
    path("create_model/model_doc/<modelid>/<organism>/<taxid>/<year>/<author>", create_metabolicmodeldoc_view),

    path("create_model/add_reactions/<modelid>/<reactions>", add_reacs_model_view),
    path("create_model/add_enzymes/<modelid>/<enzymes>", add_enzymes_model_view),
    path("create_model/add_metabolites/<modelid>/<metabolites>", add_metabolites_model_view),
    path("create_model/add_pathways/<modelid>/<pathways>", add_pathways_model_view),
    path("create_model/add_genes/<modelid>/<genes>", add_genes_model_view),

    path("create_model/add_rels_reactions/<str:modelid>/<str:reactions>", add_rels_reactions_model_view),
    path("create_model/add_rels_enzymes/<str:modelid>/<str:enzymes>", add_rels_enzymes_model_view),
    path("create_model/add_rels_metabolites/<str:modelid>/<str:metabolites>", add_rels_metabolites_model_view),

    path("create_model/add_annotation/<modelid>", add_annotation_model_view),
    path("create_model/add_gprs/<modelid>", add_gprs_model_view),
    path("create_model/add_compartments/<modelid>", add_comparts_model_view),
    path("create_model/newreactions_neo/<modelid>", add_update_reaction_node_view),
    path("create_model/newreactions/<modelid>", add_update_reaction_doc_view),
    path("list/get_protein_sequences/", download_aa_sequences),

    path("integratemodel/<modelid>/<organism>/<taxid>/<year>/<author>", integrate_plant_model),

    #path("integratemodelmongo/<modelid>/<organism>/<taxid>/<year>/<author>", integrate_metabolic_model_mongo),
    #path("integratemodelneo/<modelid>/<organism>/<taxid>/<year>/<author>", integrate_metabolic_model_neo),
    path("updatedatabase/<str:version>/<str:dbname>", UpdatedbView),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
