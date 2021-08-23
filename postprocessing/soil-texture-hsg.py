import os

from qgis.core import QgsRasterLayer, QgsProject

import processing

class wps_postprocessing:
    def postprocess(self, inputs, response):
        process_identifier = os.path.splitext(os.path.basename(__file__))[0]
        try:
            for name in inputs["layers"].text().split(','):
                uri = '/vsizip/' + response.output['output'].filepath + '/' + name + '.tif'
                print(uri)
                raster = QgsRasterLayer(uri, "{} {}".format(process_identifier, name))
                QgsProject.instance().addMapLayer(raster)
        except Exception as e:
            print(e)
            return None

        return 0
