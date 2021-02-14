import os

from qgis.utils import iface
from qgis.core import QgsVectorLayer, QgsProject
from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox

import processing

class wps_postprocessing:
    def postprocess(self, inputs, response):
        process_identifier = os.path.splitext(os.path.basename(__file__))[0]
        try:
            csv_uri = 'file:///' + response.output['output']['filePath'] + '?delimiter=,'
            csv = QgsVectorLayer(csv_uri, "{} output".format(process_identifier), 'delimitedtext')
            QgsProject.instance().addMapLayer(csv)
            layer = None
            layerField = None
            csvField = None
            for param, widget in inputs.items():
                if isinstance(widget, QgsMapLayerComboBox):
                    layer = widget.currentLayer()
                elif isinstance(widget, QgsFieldComboBox):
                    layerField = widget.currentField()
            csvField = csv.fields()[0].name()

            if layer is not None and layerField is not None and csv is not None and csvField is not None:
                parameters = { 'DISCARD_NONMATCHING' : False, 'FIELD' : layerField, 'FIELDS_TO_COPY' : [], 'FIELD_2' : csvField, 'INPUT' : layer.source(), 'INPUT_2' : csv.source(), 'METHOD' : 1, 'OUTPUT' : 'TEMPORARY_OUTPUT', 'PREFIX' : '' }
                result = processing.runAndLoadResults('qgis:joinattributestable', parameters)
                return result
            else:
                return None
        except:
            return None
