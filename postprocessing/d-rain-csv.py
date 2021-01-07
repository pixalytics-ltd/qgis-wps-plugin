from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt import QtGui
from qgis.utils import iface
from qgis.core import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.gui import *
import processing

class wps_postprocessing:
    def postprocess(self, inputs, response):
        # print("POSTPROCESSING")
        # print(inputs)
        # print(response)
        csv_uri = 'file:///' + response.filepath + '?delimiter=,'
        # print(csv_uri)
        csv = QgsVectorLayer(csv_uri, "process {} output".format('d-rain-csv'), 'delimitedtext')
        QgsProject.instance().addMapLayer(csv)
        layer = None
        layerField = None
        csvField = None
        for param, widget in inputs.items():
            if isinstance(widget, QgsMapLayerComboBox):
                # TODO check input type and export into it (GML, GeoPackage, etc.)
                layer = widget.currentLayer()
            elif isinstance(widget, QgsFieldComboBox):
                layerField = widget.currentField()
        csvField = csv.fields()[0].name()

        if layer is not None and layerField is not None and csv is not None and csvField is not None:
            parameters = { 'DISCARD_NONMATCHING' : False, 'FIELD' : layerField, 'FIELDS_TO_COPY' : [], 'FIELD_2' : csvField, 'INPUT' : layer.source(), 'INPUT_2' : csv.source(), 'METHOD' : 1, 'OUTPUT' : 'TEMPORARY_OUTPUT', 'PREFIX' : '' }
            result = processing.runAndLoadResults('qgis:joinattributestable', parameters)

