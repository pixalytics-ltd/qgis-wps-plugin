class CheckOwsLib():
    @staticmethod
    def isValid():
      owslib_exists = True
      try:
          import owslib
          version = owslib.__version__
          major = int(version.split('.')[0])
          minor = int(version.split('.')[1])
          if major == 0 and minor < 22:
              owslib_exists = False
          from owslib.wps import WebProcessingService
          from owslib.wps import ComplexDataInput
          from owslib.util import getTypedValue
          val = getTypedValue('integer', None)
      except:
          owslib_exists = False
      return owslib_exists
