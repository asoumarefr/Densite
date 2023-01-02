from qgis.PyQt import QtWidgets
from .densite_apropos import Ui_AboutDialog


# create dialog for about/help window
class DensiteAboutDialog(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.uiAbout = Ui_AboutDialog()
        self.uiAbout.setupUi(self)
