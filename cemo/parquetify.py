"""Save Simulatin data as a series of parquet files"""
import pandas as pd
from pathlib import Path

# Variable map used for postprocessing and analysis
MAP = {
    'complex': {
      'disp': {
        'vars': ['gen_disp', 'hyb_disp', 'stor_disp'],
        'cols': ['zone', 'tech', 'time', 'disp'],
        'part': ['zone', 'tech'],
        'set': 'vars',
      },
      'disp_com': {
        'vars': ['gen_disp_com'],
        'cols': ['zone', 'tech', 'time', 'disp_com'],
        'part': ['zone', 'tech'],
        'set': 'vars',
      },
      'disp_com_p': {
        'vars': ['gen_disp_com_p'],
        'cols': ['zone', 'tech', 'time', 'disp_com_p'],
        'part': ['zone', 'tech'],
        'set': 'vars',
      },
      'charge': {
        'vars': ['hyb_charge', 'stor_charge'],
        'cols': ['zone', 'tech', 'time', 'charge'],
        'part': ['zone', 'tech'],
        'set': 'vars',
      },
      'region_net_demand': {
        'vars': ['region_net_demand'],
        'cols': ['region', 'time', 'region_net_demand'],
        'part': ['region'],
        'set': 'params',
      },
      'cap_op': {
        'vars': ['gen_cap_op', 'hyb_cap_op', 'stor_cap_op'],
        'cols': ['zone', 'tech', 'cap_op'],
        'part': ['zone'],
        'set': 'vars',
        'scale': 1e-3,
      },
      'cap_new': {
        'vars': ['gen_cap_new', 'hyb_cap_new', 'stor_cap_new'],
        'cols': ['zone', 'tech', 'cap_new'],
        'part': ['zone'],
        'set': 'vars',
        'scale': 1e-3,
      },
      'cap_ret': {
        'vars': ['gen_cap_ret'],
        'cols': ['zone', 'tech', 'cap_ret'],
        'part': ['zone'],
        'set': 'vars',
        'scale': 1e-3,
      },
      'cap_exo': {
        'vars': ['gen_cap_exo', 'hyb_cap_exo', 'stor_cap_exo'],
        'cols': ['zone', 'tech', 'cap_exo'],
        'part': ['zone'],
        'set': 'params',
      },
      'cap_ret_exo': {
        'vars': ['ret_gen_cap_exo'],
        'cols': ['zone', 'tech', 'cap_ret_exo'],
        'part': ['zone'],
        'set': 'params',
      },

      'intercon_disp': {
        'vars': ['intercon_disp'],
        'cols': ['zone_source', 'zone_dest', 'time', 'intercon_disp'],
        'part': ['zone_source', 'zone_dest'],
        'set': 'vars',
      },
      'intercon_cap_op': {
        'vars': ['intercon_cap_op'],
        'cols': ['zone_source', 'zone_dest', 'intercon_cap_op'],
        'part': ['zone_source', 'zone_dest'],
        'set': 'vars',
        'scale': 1e-3,
      },
      'intercon_cap_new': {
        'vars': ['intercon_cap_new'],
        'cols': ['zone_source', 'zone_dest', 'intercon_cap_new'],
        'part': ['zone_source', 'zone_dest'],
        'set': 'vars',
        'scale': 1e-3,
      },
      'intercon_cap_exo': {
        'vars': ['intercon_cap_exo'],
        'cols': ['zone_source', 'zone_dest', 'intercon_cap_exo'],
        'part': ['zone_source', 'zone_dest'],
        'set': 'params',
      },
      'trace': {
        'vars': ['gen_cap_factor', 'hyb_cap_factor'],
        'cols': ['zone', 'tech', 'time', 'trace'],
        'part': ['zone', 'tech'],
        'set': 'params',
      },
      'cost_build': {
        'vars': ['cost_gen_build', 'cost_stor_build', 'cost_hyb_build'],
        'cols': ['zone', 'tech', 'cost_build'],
        'part': ['zone', 'tech'],
        'set': 'params',
      },
      'cost_intercon_build': {
       'vars': ['cost_intercon_build'],
       'cols': ['zone_source', 'zone_dest', 'cost_intercon_build'],
       'part': ['zone_source'],
       'set': 'params',
      },
      'fuel_heat_rate': {
        'vars': ['fuel_heat_rate'],
        'cols': ['zone', 'tech', 'fuel_heat_rate'],
        'part': ['zone'],
        'set': 'params',
      },
      'cost_fuel': {
        'vars': ['cost_fuel'],
        'cols': ['zone', 'tech', 'cost_fuel'],
        'part': ['zone'],
        'set': 'params',
      },
      'unserved': {
        'vars': ['unserved'],
        'cols': ['zone', 'time', 'unserved'],
        'part': ['zone'],
        'set': 'vars'
      }
    },
    'duals': {
      'srmc': {
        'vars': ['ldbal'],
        'cols': ['zone', 'time', 'srmc'],
        'part': ['zone'],
        'set': 'duals',
        'scale': 1e-1,
         },
    },
    'scalar': {
      'opex_fom': {
        'vars': ['cost_gen_fom', 'cost_stor_fom', 'cost_hyb_fom'],
        'cols': ['tech', 'opex_fom'],
        'set': 'params',
        'part': ['tech'],
      },
      'opex_vom': {
        'vars': ['cost_gen_vom', 'cost_stor_vom', 'cost_hyb_vom'],
        'cols': ['tech', 'opex_vom'],
        'set': 'params',
        'part': ['tech'],
      },
      'cost_cap_carry_forward': {
         'vars': ['cost_cap_carry_forward'],
         'cols': ['zone', 'cost_cap_carry_forward'],
         'part': ['zone'],
         'set': 'params',
       },
      'fuel_emit_rate': {
        'vars': ['fuel_emit_rate'],
        'cols': ['tech', 'fuel_emit_rate'],
        'set': 'params',
        'part': ['tech'],
      },
      'fixed_charge_rate': {
        'vars': ['fixed_charge_rate'],
        'cols': ['tech', 'fixed_charge_rate'],
        'set': 'params',
        'part': ['tech'],
      },
      'cost_retire': {
        'vars': ['cost_retire'],
        'cols': ['tech', 'cost_retire'],
        'set': 'params',
        'part': ['tech'],
      },
      'gen_com_mincap': {
        'vars': ['gen_com_mincap'],
        'cols': ['tech', 'gen_com_mincap'],
        'set': 'params',
        'part': ['tech'],
      },
      'gen_com_effrate': {
        'vars': ['gen_com_effrate'],
        'cols': ['tech', 'gen_com_effrate'],
        'set': 'params',
        'part': ['tech'],
      },
      'gen_com_penalty': {
        'vars': ['gen_com_penalty'],
        'cols': ['tech', 'gen_com_penalty'],
        'set': 'params',
        'part': ['tech'],
      },
    },
    'unindexed': {
      'misc': {
        'vars': ['cost_unserved', 'cost_emit', 'cost_trans', 'intercon_fixed_charge_rate',
                 'nem_emit_limit', 'nem_ret_ratio', 'nem_ret_gwh', 'year_correction_factor'],
        'set': 'params',
      }
    }
}


def pyomo_to_parquet_dual(instance, var, columns):
    """Obtain multi indexed variable values from dual as a list of tuples from instance and return pandas dataframe"""
    dual = getattr(instance, 'dual')
    names = getattr(instance, var)
    data = [i+(dual[names[i]],) for i in names]
    df = pd.DataFrame(data=data, columns=columns)
    return df


def pyomo_to_parquet_complex(instance, var, columns):
    """Obtain multi indexed variable values as a list of tuples from instance and return pandas dataframe"""
    obj = getattr(instance, var)
    list_out = obj.extract_values().items()
    data = [i[0]+(i[1],) for i in list_out]
    df = pd.DataFrame(data=data, columns=columns)
    return df


def pyomo_to_parquet_scalar(instance, var, columns):
    """Obtain scalar indexed variable as a list of tuples and return pandas dataframe"""
    obj = getattr(instance, var)
    data = obj.extract_values().items()
    df = pd.DataFrame(data=data, columns=columns)
    return df


def convert_duals(instance, folder, year):
    """Scan MAP for dual variables in instance and save to 'folder' under 'year'"""
    for key in MAP['duals']:
        for var in MAP['duals'][key]['vars']:
            try:
                parq = pyomo_to_parquet_dual(instance, var, MAP['duals'][key]['cols'])
                parq[key] = parq[key]*MAP['duals'][key].get('scale', 1)
                parq = parq.astype({key: float})
                p = Path(folder) / str(year) / key
                parq.to_parquet(p,
                                partition_cols=MAP['duals'][key]['part'],
                                compression='snappy')
            except Exception as ex:
                print("    %s NOT PROCESSED, reason: %s" % (var, ex))


def convert_complex(instance, folder, year):
    """Scan MAP for complex variables in instance and save to 'folder' under 'year'"""
    print(year)
    for key in MAP['complex']:
        for var in MAP['complex'][key]['vars']:
            if getattr(instance, var, None) is not None:
                parq = pyomo_to_parquet_complex(instance, var, MAP['complex'][key]['cols'])
                parq[key] = parq[key]*MAP['complex'][key].get('scale', 1)
                parq = parq.astype({key: float})
                p = Path(folder) / str(year) / key
                parq.to_parquet(p,
                                partition_cols=MAP['complex'][key]['part'],
                                compression='snappy')
            else:
                print("    %s NOT PROCESSED" % var)


def convert_scalar(instance, folder, year):
    """Scan MAP for scalar indexed variables in instance and save to 'folder' under 'year'"""
    for key in MAP['scalar']:
        for svar in MAP['scalar'][key]['vars']:
            if getattr(instance, svar, None) is not None:
                parq = pyomo_to_parquet_scalar(instance, svar,
                                               columns=MAP['scalar'][key]['cols'])
                parq = parq.astype({key: float})
                p = Path(folder) / str(year) / key
                parq.to_parquet(p,
                                partition_cols=MAP['scalar'][key]['part'],
                                compression='snappy')
            else:
                print("    %s NOT PROCESSED" % svar)


def convert_unindexed(instance, folder, year):
    """Scan MAP for unindexed variables in instance and save to 'folder' under 'year'"""
    for key in MAP['unindexed']:
        d = {}
        for nvar in MAP['unindexed'][key]['vars']:
            if getattr(instance, nvar, None) is not None:
                d.update({nvar: [getattr(instance, nvar).extract_values()[None]]})
            else:
                d.update({nvar: 0})
        parq = pd.DataFrame(data=d)
        p = Path(folder) / str(year) / (key+'.parquet')
        parq.to_parquet(p,
                        compression='snappy')


def parquetify(instance, folder, year):
    """Scan instance for data and save in parquet for given year"""
    convert_complex(instance, folder, year)
    convert_duals(instance, folder, year)
    convert_scalar(instance, folder, year)
    convert_unindexed(instance, folder, year)
