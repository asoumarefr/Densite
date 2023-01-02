#!/usr/bin/python
# -*-coding:Utf-8-*-

import os
import json
import psycopg2
import pandas as pd
import numpy as np
from qgis.core import QgsProject, QgsExpression, QgsFeatureRequest, NULL

# Fichier creer poour contenir les fonctions qui font etre utilisees dans la mise en place du plugin C3A
# import psycopg2 # Utilise pour la connexion a la base de donnees


class IntegrationBd:
    """ Classe qui fait tout le travail pour accéder à la base de données,
    Réaliser des requêtes dans la base de données,
    Exporter le résultat des requêtes vers le fichier Excel """

    def __init__(self):
        idDatabase = []

        home = os.path.expanduser("~")
        self.fichier = f"{home}/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/Densite/"

        with open(f"{self.fichier}Connexion/id_mdp.json", "r") as f:
            identifiants = json.load(f)

        for cle, valeur in identifiants.items():
            idDatabase.append(valeur)

        [self.user, self.password, self.host, self.port, self.bd] = idDatabase

    def integration(self):
        """Récupération des fichier SQL et execution des requetes pour l'intégration des données dans la base"""
        erreurs = []

        connection = psycopg2.connect(user=self.user,
                                      password=self.password,
                                      host=self.host,
                                      port=self.port,
                                      database=self.bd)
        cursor = connection.cursor()

        listesDossier = ["Creation", "Trigger"]
        # Creation des tables et des triggers
        for dossier in listesDossier:
            for subdir, dirs, files in os.walk(f"{self.fichier}requetes/{dossier}/"):
                for name in files:
                    if name.endswith(".sql"):
                        filepath = subdir + os.sep + name
                        with open(filepath, 'r') as fd:
                            sqlFile = fd.read()
                            fd.close()
                            reponse = self.executionRequeteSQl(connection, cursor, sqlFile)
                            if reponse:
                                erreurs.append(reponse)

        cursor.close()
        connection.close()

        return erreurs

    def executionRequeteSQl(self, connection, cursor, requete):
        """Execution requete SQL"""
        # connection = None
        # cursor = None
        erreur = None
        try:
            # connection = psycopg2.connect(user=self.user,
            #                               password=self.password,
            #                               host=self.host,
            #                               port=self.port,
            #                               database=self.bd)

            # cursor = connection.cursor()
            cursor.execute(requete)
            connection.commit()
        except (Exception, psycopg2.Error) as e:
            print(f"Erreur : {e}")
            connection.rollback()
            erreur = e

        # finally:
        #     cursor.close()
        #     connection.close()

        return erreur

    def lists_ocs_data_insert_bd(self, table_ocs, champs_code_ocs):
        """Récupérer les données liées à la base de données"""
        ocs_table = QgsProject.instance().mapLayersByName(table_ocs)[0]

        # classe_12 = []
        # geom = []

        # requete = QgsExpression("geom IS NOT NULL and st_valid(geom) = True")
        # request = QgsFeatureRequest(requete)
        # clause = QgsFeatureRequest.OrderByClause('inf_type', ascending=True)
        # orderby = QgsFeatureRequest.OrderBy([clause])
        # request.setOrderBy(orderby)

        data_global = []

        # compte = 0
        for feat_ocs in ocs_table.getFeatures():  # request
            if feat_ocs.geometry() and feat_ocs.geometry() != NULL:
                # geom.append(feat_ocs.geometry())
                # classe_12.append(int(feat_ocs["classe_12"]))
                # data_global.append((int(feat_ocs[champs_code_ocs]), f"ST_SetSRID(ST_GeomFromText({feat_ocs.geometry().asWkt()}), 2154"))
                data_global.append((int(feat_ocs[champs_code_ocs]), feat_ocs.geometry().asWkt()))
                # compte += 1
                # if compte > 3:
                #     break

        return data_global

    def insert_donnees_ocs(self, data_global, fichier):
        """Insertion des données dans la base"""
        connection = psycopg2.connect(user=self.user,
                                      password=self.password,
                                      host=self.host,
                                      port=self.port,
                                      database=self.bd)
        cursor = connection.cursor()

        chemin = f"{self.fichier}requetes/Insertion/{fichier}.sql"
        erreur = False
        with open(chemin, 'r') as fd:
            requete = fd.read()
            fd.close()
        # print(f"requete : {requete}")
        try:
            for entregistrement in data_global:
                # print(f"entregistrement : {entregistrement}\n\n")
                cursor.execute(requete, entregistrement)
                connection.commit()

        except (Exception, psycopg2.Error) as e:
            print(f"Erreur : {e}")
            connection.rollback()
            erreur = True

        finally:
            cursor.close()
            connection.close()

        return erreur

    def lists_commune_data_insert_bd(self, table_commune, champs_nom, champs_insee, champs_pop):
        """Récupérer les données liées à la base de données"""
        commune_table = QgsProject.instance().mapLayersByName(table_commune)[0]

        data_global = []
        # compte = 0
        doublonGeom = []
        for feat_commune in commune_table.getFeatures():  # request
            if feat_commune.geometry() and feat_commune.geometry() != NULL and feat_commune.geometry() not in doublonGeom:
                data_global.append((feat_commune[champs_nom], feat_commune[champs_insee],
                                    int(feat_commune[champs_pop]), int(feat_commune["code_dept"]), feat_commune.geometry().asWkt()))
                doublonGeom.append(feat_commune.geometry())
                # compte += 1
                # if compte > 3:
                #     break
        return data_global
