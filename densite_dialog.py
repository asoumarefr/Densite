# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DensiteOCSDialog
                                 A QGIS plugin
 Un chargé de mission souhaite connaître la surface et le pourcentage de différentes classes d'occupation des sols sur différents types de territoire de son département des Hautes-Pyrénées (65).
Pour cela on va utiliser une base de données fournie par le CESBIO sur le dernier millésime disponible et on synthétisera l'information sur 7 classes d'OCS.
L'utilisateur doit pouvoir indiquer un territoire (à savoir une commune ou un EPCI) sur lequel il veut obtenir ces informations agrégées.

 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-12-29
        git sha              : $Format:%H$
        copyright            : (C) 2022 by SOUMARE Abdoulayi
        email                : abdoulayisoumare@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'interfaces/densite_dialog_base.ui'))


class DensiteOCSDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(DensiteOCSDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
