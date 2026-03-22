import math

from concurrent.futures import ThreadPoolExecutor

from Equipement_db import equipements

import csv

 

MAX_JOB = 20

# Fonction pour effectuer un walk sur l'OID spécifié et récupérer les résultats dans un dictionnaire

def walk_snmp(hostname, community_string, oid):

    resultats = {}

    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(

        SnmpEngine(),

        CommunityData(community_string),

        UdpTransportTarget((hostname, 161)),

        ContextData(),

        ObjectType(ObjectIdentity(oid)),
 
        lexicographicMode=False

    ):

        if errorIndication:

            print(f"Erreur SNMP : {errorIndication}")

            break

        elif errorStatus:

            print(f"Erreur SNMP : {errorStatus.prettyPrint()} à {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")

            break

        else:

            for varBind in varBinds:

                oid = varBind[0]

                valeur = varBind[1]

                index = oid.prettyPrint().split('.')[-1]  

                resultats[index] = valeur

    return resultats

 

def snmp_get(target, community, oid):

    iterator = getCmd(

        SnmpEngine(),

        CommunityData(community),

        UdpTransportTarget((target, 161)),

        ContextData(),

        ObjectType(ObjectIdentity(oid))

    )

 

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

 

    if errorIndication:

        print(f"Erreur SNMP : {errorIndication}")

        return None

    elif errorStatus:

        print(f"Erreur SNMP : {errorStatus.prettyPrint()}")

        return None

    else:

        for varBind in varBinds:

            return varBind[1]

 

# Fonction pour afficher les températures en corrélant avec les libellés, en ignorant les températures à -128

def afficher_temperature_correlee(hostname, community_string, resultats_global):

    print(f"\n Récupération de la température pour {hostname}")

    try:

        # Recuperation de la description de l'equipement pour determiner le type

        description = snmp_get(hostname, community_string, '1.3.6.1.2.1.1.1.0')

       

        # En tete CSV

        print("Hostname;Libelle element;Temperature")

 

        if "Cisco" in str(description):

            oid_libelles = '1.3.6.1.2.1.47.1.1.1.1.7'

            oid_temperature = '1.3.6.1.4.1.9.9.91.1.1.1.1.4'

           

            resultats_temperatures = walk_snmp(hostname, community_string, oid_temperature)

            resultats_libelles = walk_snmp(hostname, community_string, oid_libelles)

           

            for index, temperature in resultats_temperatures.items():

                if temperature != 0:

                    # Ignorer les températures à 0

                    libelle = resultats_libelles.get(index, "Libellé non trouvé")

                    #On recupere uniquement les valeurs qui contiennent le mot Temp et pas le mot Module

                    #On souhaite recuperer uniquement la valeur des cartes et non celle des modules SFP

                    if "temp" in str(libelle).lower() and "module" not in str(libelle).lower():

                        print(f"{hostname};{libelle};{temperature}")

                        resultats_global.append([hostname, libelle, temperature])

 

        elif "Nokia" in str(description):

            oid_temperature = '1.3.6.1.4.1.6527.3.1.2.2.1.8.1.18'

            oid_libelles = '1.3.6.1.4.1.6527.3.1.2.2.1.8.1.8'

           

            resultats_temperatures = walk_snmp(hostname, community_string, oid_temperature)

            resultats_libelles = walk_snmp(hostname, community_string, oid_libelles)

           

            for index, temperature in resultats_temperatures.items():

                if temperature != -128:

                    # Ignorer les températures à -128

                    libelle = resultats_libelles.get(index, "Libellé non trouvé")

                    print(f"{hostname};{libelle};{temperature}")

                    resultats_global.append([hostname, libelle, temperature])

 

        elif "Huawei" in str(description):

            oid_temperature = '1.3.6.1.4.1.2011.5.25.31.1.1.1.1.11'

            oid_libelles = '1.3.6.1.2.1.47.1.1.1.1.7'

           

            resultats_temperatures = walk_snmp(hostname, community_string, oid_temperature)

            resultats_libelles = walk_snmp(hostname, community_string, oid_libelles)

 

            for index, temperature in resultats_temperatures.items():

                if temperature != 0:

                    # Ignorer les températures à 0

                    libelle = resultats_libelles.get(index, "Libellé non trouvé")

                    print(f"{hostname};{libelle};{temperature}")

                    resultats_global.append([hostname, libelle, temperature])

 

    except Exception as e:

        print(f"Erreur lors de la récupération des températures pour {hostname}: {e}")

 

if __name__ == '__main__':

    # Menu de selection du site

    sites = list(equipements.keys())

    print("Veuillez choisir un site :")

    for i, site_name in enumerate(sites):

        print(f"{i + 1}. {site_name}")

 

    index_site_selectionne = -1

    while not (0 < index_site_selectionne <= len(sites)):

        try:

            index_site_selectionne = int(input("Entrez le numéro du site : "))

            if not (0 < index_site_selectionne <= len(sites)):

                print("Numéro de site invalide. Veuillez réessayer.")

        except ValueError:

            print("Entrée invalide. Veuillez entrer un nombre.")

 

    nom_site = sites[index_site_selectionne - 1]

    print(f"\nVous avez choisi le site : {nom_site}")

 

    equipments_du_site_brut = equipements[nom_site]

   

    # Creer une liste aplatie des equipements pour faciliter la selection

    liste_equipments_complete = []

    for item in equipments_du_site_brut:

        for hostname, community in item.items():

            liste_equipments_complete.append({'hostname': hostname, 'community': community if community else 'public'})

   

    # Nouveau sous menu pour le type de groupe d'équipement

    types_group = sorted(list(set([eq['hostname'][:3] for eq in liste_equipments_complete])))

    print("\nVeuillez choisir un type de groupe d'équipement :")

    print("0. Tous les groupes")  # Option pour sélectionner tous les équipements sans filtrer par groupe

    for i, group in enumerate(types_group):

        print(f"{i + 1}. {group}")

 

    index_group_selectionne = -1

    type_group_selectionne = None

    while True:

        try:

            index_group_selectionne = int(input("Entrez le numéro du type de groupe : "))

            if index_group_selectionne == 0:

                type_group_selectionne = "all"

                break

            elif 0 < index_group_selectionne <= len(types_group):

                type_group_selectionne = types_group[index_group_selectionne - 1]

                break

            else:

                print("Numéro de groupe invalide. Veuillez réessayer.")

        except ValueError:

            print("Entrée invalide. Veuillez entrer un nombre.")

 

    liste_equipments_filtree = []

    if type_group_selectionne == "all":

        liste_equipments_filtree = liste_equipments_complete

        print(f"\nVous avez choisi tous les groupes d'équipements pour le site : {nom_site}")

    else:

        # Filtre les équipements en fonction du type de groupe sélectionné

        liste_equipments_filtree = [eq_data for eq_data in liste_equipments_complete if eq_data['hostname'].startswith(type_group_selectionne)]

        print(f"\nVous avez choisi le groupe d'équipements : {type_group_selectionne} pour le site : {nom_site}")

 

    if not liste_equipments_filtree:

        print("Aucun équipement trouvé pour le groupe sélectionné. Fin du script.")

    else:

        # Menu de sélection pour un ou plusieurs équipements

        print("\nSouhaitez-vous vérifier la température pour :")

        print("1. Un seul équipement")

        print("2. Plusieurs équipements (par nom)")

        print("3. Tous les équipements du groupe sélectionné")

 

        choix_mode_equipement = -1

        while not (0 < choix_mode_equipement <= 3):

            try:

                choix_mode_equipement = int(input("Entrez votre choix (1, 2 ou 3) : "))

                if not (0 < choix_mode_equipement <= 3):

                    print("Choix invalide. Veuillez entrer 1, 2 ou 3.")

            except ValueError:

                print("Entrée invalide. Veuillez entrer un nombre.")

 

        equipments_a_traiter = []

        # Sélection d'un seul équipement

        if choix_mode_equipement == 1:

            print(f"\nVeuillez choisir un équipement parmi les {len(liste_equipments_filtree)} disponibles :")

            for i, eq_data in enumerate(liste_equipments_filtree):

                print(f"{i + 1}. {eq_data['hostname']}")

 

            index_equipement_selectionne = -1

            while not (0 < index_equipement_selectionne <= len(liste_equipments_filtree)):

                try:

                    index_equipement_selectionne = int(input("Entrez le numéro de l'équipement : "))

                    if not (0 < index_equipement_selectionne <= len(liste_equipments_filtree)):

                        print("Numéro d'équipement invalide. Veuillez réessayer.")

                except ValueError:

                    print("Entrée invalide. Veuillez entrer un nombre.")

 

            choix_equipment_data = liste_equipments_filtree[index_equipement_selectionne - 1]

            equipments_a_traiter.append(choix_equipment_data)

 

        elif choix_mode_equipement == 2:

            print("\nEntrez les noms des équipements à vérifier, séparés par des virgules :")

            noms_entres = input().split(',')

            noms_entres = [n.strip() for n in noms_entres if n.strip()]

            for nom in noms_entres:

                eq_trouve = next((eq for eq in liste_equipments_filtree if eq['hostname'].lower() == nom.lower()), None)

                if eq_trouve:

                    equipments_a_traiter.append(eq_trouve)

                else:

                    print(f"Attention : L'équipement '{nom}' n'a pas été trouvé.")

            if not equipments_a_traiter:

                print("Aucun équipement valide sélectionné. Fin du script.")

 

        elif choix_mode_equipement == 3:

            equipments_a_traiter = liste_equipments_filtree

            print(f"\nVous avez choisi de vérifier tous les {len(equipments_a_traiter)} équipements du groupe '{type_group_selectionne}'.")

 

        # Liste pour stocker les résultats

        resultats_global = []

 

        for eq_data in equipments_a_traiter:

            choix_hostname = eq_data['hostname']

            choix_community = eq_data['community']

            afficher_temperature_correlee(choix_hostname, choix_community, resultats_global)

 

        # export CSV

        if resultats_global:

            choix_export = input("\nVoulez-vous enregistrer ces résultats dans un fichier CSV ? (o/n) : ").strip().lower()

            if choix_export == 'o':

                nom_fichier = input("Entrez le nom du fichier CSV (ex: resultats_temp.csv) : ").strip()

                with open(nom_fichier, mode='w', newline='', encoding='utf-8') as fichier_csv:

                    writer = csv.writer(fichier_csv, delimiter=';')

                    writer.writerow(["Hostname", "Libelle element", "Temperature"])

                    writer.writerows(resultats_global)

                print(f"Résultats enregistrés dans {nom_fichier}")
