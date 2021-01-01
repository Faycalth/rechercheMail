#récupère adresse mail à partir d'une liste de nom d'entreprise 
#libraries
from bs4 import BeautifulSoup
import urllib.request
from urllib.request import Request, urlopen
import urllib.parse
import csv
import time
import os
import re

def main():
    fichier_src = getNomFichier()
    maj_csv(fichier_src)

def getNomFichier():
    nom_fichier = "etablissementsInformatique.csv"
    if os.path.isfile(nom_fichier):
        return nom_fichier
    else:
        raise NameError("Erreur, le fichier n'est pas dans le dossier")

def getNomEntreprise(source):
    liste_nom = []
    with open(source, "r") as fichier_src:
        reader = csv.DictReader(fichier_src)
        for row in reader:
            nom = row['Nom']
            liste_nom.append(nom.lower())
    return liste_nom

def get_url(nom):
    url = "https://www.google.com/search?q="+nom
    req = Request(url.replace(" ", "+"), headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read()
    soup = BeautifulSoup(page, 'html.parser')
    url_site = ""

    #recherche dans la recherche
    try:
        page_recherche = soup.find("body")
        resultats = page_recherche.find_all("a")

        #liste de tous les liens
        liste_liens = []
        
        for r in resultats:
            x = nom.split(" ")
            if "www."+x[0] in r.get('href'):
                #extraction du nom de domaine
                liste_liens.append(r.get("href"))
                l2 = liste_liens[0].split("/")
                url_site = l2[3]
                break
    except:
        pass
            
    return url_site
  
def get_mail(url):           
    url_site = "https://www.google.com/search?q="+url+"+contact"
    req_site = Request(url_site, headers={'User-Agent': 'Mozilla/5.0'})
    page_site = urlopen(req_site).read()
    soup_site = BeautifulSoup(page_site, 'html.parser')
    

    #recherche dans la recherche
    try:
        page_contact = soup_site.find("body")
        resultats_contact = page_contact.find_all("div")

        liste = []
        for r in resultats_contact:
            liste.append(r.getText())
        
        #extraction mail
        liste_mail = []
        regex = "\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b" #pattern mail
        for l in liste:
            if "@" in l:
                liste_mail = extraireMail(l)

    except:
        pass
    
    return liste_mail 

def extraireMail(texte):
    pattern = "\S+@+\S+"
    liste = re.findall(pattern, texte)
    liste_mail = []
    for l in liste:
        if l.replace(" ", "") not in liste_mail:
            liste_mail.append(l)

    return liste_mail 
                

def maj_csv(source):
    with open("contactEntreprise.csv", "w", newline='') as maj_fichier, open(source, "r") as fichier_src:
        fieldnames = ["Categorie","Nom","Code Postal","Ville","Activite principale","Site Web","Contact"]

        writer = csv.DictWriter(maj_fichier, fieldnames=fieldnames, restval="")
        writer.writeheader()

        reader = csv.DictReader(fichier_src)    

        liste_nom_ent = getNomEntreprise(source)
        k = 0
        for row in reader:
            nom = row["Nom"].lower()
            if nom in liste_nom_ent:
                site_web = get_url(nom)
                if site_web:
                    contact = get_mail(site_web)
                else:
                    contact = []
                    break
                
                writer.writerow({
                    'Categorie': row["Categorie"],
                    'Nom': row["Nom"],
                    'Ville': row["Ville"], 
                    'Code Postal': row["Code Postal"],
                    'Activite principale': row["Activite principale"],
                    'Site Web': site_web,
                    'Contact': contact
                })
                k+=1
            time.sleep(2)
 
        print("Programme terminé | ", str(k), " adresses mails trouvées")         
              
#Programme
start_time = time.time()
main()
print("Temps d'execution = " + str(time.time() - start_time) + " secondes")
