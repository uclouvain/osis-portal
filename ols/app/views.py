from django.shortcuts import render
from django.http import HttpResponse
import datetime

from .models import Student, Offer, OfferEnrollment, OfferYear, Configuration


def index(request):
    now = datetime.datetime.now()
    
    html = "<html>"
    html += "<head>"
    html += "<link type='text/css' href='http://www.uclouvain.be/cps/ucl/styles/bv_page.css' rel='stylesheet' />"
    html += "<link type='text/css' href='http://www.uclouvain.be/cps/ucl/styles/ucl_page_print.css' rel='stylesheet' media='print' />"
    html += "<style>"
    html += ".titre{color:#639443;border-bottom:1px solid #AAB537;}"
    
    html += "</style>"
    
    students = Student.objects.filter(name__isnull=False).order_by('name')
    html += "</head>"
    html += "<body>"
    html += "<br/>"
    html += "<div class='composant-corps texte-base'>"           
    for student in students:
        html += "<table style='width:100%'>"
        html += "<tr><td colspan='3'><span class='titre'>Identification de l'étudiant</span></td></tr>"
        html += "<tr>"
        html += "<td style='width:250px;'>"
        html += "Nom"
        html += " prénom"
        html += "</td>"
        html += "<td>"
        html += "{0}  {1}".format(student.name, student.first_name1)
        html += "</td>"
        html += "<td>"
        html += "</td>"        
        html += "</tr>"
        html += "<tr>"
        html += "<td>"
        html += " Numéro de matricule"
        html += "</td>"
        html += "<td>"
        html += "{0}".format(student.registration_number)
        html += "</td>"
        html += "<td>"
        html += "</td>"          
        html += "</tr>"  
        html += "</table>"        
    
        html += "<table>"
        html += "<tr>"
        html += "<td colspan='3'>"
        html += "<table width='600px'>"
        html += "<tr>"
        html += "<td colspan='3'>"
        html += " <span class='titre'>Mes années d'études</span>"
        html += "</td>"
        html += "</tr>"
        html += "<tr>"
        html += "<th>"
        html += "Année"
        html += "</th>"
        html += "<th>"
        html += "Sigle"
        html += "</th>"
        html += "<th>"
        html += "Année d'études"
        html += "</th>"            
        html += "</tr>"       
        html += "<br/>"       
        for offer_enrollment in student.offer_enrollments() :
            offer = offer_enrollment.offer_year.offer
            html += "<tr>"
            html += "<td>"
            html += "{0}-{1}".format(offer_enrollment.academic_year.year, offer_enrollment.academic_year.year+1)
            html += "</td>"
            # html += "<td><a href='app/student/id_student="+ str(student.id) +"/id_offer_year="+str(offer_enrollment.offer_year.id)+"'>"
            html += "<td><a href='app/student/"+ str(student.id) +"/"+str(offer_enrollment.offer_year.id)+"/"+str(offer_enrollment.academic_year.year)+"'>"
            html += "{0} {1} {2} {3} {4}".format(offer.acronym,offer.cycle,offer.level,offer.offer_type,offer.orientation)
            html += "</a></td>"
            html += "<td>"
            html += "{0}".format(offer_enrollment.offer_year.title)
            html += "</td>"            
            html += "</tr>"   


        html += "</table>"
    

    html += "<br/>"
    html += "</div>"
    html += "</body></html>"
    return HttpResponse(html)

        
def student(request,id_student,id_offer_year,year):
 
    html = "<html>"
    html += "<head>"
    
    html += "<link type='text/css' href='http://www.uclouvain.be/cps/ucl/styles/bv_page.css' rel='stylesheet' />"
    html += "<link type='text/css' href='http://www.uclouvain.be/cps/ucl/styles/ucl_page_print.css' rel='stylesheet' media='print' />"
    html += "<style>"
    html += ".titre{color:#639443;border-bottom:1px solid #AAB537;}"
    
    html += "</style>"
    
    
    html += "</head>"
    html += "<body>"

    student = Student.objects.get(id=id_student)
    offer_year = OfferYear.objects.get(id=id_offer_year)
        
    html += "<div class='composant-corps texte-base'>"           
    html += "    <table border='0' cellpadding='2' cellspacing='2' width='100%'>"
    html += "<tr>"
    html += "<td class='composant-libelle' width='150'>Nom Prénom</td><td>{0} {1}</td>".format(student.name, student.first_name1)
    html += "</tr>"
    html += "<tr>"
    html += "<td class='composant-libelle'>Année académique</td><td>{0} - {1}</td>".format(year , int(year) + 1)
    html += "</tr>"
    html += "<tr>"
    
    html += "<td class='composant-libelle' valign='top'>Année d\'études</td><td>{0} {1} {2} {3} {4} {5} </td>".format(offer_year.offer.acronym,offer_year.offer.cycle,offer_year.offer.level,offer_year.offer.offer_type,offer_year.offer.orientation,offer_year.title)
    html += "</tr>"
    html += "</table>"
    html += "<br>"
    html += "<table border='0' cellpadding='2' cellspacing='2' width='100%'>"
    html += "<tr>"
    html += "<td colspan='8'></td>"
    html += "</tr>"
    html += "<tr>"
    html += "<td colspan='2'></td><td align='right' class='composant-titre-inter'>ECTS</td><td></td><td align='center' class='composant-titre-inter' width='50'>Janv.</td><td align='center' class='composant-titre-inter' width='50'>Juin</td><td align='center' class='composant-titre-inter' width='50'>Sept.</td><td></td>"
    html += "</tr>"
    html += "<tr>"
    html += "<td></td><td align='right'><strong>Total ECTS / Inscription</strong></td><td align='right'>60.0</td><td></td><td align='center'>IS</td><td align='center'>EP</td><td align='center'>-</td><td></td>"
    html += "</tr>"
    html += "<tr>"
    html += "<td></td><td align='right'><strong>Moyenne</strong></td><td colspan='2'></td><td align='center'>-</td><td align='center'>15.95</td><td align='center'>-</td><td></td>"
    html += "</tr>"
    html += "<tr>"
    html += "<td></td><td align='right'><strong>Mention</strong></td><td colspan='2'></td><td align='center'>PRST</td><td align='center'>R</td><td align='center'>-</td><td></td>"
    html += "</tr>"
    html += "<tr>"
    html += "<td></td><td align='right'><strong>Inscriptions aux examens</strong></td><td colspan='2'></td><td align='center'></td><td align='center'></td><td align='center'></td><td></td>"
    html += "</tr>"
    html += "<tr>"
    html += "<td class='composant-titre-inter'>Cours</td><td class='composant-titre-inter'>Intitulé</td><td align='right' class='composant-titre-inter'>ECTS</td><td align='center' class='composant-titre-inter'>Insc.</td><td align='center' class='composant-titre-inter' width='50'>Janv.</td><td align='center' class='composant-titre-inter' width='50'>Juin</td><td align='center' class='composant-titre-inter' width='50'>Sept.</td><td class='composant-titre-inter'>Crédit</td>"
    html += "</tr>"
    for learning_unit_enrollment in student.learning_unit_enrollments():
        
        learning_unit_year=learning_unit_enrollment.learning_unit_year
        l = learning_unit_year.learning_unit
        html += "<tr class='composant-ligne1' valign='top'>"
        html += "<td>{0} {1}</td><td>{2}</td><td align='right'>{3}</td><td align='center'>Insc.</td><td>".format(l.acronym,l.number,l.title,learning_unit_year.weight) 
   
        html += "<table border='0' cellpadding='0' cellspacing='0' width='100%'>"
        html += "<tr>"
        html += "<td align='right' width='34'>"
        html += "{0}".format(learning_unit_year.score_1)
        html += "</td><td align='left' width='1'></td><td align='left' width='15%'>{0}</td>".format(learning_unit_year.exam_state_1 )
        html += "</tr>"
        html += "</table>"
        html += "</td><td>"
        html += "<table border='0' cellpadding='0' cellspacing='0' width='100%'>"
        html += "<tr>"
        html += "<td align='right' width='34'>{0}</td><td align='left' width='1'></td><td align='left' width='15%'>{1}</td>".format(learning_unit_year.score_2,learning_unit_year.exam_state_2)
        html += "</tr>"
        html += "</table>"
        html += "</td><td>"
        html += "<table border='0' cellpadding='0' cellspacing='0' width='100%'>"
        html += "<tr>"
        html += "<td align='right' width='34'>{0}</td><td align='left' width='1'></td><td align='left' width='15%'>{1}</td>".format(learning_unit_year.score_3,learning_unit_year.exam_state_3)
        html += "</tr>"
        html += "</table>"
        html += "</td><td align='center'>{0}</td>".format(learning_unit_year.credit_type)
        html += "</tr>"


    html += "</table>"
    html += "<p>"
    html += "</p>"
    html += "<p style='padding:10px;background-color:#FCE4AE'>(Session de  juin)  Vous avez acquis la totalité des crédits de votre programme annuel. Vous êtes admis à poursuivre votre cycle d\'études  dans le respect des autres conditions d’admission et de financement. </p>"
    html += "<table align='center' border='0' cellpadding='2' cellspacing='2'>"
    html += "<tr class='texte-petit'>"
    html += "<td class='composant-titre-inter' colspan='4'>Légende</td>"
    html += "</tr>"
    html += "<tr class='texte-petit'>"
    html += "<td width='15'>P</td><td width='150'>Examen partiel</td><td width='15'>T</td><td width='150'>Note résultant d\'un test</td>"
    html += "</tr>"
    html += "<tr class='texte-petit'>"
    html += "<td>I</td><td>Première inscription</td><td>V</td><td>Evaluation satisfaisante (la note ne compte pas)</td>"
    html += "</tr>"
    html += "<tr class='texte-petit'>"
    html += "<td>Y</td><td>Deuxième inscription</td><td>W</td><td>Evaluation non satisfaisante (la note ne compte pas)</td>"
    html += "</tr>"
    html += "<tr class='texte-petit'>"
    html += "<td>R,J</td><td>Report de note</td><td>EPM</td><td>Cours reporté (Epreuve modifiée)</td>"
    html += "</tr>"
    html += "<tr class='texte-petit'>"
    html += "<td>B</td><td>Crédit (Bologne)</td><td></td><td></td>"
    html += "</tr>"
    html += "</table>"
    html += "<p align='center' style='color:red'>"
    html += "Attention : à partir de juin 2009, la moyenne est exprimée sur un maximum de 20."
    html += "</p>"
    # html += "<p class='non-imprime4'>&gt; Retour à la <a href='retour'>liste de mes années d\'études</a></p>"


    html += "</div>"
    html += "</div>"

    html += " </td>"
    html += "</tr>"
    html += "</table>"
    html += "</div>"
    
    
    
    
    
    html += "</body>"
    html += "</html>"
    return HttpResponse(html)
    

def attestations(request):
    avisDispoNonImprime=True
    avisDispoDejaImprime=False
    deDispoNonImprime=True
    deDispoDejaImprime=False
    abcDispoNonImprime=True
    abcDispoDejaImprime=False
    echeanceDispoNonImprime=True
    echeanceDispoDejaImprime=False
    docDisponibles=True
    inscritPourCetteAnnee=True
    configuration = Configuration.objects.get(key='DEF0021_ETD')
    if configuration:
        anac=configuration.value
    else :
        anac=2015
    
    texte_avis="Votre attestation \'<b>avis d'enregistrement + facture</b>\' {0}-{1} <font style=\'color:green\'>est disponible</font> et peut être imprimée".format(anac, int(anac)+1)
    if avisDispoDejaImprime:
        texte_avis="Votre attestation 'avis d'enregistrement + facture' {0}-{1} a déjà été imprimée mais est toujours disponible".format(anac, int(anac)+1)
    
    texte_de = "Votre attestation \'<b>Carte d'étudiant provisoire + transports en commun</b>\' {0}-{1} <font style=\'color:green\'>est disponible</font> et peut être imprimée".format(anac, int(anac)+1)    
    if deDispoDejaImprime:
        texte_de = "Votre attestation 'Carte d'étudiant provisoire + transports en commun' {0}-{1} a déjà été imprimée mais est toujours disponible".format(anac, int(anac)+1)
        
    texte_alloc ="Votre attestation d\'inscription régulière \'<b>le cas échéant, pour les allocations familiales, mutuelles, ...</b>\'"
    texte_alloc += " {0}-{1} <font style=\'color:green\'>est disponible</font> et peut être imprimée".format(anac, int(anac)+1)
    if abcDispoDejaImprime: 
        texte_alloc = "Votre attestation d\'inscription régulière \'<b>le cas échéant, pour les allocations familiales, mutuelles, ...</b>"
        texte_alloc += "\' {0}-{1} <font style=\'color:orange\'>a déjà été imprimée</font> mais est toujours disponible".format(anac, int(anac)+1)  

    texte_echeance = "Votre document <b>avis d'échéance</b> {0}-{1} <font style='color:green'>est disponible</font> et peut être imprimé".format(anac, int(anac)+1)    
    if echeanceDispoDejaImprime:
        texte_echeance = "<Votre document \'<b>avis d'échéance</b>\' {0}-{1}"
        texte_echeance += " <font style=\'color:orange\'>a déjà été imprimé</font> mais est toujours disponible".format(anac, int(anac)+1)  
    
    html = "<html>"
    html += "<head>"
    html += "<link type='text/css' href='http://www.uclouvain.be/cps/ucl/styles/bv_page.css' rel='stylesheet' />"
    html += "<link type='text/css' href='http://www.uclouvain.be/cps/ucl/styles/ucl_page_print.css' rel='stylesheet' media='print' />"
    html += "<style>"
    html += ".titre{color:#639443;border-bottom:1px solid #AAB537;}"
    html += ".printingButton{width:200px;}"
    html += "</style>"
    
    students = Student.objects.filter(name__isnull=False).order_by('name')
    html += "</head>"
    html += "<body>"
    html += "<div class='composant-corps texte-base'>"
    student = Student.objects.get(id=1)
    html += "<form>"
    html += "<table>"
    html += "<tr>"
    html += "<td>{0}</td><td><input type='submit' value='Avis' class='printingButton'/><td/>".format(texte_avis)
    html += "</tr>"
    html += "<tr>"
    html += "<td>{0}</td><td><input type='submit' value='De' class='printingButton'/><td/>".format(texte_de)
    html += "</tr>"    
    html += "<tr>"
    html += "<td>{0}</td><td><input type='submit' value='Allocations' class='printingButton'/><td/>".format(texte_alloc)
    html += "</tr>"    
    html += "<tr>"
    html += "<td>{0}</td><td><input type='submit' value='Avis' class='printingButton'/><td/>".format(texte_echeance)
    html += "</tr>"
    html += "</table>"
    html += "</form>"
    html += "</div>"
    html += "</body></html>"
    return HttpResponse(html)    