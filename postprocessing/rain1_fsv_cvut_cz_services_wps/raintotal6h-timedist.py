import os

from qgis.utils import iface
from qgis.core import QgsVectorLayer, QgsProject
from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox

import processing

class WPSPostprocessing:
    def run(self, inputs, response):
        process_identifier = os.path.splitext(os.path.basename(__file__))[0]
        try:
            csv_uri = 'file:///' + response.output['output'].filepath + '?delimiter=,'
            csv = QgsVectorLayer(csv_uri, "{} output".format(process_identifier), 'delimitedtext')
            QgsProject.instance().addMapLayer(csv)
        except Exception as e:
            print(e)
            return None
        
        return 0
