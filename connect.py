from qgis.PyQt.QtCore import QThread, pyqtSignal
import tempfile, os

owslib_exists = True
try:
    from owslib.wps import WebProcessingService
    from owslib.wps import ComplexDataInput
    import owslib.wps
    from owslib.util import getTypedValue
    val = getTypedValue('integer', None)
except:
    owslib_exists = False

class ResponseOutput:
    def __init__(self, filepath, minetype):
        self.filepath = filepath
        self.minetype = minetype

class Response():
    status = 200
    data = []
    output = {}

# TODO create superclass for these classes
class GetProcesses(QThread):
    statusChanged = pyqtSignal(object)
    url = None
    timeout = 5

    def setUrl(self, url):
        self.url = url

    def setTimeout(self, timeout):
        self.timeout = timeout

    def run(self):
        responseToReturn = Response()
        try:
            wps = WebProcessingService(self.url)
            wps.getcapabilities()
            # processes = [x.identifier for x in wps.processes]
            responseToReturn.status = 200
            responseToReturn.data = wps.processes
        except:
            responseToReturn.status = 500
        self.statusChanged.emit(responseToReturn)

class GetProcess(QThread):
    statusChanged = pyqtSignal(object)
    url = None
    timeout = 5
    identifier = ''

    def setUrl(self, url):
        self.url = url

    def setTimeout(self, timeout):
        self.timeout = timeout

    def setIdentifier(self, identifier):
        self.identifier = identifier

    def run(self):
        responseToReturn = Response()
        if self.identifier != "":
            try:
                wps = WebProcessingService(self.url)
                process = wps.describeprocess(self.identifier)
                responseToReturn.status = 200
                responseToReturn.data = process
            except:
                responseToReturn.status = 500
        else:
            responseToReturn.status = 500
        self.statusChanged.emit(responseToReturn)

class ExecuteProcess(QThread):
    statusChanged = pyqtSignal(object)
    url = None
    timeout = 60
    identifier = ''
    inputs = []

    def setUrl(self, url):
        self.url = url

    def setTimeout(self, timeout):
        self.timeout = timeout

    def setIdentifier(self, identifier):
        self.identifier = identifier

    def setInputs(self, inputs):
        self.inputs = inputs

    def getFilePath(self, mimeType):
        temp_name = next(tempfile._get_candidate_names())
        defult_tmp_dir = tempfile._get_default_tempdir()
        suffix = 'zip'
        if mimeType == 'application/csv':
            suffix = 'csv'
        return os.path.join(defult_tmp_dir, temp_name + "." + suffix)

    def run(self):
        responseToReturn = Response()
        if self.identifier != "" and len(self.inputs) > 0:
            try:
                wps = WebProcessingService(self.url)
                execution = wps.execute(self.identifier, self.inputs, output=[])
                owslib.wps.monitorExecution(execution)
                for output in execution.processOutputs:
                    filePath = self.getFilePath(output.mimeType)
                    responseToReturn.output[output.identifier] = ResponseOutput(
                        filePath, output.mimeType
                    )
                    execution.getOutput(filePath, output.identifier)
                responseToReturn.status = 200
            except Exception as e:
                responseToReturn.status = 500
                responseToReturn.data = str(e)
        else:
            responseToReturn.status = 500
        self.statusChanged.emit(responseToReturn)
