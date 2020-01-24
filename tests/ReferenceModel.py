'''Temporary openCEM model instance for runef simulations'''
from cemo.model import CreateModel, model_options
options = model_options(unslim=True, nem_emit_limit=True, nem_ret_ratio=False, nem_ret_gwh=False, region_ret_ratio=False, nem_disp_ratio=False, nem_re_disp_ratio=False) 
model = CreateModel('openCEM', options).create_model()
