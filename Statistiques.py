#!/usr/bin/python
# -*- coding: utf-8 -*-

from qgis.core import Qgis, QgsProject, QgsVectorLayer, QgsLayerTreeLayer, QgsDataSourceUri, QgsRasterLayer
from qgis.utils import iface
import psycopg2
import os
import re
import json

import matplotlib.pyplot as plt
import pandas as pd

class Statistiques:
    """ Second pour contenir quelques fonctions qui seront utilisées dans le fichier principale CheckOptyce.py """

    def __init__(self):
        """Le constructeur de ma classe
        Il prend pour attribut de classe les *** """

        home = os.path.expanduser("~")
        self.fichier = f"{home}/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/Densite/"

        idDatabase = []
        home = os.path.expanduser("~")
        self.fichier = f"{home}/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/Densite/"

        with open(f"{self.fichier}Connexion/id_mdp.json", "r") as f:
            identifiants = json.load(f)

        for cle, valeur in identifiants.items():
            idDatabase.append(valeur)

        [self.user, self.password, self.host, self.port, self.bd] = idDatabase

    def tempsEcouler(self, seconde):
        seconds = seconde % (24 * 3600)
        hour = int(seconds // 3600)
        seconds %= 3600
        minutes = int(seconds // 60)
        seconds %= 60
        return f"{hour}h: {minutes}mn : {int(seconds)}sec" if hour > 0 else f"{minutes}mn : {int(seconds)}sec"

    def alerteInfo(self, monMessage, duree=5):
        """Fonction pour afficher un message d'information à destination de l'utilisateur"""
        iface.messageBar().pushMessage("Message : ", monMessage, level=Qgis.Info, duration=duree)

    def verificationIdentifiantConnexionDatabase(self):
        """Pour ouvrir le fichier de connexion, permettant de récupérer les informations de connexion à
        la base de données"""

        # Identifiant et mot de passe de l'utilisateur de la base de données.
        identifiantErronner = False

        try:
            connection = psycopg2.connect(user=self.user,
                                          password=self.password,
                                          host=self.host,
                                          port=self.port,
                                          database=self.bd)

            connection.cursor()
        except (Exception, psycopg2.Error) as error:
            print("Précision de l'erreur : ", error)
            identifiantErronner = True

        return True if identifiantErronner else False

    def connectionBD(self, requete):
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

    def generateur(self, listeCommunes):
        """"""
        chemin = f"{self.fichier}requetes/Selection/stat.sql"
        with open(chemin, 'r') as fd:
            requete = fd.read()
            fd.close()

        requeteComplet = tuple(listeCommunes) if len(listeCommunes) > 1 else (f"('{listeCommunes[0]}')" if len(listeCommunes) == 1 else "")
        if requeteComplet:
            requete = requete.format(requeteComplet)

            resultat = self.connectionBD(requete)
            self.camembertStat(resultat)

    def camembertStat(self, data_stat):
        """Pour faire de la réprésentation statistique"""

        plt.figure(figsize=(8, 8))
        enregistrement = []
        labels = []
        nom = []
        explode = []
        for (nom_classe, superficie), exp in zip(data_stat, [0, 0.2, 0, 0, 0]):

            enregistrement.append(superficie)
            labels.append(f"{nom_classe}\n{int(superficie/10000)} ha")
            explode.append(exp)
            nom.append(nom_classe)

        # # x = [1, 2, 3, 4, 5]
        # # resultat : [('Territoire agricole', Decimal('6942046.68'))]
        # # plt.pie(enregistrement, labels=['A', 'B', 'C', 'D', 'E'],
        # plt.pie(enregistrement, labels=labels,
        #            colors=['red', 'green', 'yellow', "blue", "lightskyblue"],
        #            # explode=[0, 0.2, 0, 0, 0],
        #            explode=explode,
        #            autopct=lambda enregistrement: str(round(enregistrement, 2)) + '%',
        #            pctdistance=1, labeldistance=1.4)  # ,
        #            #  shadow=True)
        # plt.legend()
        #
        # plt.show()

        ####################################
        labels = labels
        sizes = enregistrement
        colors = ['red', 'green', 'yellow', "blue", "lightskyblue"]

        plt.pie(sizes, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90)

        plt.axis('equal')

        plt.savefig('PieChart01.png')
        plt.show()
