'''Temporary openCEM model instance for runef simulations'''
from cemo.model import create_model
model = create_model('openCEM',
                     unslim=True,
                     emitlimit=True,
                     nem_ret_ratio=False,
                     nem_ret_gwh=False,
                     region_ret_ratio=False,
                     nem_disp_ratio=False,
                     no_disp_strategic_reserve=True)
