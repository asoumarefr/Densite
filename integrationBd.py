#!/usr/bin/python
# -*-coding:Utf-8-*-

import os
import psycopg2
import json
from qgis.core import QgsProject, QgsExpression, QgsFeatureRequest, NULL
# import pandas as pd
# import numpy as np

# Fichier creer poour contenir les fonctions qui font etre utilisees dans la mise en place du plugin C3A
# import psycopg2 # Utilise pour la connexion a la base de donnees


class IntegrationBd:
    """ Classe qui fait tout le travail pour accéder à la base de données,
    Réaliser des requêtes dans la base de données """

    def __init__(self):

        home = os.path.expanduser("~")
        self.fichier = f"{home}/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/Densite/"

        with open(f"{self.fichier}Connexion/id_mdp.json", "r") as f:
            identifiants = json.load(f)
            f.close()

        id_database = (valeur for valeur in identifiants.values())
        [self.user, self.password, self.host, self.port, self.bd] = id_database

    def connection_bd(self, requete):
        """Pour se connecter à la base de données"""
        connection = None
        cursor = None
        record = []

        if requete:
            try:
                connection = psycopg2.connect(user=self.user,
                                              password=self.password,
                                              host=self.host,
                                              port=self.port,
                                              database=self.bd)

                cursor = connection.cursor()

                cursor.execute(requete)
                record = cursor.fetchall()

            except (Exception, psycopg2.Error) as error:
                print(f"Erreur de connexion à la base de données PostgreSQL {error}")

            finally:
                # closing database connection.
                if connection:
                    cursor.close()
                    connection.close()
                    # self.alerteInfos(u"La requete a bien été executée", "T", "green")
        return record

    def integration(self):
        """Récupération des fichier SQL et execution des requetes pour l'intégration des données dans la base"""
        erreurs = []

        connection = psycopg2.connect(user=self.user,
                                      password=self.password,
                                      host=self.host,
                                      port=self.port,
                                      database=self.bd)
        cursor = connection.cursor()

        listes_dossiers = ["Creation", "Trigger"]
        # Creation des tables et des triggers
        for dossier in listes_dossiers:
            for subdir, dirs, fichier in os.walk(f"{self.fichier}requetes/{dossier}/"):
                for name in fichier:
                    if name.endswith(".sql"):
                        filepath = subdir + os.sep + name
                        with open(filepath, 'r') as fd:
                            sqlFile = fd.read()
                            fd.close()
                            reponse = self.execution_requete_sql(connection, cursor, sqlFile)
                            if reponse:
                                erreurs.append(reponse)

        cursor.close()
        connection.close()

        return erreurs

    def execution_requete_sql(self, connection, cursor, requete):
        """Execution requete SQL"""
        erreur = None
        try:
            cursor.execute(requete)
            connection.commit()
        except (Exception, psycopg2.Error) as e:
            print(f"Erreur : {e}")
            connection.rollback()
            erreur = e

        return erreur

    def insert_donnees_bd(self, data_global, fichier):
        """Insertion des données dans la base"""
        erreur = False
        connection = psycopg2.connect(user=self.user,
                                      password=self.password,
                                      host=self.host,
                                      port=self.port,
                                      database=self.bd)
        cursor = connection.cursor()

        chemin = f"{self.fichier}requetes/Insertion/{fichier}.sql"
        with open(chemin, 'r') as fd:
            requete = fd.read()
            fd.close()

        try:
            for entregistrement in data_global:
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

    def recup_valeur_enregistrements_ocs(self, table_ocs, champs_code_ocs):
        """Récupérer les données liées à la base de données"""
        ocs_table = QgsProject.instance().mapLayersByName(table_ocs)[0]
        data_global = []

        for feat_ocs in ocs_table.getFeatures():  # request
            if feat_ocs.geometry() and feat_ocs.geometry() != NULL:
                data_global.append((int(feat_ocs[champs_code_ocs]), feat_ocs.geometry().asWkt()))

        return data_global
    
    def recup_valeur_enregistrements_commune(self, table_commune, champs_nom, champs_insee, champs_dept):
        """Récupérer les données liées à la base de données"""

        commune_table = QgsProject.instance().mapLayersByName(table_commune)[0]

        data_global = []
        doublon_geom = []
        for feat_commune in commune_table.getFeatures():
            if feat_commune.geometry() and feat_commune.geometry() != NULL and feat_commune.geometry() not in doublon_geom:
                data_global.append((feat_commune[champs_nom], feat_commune[champs_insee],
                                    int(feat_commune["population"]), feat_commune[champs_dept], feat_commune.geometry().asWkt()))
                doublon_geom.append(feat_commune.geometry())

        return data_global
