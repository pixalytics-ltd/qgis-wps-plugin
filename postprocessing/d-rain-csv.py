from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt import QtGui
from qgis.utils import iface
from qgis.core import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.gui import *

class wps_postprocessing:
    def postprocess(self, inputs, response):
        print("POSTPROCESSING")
        print(inputs)
        print(response)
        csv_uri = 'file:///' + response.filepath + '?delimiter=,'
        print(csv_uri)
        vector = QgsVectorLayer(csv_uri, "process {} output".format('d-rain-csv'), 'delimitedtext')
        QgsProject.instance().addMapLayer(vector)
        # TODO join with layer
        # http://www.qgistutorials.com/fr/docs/performing_table_joins_pyqgis.html
