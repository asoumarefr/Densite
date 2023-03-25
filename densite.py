"""
/***************************************************************************
DensiteOCS    A QGIS plugin
Un chargé de mission souhaite connaître la surface et le pourcentage de
différentes classes d'occupation des sols sur  différents types de
territoire de son département des Hautes-Pyrénées (65).
Pour cela on va utiliser une base de données fournie par le CESBIO sur le
dernier millésime disponible et on synthétisera l'information sur 7 classes
d'OCS.
L'utilisateur doit pouvoir indiquer un territoire (à savoir une commune ou un
EPCI) sur lequel il veut obtenir ces informations agrégées.
"""

import re
import time
from pathlib import Path
import os.path


from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import QAction, QTableWidgetItem, QFileDialog
from qgis.core import QgsProject, QgsVectorLayer, QgsMapLayer, QgsWkbTypes


from .resources import *
from .densite_dialog import DensiteOCSDialog
from .statistiques import Statistiques
from . import Initiatlisation
from .aboutdialog import DensiteAboutDialog

"""
pyrcc5 resources.qrc -o resources.py
pyuic5 c3a_dialog_base.ui -o ../c3a_dialog_base.py
pyuic5 densite_dialog_base.ui -o ../densite_dialog_base.py

"""


class DensiteOCS:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
        which provides the hook by which you can manipulate the QGIS
        application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n',
                                   f'DensiteOCS_{locale}.qm')

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Fonction pour déplacer l'icone de plugin
        self.toolbar = self.iface.addToolBar("Densité d'OCS")
        # self.toolbar.setObjectName(f"Densité d'OCS")

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr("Densité d'OCS")

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.dlg = DensiteOCSDialog()
        self.init = Initiatlisation()
        # self.stat = IntegrationBd()
        self.stat = Statistiques()
        self.dlg.helpButton.clicked.connect(self.aide_apropos)

        self.dlg.boutonCreationTb.setStyleSheet("background-color: #7fcdbb")
        self.dlg.boutonIntegrationBd.setStyleSheet("background-color: #addd8e")
        self.dlg.boutonIntegrationCommune.setStyleSheet("background-color: #FFA500")

        # Sélection du repertoire où sera stocké les fichiers
        self.dlg.boutonCheminImport.clicked.connect(self.choix_du_dossier_import)

        # Action associée au bouton secondal d'importation des couches dans QGIS
        self.dlg.boutonImport.clicked.connect(self.importation_donnees_dans_qgis)

        # Création du schéma et des tables
        self.dlg.boutonCreationTb.clicked.connect(self.creation_bd)

        # Intégration des données dans la base de données
        self.dlg.boutonIntegrationBd.clicked.connect(self.insertion_donnees_ocs)

        # Rafraîchir l'interface utilisateur de QGIS (les tables)
        self.dlg.RafraichirUi.clicked.connect(self.rafraichisement)

        self.dlg.comboBox_tb_OCS.currentTextChanged.connect(self.champs_colonne_code12)
        self.dlg.comboBox_tb_commune.currentTextChanged.connect(self.champs_colonne_comm)

        self.dlg.boutonIntegrationCommune.clicked.connect(self.insertion_donnees_communes)

        ####################### STAT ##########################
        self.dlg.tableWidget_ChoixFinal_Stat.setColumnWidth(0, 217)

        self.dlg.comboBox_Stat.activated.connect(self.integration_barre_recherche_stat)
        self.dlg.rafraichirUi_ToutSupprimer.clicked.connect(self.supprimer_donnees_communes)
        self.dlg.rafraichirUi_barre_recherche.clicked.connect(self.rafraichir_liste_communes)

        self.dlg.exportStat.clicked.connect(self.generer_statistiques)

    # noinspection PyMethodMayBeStatic
    def tr(self, message) -> None:
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DensiteOCS', message)

    def add_action(self, icon_path: str, text: str, callback, enabled_flag: bool = True,
                   add_to_menu: bool = True, add_to_toolbar: bool = True, status_tip: str = None, whats_this=None,
                   parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            # Fonction pour déplacer l'icone de plugin
            # self.iface.addToolBarIcon(action)
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # Cette image a été téléchargée ici :
        # https://thenounproject.com/icon/nature-2404733/
        icon_path = ':/plugins/Densite/icon.png'
        self.add_action(
            icon_path,
            text=self.tr("Densité d'occupation des sols"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr("Densité d'OCS"), action)
            self.iface.removeToolBarIcon(action)

        # Supression de l'icone de plugin
        del self.toolbar

    def run(self) -> None:
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        self.dlg.exec_()

    def aide_apropos(self) -> None:
        """Apropos pour afficher des détails concernant cet outil"""
        # set the version
        self.about_dlg = DensiteAboutDialog()

        # add version to the label
        self.about_dlg.uiAbout.version_n.setText(self.init.version())

        self.about_dlg.uiAbout.autors_name.setText(self.init.author_name())

        # show dialog
        self.about_dlg.show()

    def rafraichisement(self) -> None:
        """Fonction pour rafraîchir l'interface QGIS notamment les couches"""
        self.dlg.textBrowser.clear()
        self.couche_combobox_ocs()
        self.couche_combobox_communes()
        self.dlg.progressBar.setValue(0)

    def couche_combobox_ocs(self) -> None:
        """ fonction qui permet de recupérer et d'afficher les noms des TABLES, de type polygones"""
        # On récupère ici la liste des tables présentes dans QGIS.

        layers = list(QgsProject.instance().mapLayers().values())
        layer_list = ['']
        self.dlg.comboBox_tb_OCS.clear()

        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                try:
                    if QgsWkbTypes.geometryType(layer.wkbType()) in (2, 5):
                        layer_list.append(layer.name())

                except Exception as e:
                    print(f"Erreur comboboxCmd : {e}")
                    continue

        # Si absence de couche dans QGIS, on vide les combobox
        if len(layer_list) == 1:
            self.dlg.comboBox_tb_OCS.clear()
            self.alerte_infos("Votre projet ne contient aucun shape de type Polygone")

        else:
            # On insère les données tables dans le Combobox
            layer_list.sort()
            self.dlg.comboBox_tb_OCS.addItems(layer_list)

            # On définit la valeur par défaut de la couche s'il y a un table du nom 'etude_cap_ft'
            for valeur in layer_list:
                regexp = re.compile(r'clc')
                if regexp.search(valeur.lower()):
                    self.dlg.comboBox_tb_OCS.setCurrentIndex(layer_list.index(valeur))
                    break

            self.dlg.textBrowser.clear()

    def champs_colonne_code12(self) -> None:
        """ fonction qui permet de recupérer et d'afficher les noms des champs associée à la table sélectionnée"""
        # Création d'une variable fetcable qui parcours la table t_cable
        layers = list(QgsProject.instance().mapLayers().values())

        champs_list = ['']
        self.dlg.comboBoxChampsCode_12.clear()

        for layer in layers:
            if layer.name() == self.dlg.comboBox_tb_OCS.currentText():
                champs_list.extend(str(champs.name()) for champs in layer.fields())

        if len(champs_list) == 1:
            self.dlg.comboBoxChampsCode_12.clear()

        else:
            # On insère des données colonnes dans le Combobox
            self.dlg.comboBoxChampsCode_12.addItems(champs_list)

            # On définit la valeur par défaut de la couche s'il y a un champs du nom de 'code'
            regexp = re.compile(r'code*')
            for valeur in champs_list:
                if regexp.search(valeur.lower()):
                    self.dlg.comboBoxChampsCode_12.setCurrentIndex(champs_list.index(valeur))
                    break

    def couche_combobox_communes(self) -> None:
        """ fonction qui permet de recupérer et d'afficher les noms des TABLES, de type polygones"""
        # On récupère ici la liste des tables présentes dans QGIS.

        layers = list(QgsProject.instance().mapLayers().values())
        layer_list = ['']
        self.dlg.comboBox_tb_commune.clear()

        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                try:
                    if QgsWkbTypes.geometryType(layer.wkbType()) in (2, 5):
                        layer_list.append(layer.name())

                except Exception as e:
                    print(f"Erreur comboboxCmd : {e}")
                    continue

        # Si absence de couche dans QGIS, on vide les combobox
        if len(layer_list) == 1:
            self.dlg.comboBox_tb_commune.clear()
            self.alerte_infos("Votre projet ne contient aucun shape de type Polygone")

        else:
            # On insère les données tables dans le Combobox
            layer_list.sort()
            self.dlg.comboBox_tb_commune.addItems(layer_list)

            # On définit la valeur par défaut de la couche s'il y a un table du nom 'etude_cap_ft'
            for valeur in layer_list:
                regexp = re.compile(r'commune')
                if regexp.search(valeur.lower()):
                    self.dlg.comboBox_tb_commune.setCurrentIndex(layer_list.index(valeur))
                    break

            self.dlg.textBrowser.clear()

    def champs_colonne_comm(self) -> None:
        """ fonction qui permet de recupérer et d'afficher les noms des champs associée à la table sélectionnée"""
        # Création d'une variable fetcable qui parcours la table t_cable
        layers = list(QgsProject.instance().mapLayers().values())

        champs_list = ['']
        self.dlg.comboBoxChampsNom.clear()
        self.dlg.comboBoxChampsInsee.clear()
        self.dlg.comboBoxChampsCodeDept.clear()

        for layer in layers:
            if layer.name() == self.dlg.comboBox_tb_commune.currentText():
                # champs_list.append(str(champs.name()) for champs in layer.fields())
                champs_list.extend(str(champs.name()) for champs in layer.fields())
        if len(champs_list) == 1:
            self.dlg.comboBoxChampsNom.clear()

        else:
            self._extracted_from_champs_colonne_comm_20(champs_list)

    # TODO Rename this here and in `champs_colonne_comm`
    def _extracted_from_champs_colonne_comm_20(self, champs_list) -> None:
        # On insère des données colonnes dans le Combobox
        self.dlg.comboBoxChampsNom.addItems(champs_list)
        self.dlg.comboBoxChampsInsee.addItems(champs_list)
        self.dlg.comboBoxChampsCodeDept.addItems(champs_list)

        # On définit la valeur par défaut de la couche s'il y a un champs du nom de 'etude'
        regexp_nom = re.compile(r'nom_com*')
        regexp_insee = re.compile(r'insee*')
        regexp_dept = re.compile(r'code_dept*')

        for valeur in champs_list:
            if regexp_nom.search(valeur.lower()):
                self.dlg.comboBoxChampsNom.setCurrentIndex(champs_list.index(valeur))

            elif regexp_insee.search(valeur.lower()):
                self.dlg.comboBoxChampsInsee.setCurrentIndex(champs_list.index(valeur))

            elif regexp_dept.search(valeur.lower()):
                self.dlg.comboBoxChampsCodeDept.setCurrentIndex(champs_list.index(valeur))

    def alerte_infos(self, info: str, efface=False, couleur="red") -> None:
        """Fonction pour afficher des messages d'alerte dans la barre d'info"""
        if efface:
            self.dlg.textBrowser.clear()
        self.dlg.textBrowser.setTextColor(QColor(couleur))
        self.dlg.textBrowser.append(f"{info}\n")

    def choix_du_dossier_import(self) -> None:
        """Fonction pour choisir le repertoire à partir duquel je souhaite IMPORTER des données"""
        dirname = QFileDialog.getExistingDirectory(self.dlg,
                                                   "Sélectionner votre repertoire d'importation des fichiers", "")

        # chemin = self.dlg.lienCheminImport.text()
        # On change le chemin accès par defaut
        if os.access(dirname, os.W_OK) and os.path.isdir(dirname):
            self.dlg.lienCheminImport.setText(dirname)
            self.dlg.boutonImport.setEnabled(True)
            os.chdir(dirname)

        else:
            print(f"Le chemin indiqué est incorrect : {dirname}")
            self.dlg.boutonImport.setEnabled(False)

    def importation_donnees_dans_qgis(self) -> None:
        """Importer des données shapes"""
        # Liste des données à importer
        repertoire = self.dlg.lienCheminImport.text()

        for subdir, dirs, files in os.walk(repertoire):
            for name in files:
                if name.endswith('.shp'):
                    filepath = subdir + os.sep + name

                    # nom = os.path.basename(name)
                    nom = Path(filepath).stem
                    # print(f"nom : {nom}")
                    couche_shp = QgsVectorLayer(filepath, nom, "ogr")
                    crs = couche_shp.crs()
                    crs.createFromId(2154)
                    couche_shp.setCrs(crs)

                    QgsProject.instance().addMapLayer(couche_shp, True)

        self.dlg.tabWidget.setCurrentWidget(self.dlg.tab_Suppr)

    def creation_bd(self) -> None:
        """Creation des schémas et des tables"""
        if reponse := self.stat.integration():
            self.alerte_infos("Une ou plusieurs erreurs ont été trouvées :")
            for erreur in reponse:
                self.alerte_infos(f"{erreur}")
        else:
            self.alerte_infos("Les requetes de création ont bien été éxecuées", couleur="green")

    def insertion_donnees_ocs(self) -> None:
        """Execution des réquetes d'insertion des données dans bd"""
        self.dlg.progressBar.setValue(0)
        start_time = time.time()  # Horaire du début d'execution du programme

        tb_ocs = self.dlg.comboBox_tb_OCS.currentText()
        champs_code_ocs = self.dlg.comboBoxChampsCode_12.currentText()
        self.dlg.progressBar.setValue(50)

        data_global = self.stat.recup_valeur_enregistrements_ocs(tb_ocs, champs_code_ocs)

        self.stat.insert_donnees_bd(data_global, "01_insert_ocs")

        etape = f"Fin de l'exécution du programme en {self.stat.temps_ecouler(time.time() - start_time)}"
        self.alerte_infos(etape, False, "grey")

        self.dlg.progressBar.setValue(100)

    def insertion_donnees_communes(self) -> None:
        """Execution des réquetes d'insertion des données dans bd"""
        self.dlg.progressBar.setValue(0)
        start_time = time.time()  # Horaire du début d'execution du programme

        commune = self.dlg.comboBox_tb_commune.currentText()
        champs_nom = self.dlg.comboBoxChampsNom.currentText()
        champs_insee = self.dlg.comboBoxChampsInsee.currentText()
        champs_dept = self.dlg.comboBoxChampsCodeDept.currentText()

        data_global = self.stat.recup_valeur_enregistrements_commune(commune, champs_nom, champs_insee, champs_dept)
        self.dlg.progressBar.setValue(50)

        self.stat.insert_donnees_bd(data_global, "02_insert_commune")

        etape = f"Fin de l'exécution du programme en {self.stat.temps_ecouler(time.time() - start_time)}"
        self.alerte_infos(etape, False, "grey")
        self.dlg.progressBar.setValue(100)

    ############################################# STAT ###############################################
    def integration_barre_recherche_stat(self) -> None:
        """Fonction qui permet d'ajouter la séléction des communes depuis la barre de recherche"""
        test_saisie = self.dlg.comboBox_Stat.currentText()

        valeur_commune = [self.dlg.tableWidget_ChoixFinal_Stat.item(a, 0).text() for a in
                          range(self.dlg.tableWidget_ChoixFinal_Stat.rowCount())]

        if test_saisie in self.liste_des_communes and test_saisie not in valeur_commune:
            ligne = self.dlg.tableWidget_ChoixFinal_Stat.rowCount()
            self.dlg.tableWidget_ChoixFinal_Stat.insertRow(ligne)
            self.dlg.tableWidget_ChoixFinal_Stat.setItem(ligne, 0, QTableWidgetItem(test_saisie))
            valeur_commune.append(test_saisie)

    def rafraichir_liste_communes(self) -> None:
        """Rafraichir l'interface"""

        self.dlg.comboBox_Stat.clear()
        if self.stat.verification_identifiant_connexion_bd():

            message = f"""Vous n'avez pas accès à l'internet \nOU" 
                       \n\nVos identifiants de connexion sont incorrects. \nMerci de modifier le fichier de connexion
                       ci-dessous le lien pour insérer vos propres identifiants :\n
                       C:/Users/NomDuPc/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/Densite/
                       connexion/id_mdp.json"""
            self.dlg.textBrowser.setTextColor(QColor("red"))
            self.dlg.textBrowser.append(f"{message}\n")
            self.dlg.progressBar.setValue(0)

        else:
            self._extracted_from_rafraichir_liste_communes_18()

    # TODO Rename this here and in `rafraichir_liste_communes`
    def _extracted_from_rafraichir_liste_communes_18(self) -> None:
        # On réunitialise la barre de recherche
        self.dlg.comboBox_Stat.addItems([''])

        self.dlg.textBrowser.clear()
        self.dlg.progressBar.setValue(0)

        ################################### COLLECTE ##########################################
        liste_communes = self.stat.connection_bd("""SELECT  nom
                                                    FROM   densite_65.commune 
                                                    GROUP BY nom;""")

        self.liste_des_communes = [nom[0] for nom in liste_communes]

        # Ajout de la liste des communes dans la barre de recherche
        self.barre_de_recherche((nom[0] for nom in liste_communes))

    def barre_de_recherche(self, liste_barre: list) -> None:
        """Fonction pour ajouter des valeurs dans la barre de recherche du combobox"""
        self.dlg.comboBox_Stat.addItems(liste_barre)

    def supprimer_donnees_communes(self) -> None:
        """Pour supprimer des valeurs séléctionnées dans le widget."""

        if self.dlg.tableWidget_ChoixFinal_Stat.rowCount() > 0:
            for _ in range(self.dlg.tableWidget_ChoixFinal_Stat.rowCount()):
                self.dlg.tableWidget_ChoixFinal_Stat.removeRow(0)

    def generer_statistiques(self) -> None:
        """Génération des statistiques"""
        valeur_filtre_final = [self.dlg.tableWidget_ChoixFinal_Stat.item(row, 0).text() for row in
                               range(self.dlg.tableWidget_ChoixFinal_Stat.rowCount())]

        self.stat.generateur(valeur_filtre_final)
