# Temporary openCEM model instance for ReferenceModel.py
from cemo.model import create_model
model = create_model('openCEM',
                     unslim=True,
                     emitlimit=True,
                     nemret=False,
                     regionret=False)
