import os
import psycopg2
import json
from qgis.core import QgsProject, NULL


class IntegrationBd:
    """ Classe qui fait tout le travail pour accéder à la base de données,
    Réaliser des requêtes dans la base de données """

    def __init__(self):
        home = os.path.expanduser("~")
        # TODO mettre le lien relatif du schemin
        self.fichier = f"{home}/.local/share/QGIS/QGIS3/profiles/default/python/plugins/Densite/"

        with open(f"{self.fichier}connexion/id_mdp.json", "r") as f:
            identifiants = json.load(f)
            f.close()

        id_database = iter(identifiants.values())
        [self.user, self.password, self.host, self.port, self.bd] = id_database

    def database_connexion_cursor(self) -> tuple[psycopg2, psycopg2]:
        """
        @return:
        """
        connection = psycopg2.connect(user=self.user,
                                      password=self.password,
                                      host=self.host,
                                      port=self.port,
                                      database=self.bd)

        cursor = connection.cursor()
        # TODO vérifier le type de cursor et de connection
        return connection, cursor

    @staticmethod
    def temps_ecouler(seconde: int) -> str:
        """
        Pour connaitre le temps écoulé
        @param seconde:
        @return:
        """
        seconds = seconde % (24 * 3600)
        hour = int(seconds // 3600)
        seconds %= 3600
        minutes = int(seconds // 60)
        seconds %= 60
        return f"{hour}h: {minutes}mn : {seconds}sec" if hour > 0 else f"{minutes}mn : {seconds}sec"

    def connection_bd(self, request: str) -> list:
        """
        Pour se connecter à la base de données
        @param request:
        @return:
        """
        connection = None
        cursor = None
        record = []

        if request:
            try:
                connection, cursor = self.database_connexion_cursor()
                cursor.execute(request)
                record = cursor.fetchall()

            except psycopg2.Error as error:
                print(f"error de connexion à la base de données PostgreSQL {error}")

            finally:
                # closing database connection.
                if connection:
                    cursor.close()
                    connection.close()

        return record

    def integration(self) -> list:
        """
        Récupération des fichiers SQL et execution des requêtes pour l'intégration des données dans la base
        """
        connection, cursor = self.database_connexion_cursor()
        connection, cursor = self.create_table_and_trigger(connection, cursor)
        cursor.close()
        connection.close()
        return []

    def create_table_and_trigger(self, connection, cursor):
        """
        @param connection:
        @param cursor:
        """
        listes_dossiers = ["creations", "triggers"]
        erreurs = []

        # Creation des tables et des triggers
        for dossier in listes_dossiers:
            for subdir, dirs, fichier in os.walk(f"{self.fichier}requetes/{dossier}/"):
                for name in fichier:
                    if name.endswith(".sql"):
                        filepath = subdir + os.sep + name
                        with open(filepath, 'r') as fd:
                            sql_file = fd.read()
                            fd.close()
                            if reponse := self.execution_requete_sql(connection, cursor, sql_file):
                                erreurs.append(reponse)

        return connection, cursor

    @staticmethod
    def execution_requete_sql(connection: psycopg2, cursor: psycopg2, request: str) -> None or psycopg2.Error:
        """
        Execution requête SQL
        @param connection:
        @param cursor:
        @param request:
        @return:
        """
        error = None
        try:
            cursor.execute(request)
            connection.commit()
        except psycopg2.Error as e:
            print(f"error : {e}")
            connection.rollback()
            error = e

        return error

    def insert_donnees_bd(self, dataset: list, fichier: str) -> bool:
        """
        Insertion des données dans la base
        @param dataset:
        @param fichier:
        @return:
        """
        error = False
        connection, cursor = self.database_connexion_cursor()

        chemin = f"{self.fichier}requetes/insertions/{fichier}.sql"
        with open(chemin, 'r') as fd:
            request = fd.read()
            fd.close()

        try:
            for recording in dataset:
                cursor.execute(request, recording)
                connection.commit()

        except (psycopg2.Error):
            connection.rollback()
            error = True

        finally:
            cursor.close()
            connection.close()

        return error

    @staticmethod
    def recup_valeur_enregistrements_ocs(table_ocs: str, champs_code_ocs: str) -> list:
        """
        Récupérer les données liées à la base de données
        @param table_ocs:
        @param champs_code_ocs:
        @return:
        """
        ocs_table = QgsProject.instance().mapLayersByName(table_ocs)[0]
        return [
            (int(feat_ocs[champs_code_ocs]), feat_ocs.geometry().asWkt())
            for feat_ocs in ocs_table.getFeatures()
            if feat_ocs.geometry() and feat_ocs.geometry() != NULL
        ]

    @staticmethod
    def recup_valeur_enregistrements_commune(table_commune: str, champs_nom: str, champs_insee: str, champs_dept: str) -> list:
        """
        Récupérer les données liées à la base de données
        @param table_commune:
        @param champs_nom:
        @param champs_insee:
        @param champs_dept:
        @return:
        """
        commune_table = QgsProject.instance().mapLayersByName(table_commune)[0]

        dataset = []
        doublon_geom = []
        for feat_commune in commune_table.getFeatures():
            if feat_commune.geometry() and feat_commune.geometry() != NULL and feat_commune.geometry() not in doublon_geom:
                dataset.append((feat_commune[champs_nom], feat_commune[champs_insee],
                                    int(feat_commune["population"]), feat_commune[champs_dept], feat_commune.geometry().asWkt()))
                doublon_geom.append(feat_commune.geometry())

        return dataset
