# -*- encoding: utf-8 -*-

# from django.shortcuts import render, render_to_response, redirect, get_object_or_404, get_list_or_404, Http404
from django.shortcuts import *
from django.views.generic import TemplateView, FormView
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.template import RequestContext
from django import template
from models import proyecto
from .forms import *
import funciones
import sys
#~ from administradorConsultas import AdministradorConsultas # Esta la comente JAPeTo
#~ from manejadorArchivos import obtener_autores # Esta la comente JAPeTo
#~ from red import Red # Esta la comente JAPeTo
from Logica import ConsumirServicios, procesamientoScopusXml, procesamientoArxiv
# import igraph
import traceback
import json
import django.utils
from Logica.ConexionBD.adminBD import AdminBD
# sys.setdefaultencoding is cancelled by site.py
reload(sys)  # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')
# Create your views here.
# @login_required

#ruta = "/home/administrador/ManejoVigtech/ArchivosProyectos/"

sesion_proyecto=None
mensajes_pantalla=None
proyectos_list =None
model_proyecto =None


class home(TemplateView):
    template_name = "home.html"
    def get_context_data(self, **kwargs):
        global proyectos_list
        global model_proyecto
        try:
            proyectos_list = get_list_or_404(proyecto,  idUsuario=self.request.user)
        except:
            proyectos_list = None
	return {'proyectos': proyectos_list, 'mproyecto': model_proyecto}
           

class RegistrarUsuario(FormView):
    template_name = "registrarUsuario.html"
    form_class = FormularioRegistrarUsuario
    success_url = reverse_lazy('RegistrarUsuarios')

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, "Se ha creado exitosamente el usuario")
        return redirect('login')

@login_required
def nuevo_proyecto(request):
    if request.method == 'POST':
        form = FormularioCrearProyecto(request.POST)
        fraseB = request.POST.get('fraseB')
        fraseA = request.POST.get('fraseA')
        autor = request.POST.get('autor')
        words = request.POST.get('words')
        before = request.POST.get('before')
        after = request.POST.get('after')
        limArxiv = request.POST.get('limArxiv')
        limSco = request.POST.get('limSco')
        print limArxiv, limSco
        global mensajes_pantalla
        mensajes_pantalla=""
        global proyectos_list
        print "entro a nuevo proyect, by japeto"
        #print fraseB
        #Formato de frase de busqueda
        #FraseBásica,Words,FraseA,autor,before,after
        busqueda = fraseB + "," + words + "," + fraseA + "," + autor + "," + before + "," + after
        print "busca "+busqueda+", by japeto"
        if form.is_valid():
            nombreDirectorio = form.cleaned_data['nombre']
            articulos = {}
            modelo_proyecto = form.save(commit=False)
            modelo_proyecto.idUsuario = request.user
            print "formulario valido, by japeto"
            # print "2"
            # proyectos_list = get_list_or_404(proyecto,  idUsuario=request.user)
            # proyectos_list = get_list_or_404(proyecto, idUsuario=request.user)
            #modelo_proyecto.calificacion=5
            modelo_proyecto.fraseBusqueda = busqueda
            modelo_proyecto.save()

            #Creacion del directorio donde se guardaran los documentos respectivos del proyecto creado.
            mensajes_pantalla="<p class='text-primary'><span class='fa  fa-send fa-fw'></span>Se ha creado el Directorio para el proyecto</p>"
            funciones.CrearDirectorioProyecto(modelo_proyecto.id_proyecto, request.user)
            print "se crea directorio, by japeto"
            
            if fraseB != "":
                try:
                    """
                        Descarga de documentos de Google Scholar y Scopus
                    """
                    print "descarga de documentos, by japeto"
                    mensajes_pantalla+="<p class='text-primary'><span class='fa  fa-send fa-fw'></span>Descarga de documentos de Arxiv</p>"
                    articulos_arxiv= ConsumirServicios.consumir_arxiv(fraseB, request.user.username, str(modelo_proyecto.id_proyecto), limArxiv)
                    # mensajes_pantalla+="<p class='text-primary'><span class='fa  fa-send fa-fw'></span>Descarga de documentos de Google Scholar</p>"
                    # articulos = ConsumirServicios.consumir_scholar(fraseB, request.user.username, str(modelo_proyecto.id_proyecto) )
                    mensajes_pantalla+="<p class='text-primary'><span class='fa  fa-send fa-fw'></span>Descarga de documentos de Scopus</p>"
                    articulos_scopus = ConsumirServicios.consumir_scopus(fraseB, request.user.username, str(modelo_proyecto.id_proyecto), limSco)
                    mensajes_pantalla+="<p class='text-success'><span class='fa  fa-check fa-fw'></span>Descarga de documentos terminada</p>"
                except:
                    mensajes_pantalla+="<p class='text-danger'><span class='fa  fa-times fa-fw'></span><b>PROBLEMA: </b>Descarga de documentos</p>"
                    mensajes_pantalla+="STOP";
                    print traceback.format_exc()
                    

                try:
                    """
                        indexación
                    """
                    mensajes_pantalla+="<p class='text-primary'><span class='fa  fa-send fa-fw'></span>Inicia la indexación</label></p>"
                    print mensajes_pantalla
                    ir = ConsumirServicios.IR()
                    ir.indexar(str(request.user.username),str(modelo_proyecto.id_proyecto))
                    mensajes_pantalla+="<p class='text-success'><span class='fa  fa-check fa-fw'></span>Indexacion terminada</p>"
                except:
                    mensajes_pantalla+="<p class='text-danger'><span class='fa  fa-times fa-fw'></span><b>PROBLEMA:</b>La indexación no se puede completar</p>"
                    print traceback.format_exc()

                try:
                    """"
                        Analisis
                    """
                    mensajes_pantalla+="<p class='text-primary'><span class='fa  fa-send fa-fw'></span>Inicia el Analisis</p>"
                    # print mensajes_pantalla
                    data = ConsumirServicios.consumir_analisis(str(request.user.username),str(modelo_proyecto.id_proyecto))
                    mensajes_pantalla+="<p class='text-success'><span class='fa  fa-check fa-fw'></span>Analisis terminado</p>"
                except:
                    mensajes_pantalla+="<p class='text-danger'><span class='fa  fa-times fa-fw'></span><b>PROBLEMA:</b> El Analisis no se puede completar</p>"
                    print traceback.format_exc()


                
                try:
                    """
                    Analisis de Redes Sociales
                    """
                    mensajes_pantalla+="<p class='text-primary'><span class='fa  fa-send fa-fw'></span>Inicia el Analisis de Redes Sociales</p>"
                    # print mensajes_pantalla
                    network = ConsumirServicios.consumir_red(str(request.user.username),str(modelo_proyecto.id_proyecto))
                    mensajes_pantalla+="<p class='text-success'><span class='fa  fa-check fa-fw'></span>Analisis de Redes Sociales terminado</p>"
                except:
                    mensajes_pantalla+="<p class='text-danger'><span class='fa  fa-times fa-fw'></span><b>PROBLEMA:</b>El Analisis de Redes Sociales no se puede completar</p>"
                    print traceback.format_exc()

                try:
                    """
                        Inserción de metadatos Arxiv
                    """
                    mensajes_pantalla+="<p class='text-primary'><span class='fa  fa-send fa-fw'></span>Inica la inserción de metadatos Arxiv</p>"
                    # print mensajes_pantalla
                    xml = open("/home/vigtech/shared/repository/"+ str(request.user.username)
                                    + "." + str(modelo_proyecto.id_proyecto) + "/salida.xml")
                    procesamientoArxiv.insertar_metadatos_bd(str(modelo_proyecto.id_proyecto),xml)
                    mensajes_pantalla+="<p class='text-success'><span class='fa  fa-check fa-fw'></span>La inserción de metadatos Arxiv ha terminado</p>"
                except:
                    mensajes_pantalla+="<p class='text-danger'><span class='fa  fa-times fa-fw'></span><b>PROBLEMA:</b>La inserción de metadatos Arxiv no se puede completar</p>"
                    print traceback.format_exc()
                
                try:
                    """
                       Conexión con base datos para insertar metadatos de paper de Scopus
                    """
                    mensajes_pantalla+="<p class='text-primary'><span class='fa  fa-send fa-fw'></span>Inica la inserción de metadatos Scopus</p>"
                    # print mensajes_pantalla
                    busqueda = open("/home/vigtech/shared/repository/"+ str(request.user.username)
                                    + "." + str(modelo_proyecto.id_proyecto) + "/busqueda0.xml")
                    mensajes_pantalla+="<p class='text-success'><span class='fa  fa-check fa-fw'></span>La inserción de metadatos Scopus ha terminado</p>"                    
                except:
                    mensajes_pantalla+="<p class='text-danger'><span class='fa  fa-times fa-fw'></span><b>PROBLEMA:</b>La inserción de metadatos Scopus no se puede completar</p>"
                    print traceback.format_exc()

                
                try:
                    """
                        NAIVE BAYES
                    """
                    ConsumirServicios.consumir_recuperacion_unidades_academicas(str(request.user.username),str(modelo_proyecto.id_proyecto))
                    mensajes_pantalla += "<p class='text-primary'><span class='fa  fa-send fa-fw'></span>Inicia el procesando Scopus XML</ṕ>"
                    # print mensajes_pantalla
                    procesamientoScopusXml.xml_to_bd(busqueda, modelo_proyecto.id_proyecto, articulos_scopus['titulos'])
                    mensajes_pantalla+="<p class='text-success'><span class='fa  fa-check fa-fw'></span>Inicia el procesando Scopus XML ha terminado</p>"
                except:
                    mensajes_pantalla+="<p class='text-danger'><span class='fa  fa-times fa-fw'></span><b>PROBLEMA:</b> El procesando Scopus XML no se puede completar</p>"
                    print traceback.format_exc()                        
                
                try:
                    mensajes_pantalla+="<p class='text-primary'><span class='fa  fa-send fa-fw'></span>Inicia la recuperacion de unidades academicas</p>"
                    # print mensajes_pantalla
                    ConsumirServicios.consumir_recuperacion_unidades_academicas(str(request.user.username),str(modelo_proyecto.id_proyecto))
                    mensajes_pantalla+="<p class='text-success'><span class='fa  fa-check fa-fw'></span>Finaliza la recuperacion de unidades academicas</p>"
                    mensajes_pantalla+="<p class='text-success'><span class='fa  fa-check fa-fw'></span>Se ha creado exitosamente el proyecto</p>"
                    mensajes_pantalla+="EOF"
                except:
                    mensajes_pantalla+="<p class='text-danger'><span class='fa  fa-times fa-fw'></span><b>PROBLEMA:</b> la recuperacion de unidades academicas no se puede completar</p>"
                    mensajes_pantalla+="EOF"
                    print traceback.format_exc() 
                # messages.success(request, "Se ha creado exitosamente el proyecto")
                #articulos = funciones.buscadorSimple(fraseB)
                #ac = AdministradorConsultas()
                #ac.descargar_papers(fraseB)
                #lista_scopus = ac.titulos_descargas
            #if fraseA != "" or autor != "" or words != "":
            #    articulos = funciones.buscadorAvanzado(fraseA, words, autor, after, before)
            #print articulos
            #~ print str(modelo_proyecto.id_proyecto)
            #~ print str(modelo_proyecto.resumen)
            #funciones.moveFiles(modelo_proyecto.id_proyecto, request.user, articulos, lista_scopus)
            #funciones.escribir_archivo_documentos(modelo_proyecto.id_proyecto, request.user, articulos, lista_scopus)
            # messages.success(request, "Se ha creado exitosamente el proyecto")
            #~ return redirect('crear_proyecto')
            global proyectos_list
            global model_proyecto
            try:
                proyectos_list = get_list_or_404(proyecto,  idUsuario=self.request.user)
            except:
                print traceback.format_exc()
                proyectos_list = None
        else:
            messages.error(request, "Imposible crear el proyecto")
    else:
        form = FormularioCrearProyecto()
    return render(request, 'GestionProyecto/NuevoProyecto.html', {'form': form,
                'proyectos': proyectos_list, 'mproyecto': model_proyecto}, context_instance=RequestContext(request))


#Visualización de proyectos propios de un usuario.
@login_required
def ver_mis_proyectos(request):
    global model_proyecto
    global proyectos_list
    try:
        proyectos_list = get_list_or_404(proyecto, idUsuario=request.user)
    except: 
        proyectos_list =None
        messages.success(request, "Usted no tiene proyectos")

    return render(request, 'GestionProyecto/verMisProyectos.html', {'proyectos': proyectos_list, 'mproyecto': model_proyecto}, context_instance=RequestContext(request))


#Visualización de proyectos con disponibilidad pública que no pertenecen al usuario actual.
@login_required
def ver_otros_proyectos(request):
    try:
        proyectos_list = get_list_or_404(proyecto)
        idUser = request.user
        otros_proyectos = []
        for project in proyectos_list:
            if project.idUsuario != idUser:
                otros_proyectos.append(project)
    except:
        proyectos_list =None

    return render(request, 'GestionProyecto/OtrosProyectos.html', {
        'proyectos': otros_proyectos, 'proyectos':proyectos_list, 'mproyecto': model_proyecto}, context_instance=RequestContext(request))


@login_required
def busqueda_navegacion(request):
    global proyectos_list
    global model_proyecto
    return render(request, 'GestionBusqueda/Busqueda_Navegacion.html', {'proyectos': proyectos_list, 'mproyecto': model_proyecto})


@login_required
def editar_proyecto(request, id_proyecto):
    global proyectos_list
    global model_proyecto
    model_proyecto = get_object_or_404(proyecto, id_proyecto=id_proyecto)
    request.session['proyecto']= str(model_proyecto.id_proyecto)
    request.proyecto = model_proyecto
    print  "This is my project:",request.session['proyecto']
    lista = funciones.crearListaDocumentos(id_proyecto, request.user)
    if request.method == 'POST':
        proyecto_form = FormularioCrearProyecto(request.POST, instance=model_proyecto)
        #proyecto_form.fields['disponibilidad'].widget.attrs['disabled']=True
        if proyecto_form.is_valid:
            #print "Hola mundo"
            #print proyecto_form.cleaned_data
            #nuevoNombre=proyecto_form.cleaned_data['nombre']
            model_project = proyecto_form.save()
            #    funciones.cambiarNombreDirectorio(nombreDirectorioAnterior,nuevoNombre,request.user)
            messages.success(request, "Se ha modificado exitosamente el proyecto")
        else:
            messages.error(request, "Imposible editar el proyecto")
    else:
        proyecto_form = FormularioCrearProyecto(instance=model_proyecto)
    return render(request, 'GestionProyecto/editar_proyecto.html',
                  {'form': proyecto_form, 'lista': lista, 'user': request.user, 'mproyecto':model_proyecto, 'proyectos': proyectos_list, 'proyecto': id_proyecto},
                  context_instance=RequestContext(request))




@login_required
def ver_proyecto(request, id_proyecto):
    global model_proyecto
    global proyectos_list
    model_proyecto = get_object_or_404(proyecto, id_proyecto=id_proyecto)
    proyecto_form = FormularioCrearProyecto(instance=model_proyecto)
    #proyecto_form.fields['disponibilidad'].widget.attrs['disabled']=True
    #proyecto_form.fields['nombre'].label="Titulo del proyecto"
    proyecto_form.fields['nombre'].widget.attrs['disabled'] = True
    proyecto_form.fields['resumen'].widget.attrs['disabled'] = True

    return render(request, 'GestionProyecto/ver_proyecto.html', {'form': proyecto_form, 'mproyecto':model_proyecto, 'proyectos':proyectos_list},
                  context_instance=RequestContext(request))


@login_required
def buscador(request):
    global proyectos_list
    global model_proyecto
    if request.method == 'GET':
        ir = ConsumirServicios.IR()

        fraseBusqueda = request.GET.get("busquedaIR")
        # IR.consultar(fraseBusqueda,"","")
        data = ir.consultar(fraseBusqueda,str(request.user.username),request.session['proyecto'])
        #data = funciones.busqueda(fraseBusqueda)
        #for d in data:
        #    d['path'] = d['path'].replace("/home/vigtech/shared/repository/", "/media/").encode("utf8")
        print data
        print fraseBusqueda
    else:
        print "Hi"
    return render(request, "GestionBusqueda/Busqueda_Navegacion.html", {'resultados': data, 'proyectos': proyectos_list, 'mproyecto': model_proyecto})


@login_required
def analisisView(request):
    global proyectos_list
    global model_proyecto

    #data = ConsumirServicios.consumir_red(request.user.username, request.session['proyecto'])
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    with open("/home/vigtech/shared/repository/" + proyecto + "/coautoria.json") as json_file:
        data = json.load(json_file)
    #nodos, aristas = r.generar_json()
    nodos1 = json.dumps(data['nodes'])
    aristas1 = json.dumps(data['links'])

   # return render(request, "GestionAnalisis/coautoria.html", {"nodos": nodos1, "aristas": aristas1})
    return render(request, "GestionAnalisis/coautoria.html", {"nodos": nodos1, "aristas": aristas1, 'proyectos': proyectos_list, 'mproyecto': model_proyecto})
    #return render(request, "GestionAnalisis/coautoria2.html", {"proyecto":proyecto})
@login_required
def coautoria_old(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    with open("/home/vigtech/shared/repository/" + proyecto + "/coautoria.json") as json_file:
        data = json.load(json_file)



    #nodos, aristas = r.generar_json()
    nodos1 = json.dumps(data['nodes'])
    aristas1 = json.dumps(data['links'])

   # return render(request, "GestionAnalisis/coautoria.html", {"nodos": nodos1, "aristas": aristas1})
    return render(request, "GestionAnalisis/Analisis.html", {"nodos": nodos1, "aristas": aristas1, 'proyectos': proyectos_list, 'mproyecto': model_proyecto})
    
@login_required
def eliminar_proyecto(request, id_proyecto):
    global model_proyecto
    global proyectos_list
    try:
        # print "#1"
        proyectos_list = get_list_or_404(proyecto,  idUsuario=self.request.user)
        # print "#2"
        model_proyecto = get_object_or_404(proyecto, id_proyecto=str(self.request.session['proyecto']))
        # print "#3"   
    except:
        proyectos_list = None
        model_proyecto = None


    user = request.user
    project = get_object_or_404(proyecto, id_proyecto=id_proyecto)
    funciones.eliminar_proyecto(id_proyecto, user)
    project.delete()
    messages.success(request, "El proyecto \""+project.nombre+"\" se elimino.")
    return HttpResponseRedirect(reverse('ver_mis_proyectos'))

@login_required
def analisis_paises(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    with open("/home/vigtech/shared/repository/" + proyecto + "/data.json") as json_file:
        data = json.load(json_file)
        print data
    labels=json.dumps(data['paises']['labels'])
    values=json.dumps(data['paises']['valores'])
    print proyecto
    #return render(request, "GestionAnalisis/paisesbar.html",{"labels": labels, "values": values})
    return render(request, "GestionAnalisis/paisesbar.html",{"proyecto":proyecto, 'proyectos': proyectos_list, 'mproyecto': model_proyecto})

@login_required
def analisis_autores(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    #return render(request, "GestionAnalisis/paisesbar.html",{"labels": labels, "values": values})
    return render(request, "GestionAnalisis/autoresbar.html",{"proyecto":proyecto,'proyectos': proyectos_list, 'mproyecto': model_proyecto})
@login_required
def analisis_afiliaciones(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    #return render(request, "GestionAnalisis/paisesbar.html",{"labels": labels, "values": values})
    return render(request, "GestionAnalisis/afiliacionesbar.html",{"proyecto":proyecto,'proyectos': proyectos_list, 'mproyecto': model_proyecto})
@login_required
def analisis_revistas(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    #return render(request, "GestionAnalisis/paisesbar.html",{"labels": labels, "values": values})
    return render(request, "GestionAnalisis/revistasbar.html",{"proyecto":proyecto,'proyectos': proyectos_list, 'mproyecto': model_proyecto})
@login_required
def analisis_docsfechas(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    #return render(request, "GestionAnalisis/paisesbar.html",{"labels": labels, "values": values})
    return render(request, "GestionAnalisis/fechasbar.html",{"proyecto":proyecto,'proyectos': proyectos_list, 'mproyecto': model_proyecto})
@login_required
def analisis_tipodocs(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    #return render(request, "GestionAnalisis/paisesbar.html",{"labels": labels, "values": values})
    return render(request, "GestionAnalisis/tiposbar.html",{"proyecto":proyecto,'proyectos': proyectos_list, 'mproyecto': model_proyecto})

@login_required
def analisis_paisespie(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    #return render(request, "GestionAnalisis/paisesbar.html",{"labels": labels, "values": values})
    return render(request, "GestionAnalisis/paisespie.html",{"proyecto":proyecto,'proyectos': proyectos_list, 'mproyecto': model_proyecto})

@login_required
def analisis_autorespie(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    #return render(request, "GestionAnalisis/paisesbar.html",{"labels": labels, "values": values})
    return render(request, "GestionAnalisis/autorespie.html",{"proyecto":proyecto, 'proyectos': proyectos_list, 'mproyecto': model_proyecto})
@login_required
def analisis_afiliacionespie(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    #return render(request, "GestionAnalisis/paisesbar.html",{"labels": labels, "values": values})
    return render(request, "GestionAnalisis/afiliacionespie.html",{"proyecto":proyecto,'proyectos': proyectos_list, 'mproyecto': model_proyecto})
@login_required
def analisis_revistaspie(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    #return render(request, "GestionAnalisis/paisesbar.html",{"labels": labels, "values": values})
    return render(request, "GestionAnalisis/revistaspie.html",{"proyecto":proyecto, 'proyectos': proyectos_list, 'mproyecto': model_proyecto})
@login_required
def analisis_docsfechaspie(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    #return render(request, "GestionAnalisis/paisesbar.html",{"labels": labels, "values": values})
    return render(request, "GestionAnalisis/fechaspie.html",{"proyecto":proyecto,'proyectos': proyectos_list, 'mproyecto': model_proyecto})
@login_required
def analisis_tipodocspie(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    #return render(request, "GestionAnalisis/paisesbar.html",{"labels": labels, "values": values})
    return render(request, "GestionAnalisis/tipospie.html",{"proyecto":proyecto, 'proyectos': proyectos_list, 'mproyecto': model_proyecto})
@login_required
def analisis_clustering(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    #return render(request, "GestionAnalisis/paisesbar.html",{"labels": labels, "values": values})
    return render(request, "GestionAnalisis/grupos.html",{"proyecto":proyecto, 'proyectos': proyectos_list, 'mproyecto': model_proyecto})

@login_required
def analisis_indicadores(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    with open("/home/vigtech/shared/repository/" + proyecto + "/data.json") as json_file:
        data = json.load(json_file)
        print data
    #labels=json.dumps(data['paises']['labels'])
    #values=json.dumps(data['paises']['valores'])
    #print proyecto
    #return render(request, "GestionAnalisis/paisesbar.html",{"labels": labels, "values": values})
    return render(request, "GestionAnalisis/indicadores.html",{"data":data, 'proyectos': proyectos_list, 'mproyecto': model_proyecto})

@login_required
def clasificacion_eisc(request):
    global proyectos_list
    global model_proyecto
    proyecto = str(request.user.username) + "." + str(request.session['proyecto'])
    with open("/home/vigtech/shared/repository/" + proyecto + "/eisc.json") as json_file:
        data = json.load(json_file)

    eids = data['clasificacion']
    adminBD = AdminBD()
    papers =adminBD.get_papers_eid(eids)
    return render (request, "GestionEISC/clasificacion_eisc.html", {"papers": papers, 'proyectos': proyectos_list, 'mproyecto': model_proyecto})


def logmensajes(request):
    if request.method == 'GET':
        global mensajes_pantalla
        response = {"mensaje": mensajes_pantalla}
        mensajes_pantalla =""
        return HttpResponse(json.dumps(response),content_type="application/json")
    else:
        return HttpResponse(json.dumps({"mensaje": ""}),content_type="application/json")


# def registrarusuario(request):
#     if request.method == 'GET':
#         return render(request, "registrarUsuario.html")
#     elif request.method == 'POST':
#         data = request.POST.get('nombre')
#         print data        
#         # messages.success(request, "Se ha creado exitosamente el usuario")
#         # return redirect('login')
#         return render (request, "registrarUsuario.html", {"response": data})        
#     else:
#         return render(request, "registrarUsuario.html")