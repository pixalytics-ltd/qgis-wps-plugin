import os

from qgis.utils import iface
from qgis.core import QgsVectorLayer, QgsProject
from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox

import processing

class WPSPostprocessing:
    def run(self, inputs, response):
        process_identifier = os.path.splitext(os.path.basename(__file__))[0]
        try:
            for identifier, output in response.output.items():
                csv_uri = 'file:///' + output.filepath + '?delimiter=,'
                csv = QgsVectorLayer(csv_uri, "{} {}".format(process_identifier, identifier), 'delimitedtext')
                QgsProject.instance().addMapLayer(csv)

                if identifier == 'output':
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
                        parameters = { 'DISCARD_NONMATCHING' : False, 'FIELD' : layerField,
                                       'FIELDS_TO_COPY' : [], 'FIELD_2' : csvField,
                                       'INPUT' : layer.source(), 'INPUT_2' : csv.source(), 'METHOD' : 1,
                                       'OUTPUT' : 'TEMPORARY_OUTPUT', 'PREFIX' : '' }
                        print(processing.runAndLoadResults('qgis:joinattributestable', parameters))
        except Exception as e:
            print(e)
            return None

        return 0
