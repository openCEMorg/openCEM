"""Multi year simulation module"""
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "GPLv3"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"

import configparser
import datetime
import json
from pathlib import Path
import tempfile
import re
import ast
import shutil

import pandas as pd
from pyomo.opt import SolverFactory

import cemo.const
from cemo.cluster import ClusterRun, InstanceCluster
from cemo.jsonify import json_carry_forward_cap, jsonify
from cemo.parquetify import parquetify
from cemo.model import CreateModel, model_options
from cemo.utils import printstats
from cemo.summary import Summary

from shutil import copyfileobj


def parse_solver_options(option_string):
    """Turn solver options in string format into JSON"""
    # parse options in the form 'key=value key=value' into a [(key, value)]
    r = re.compile(r'\b(\w[\w_.]*)\b\s*=\s*\b(\w[\w\-_.]*)\b')
    dispatch_opts = r.findall(option_string)
    option_dict = dict()
    for key, val in dispatch_opts:
        try:
            value = ast.literal_eval(val)
        except ValueError:
            value = val

        option_dict[key] = value

    return option_dict


def make_file_path(pathstring, cfgroot):
    '''Return a full path for a file reference in cfg file, whether relative or absolute'''
    if Path(pathstring).is_absolute():
        return Path(pathstring)
    return cfgroot.parent / pathstring


def sql_tech_pairs(techset):
    """Format zone,tech pairs as a set for MySQL query statement"""
    out = []
    for i in techset.keys():
        for j in techset[i]:
            out.append((i, j))
    if not out:
        out.append((99, 99))  # return non empty set to preserve query syntax if list is empty
    return "(" + ", ".join(map(str, out)) + ")"


def athena_tech_pairs(techset):
    """Format zone,tech pairs as a set for AthenaDB SQL query statement"""
    out = []
    for i in techset.keys():
        for j in techset[i]:
            out.append((i, j))
    if not out:
        out.append((99, 99))  # return non empty set to preserve query syntax if list is empty
    return "(" + ", ".join(["ROW(CAST(%d as INTEGER), CAST(%d as INTEGER))" % x for x in out]) + ")"


def gen_timerange(year, test=False, athena=False):
    """Generate a time range for mysql and athena queries"""
    date1 = datetime.datetime(year - 1, 7, 1, 0, 0, 0)
    strd1 = "'" + str(date1) + "'"
    date2 = datetime.datetime(year, 6, 30, 23, 0, 0)
    if test:
        date2 = datetime.datetime(year - 1, 7, 7, 23, 0, 0)
    strd2 = "'" + str(date2) + "'"
    if athena:
        return "BETWEEN " + "CAST(" + strd1 + " AS timestamp)" + " AND " + "CAST(" + strd2 + " AS timestamp)"
    return "BETWEEN " + strd1 + " AND " + strd2


def sql_list(list):
    """Format set lists as a comma separated set for SQL query statement"""
    if not list:
        list.append(99)  # return non empty set to preserve query syntax if list is empty
    return ", ".join(map(str, list))


def dclist(techset):
    """Generate a technology set for a data command statement"""
    out = ""
    for i in techset.keys():
        for j in techset[i]:
            out = out + str(i) + " " + str(j) + "\n"
    return out


def roundup(cap):
    '''
    Round capacity results.
    Catching small numbers due to solver numerical tolerance.
    Let bigger negative numners pass to raise exceptions.
    '''
    if -1e-6 < cap < 1:
        return 0
    if cap < -1e-6:
        return cap
    return cap


def setinstancecapacity(instance, data):
    ''' Fix capacity varibles from cluster results to speed up dispatch calculation'''
    for z in instance.zones:
        for n in instance.gen_tech_per_zone[z]:
            key = str(z) + ',' + str(n)
            instance.gen_cap_new[z, n].setlb(roundup(
                data['gen_cap_new[' + key + ']']['solution']))
            instance.gen_cap_new[z, n].setub(roundup(
                    data['gen_cap_new[' + key + ']']['solution']))
        for s in instance.stor_tech_per_zone[z]:
            key = str(z) + ',' + str(s)
            instance.stor_cap_new[z, s].setlb(roundup(
                data['stor_cap_new[' + key + ']']['solution']))
            instance.stor_cap_new[z, s].setub(roundup(
                data['stor_cap_new[' + key + ']']['solution']))
        for h in instance.hyb_tech_per_zone[z]:
            key = str(z) + ',' + str(h)
            instance.hyb_cap_new[z, h].setlb(roundup(
                data['hyb_cap_new[' + key + ']']['solution']))
            instance.hyb_cap_new[z, h].setub(roundup(
                data['hyb_cap_new[' + key + ']']['solution']))
        for i in instance.intercon_per_zone[z]:
            key = str(z) + ',' + str(i)
            instance.intercon_cap_new[z, i].setlb(roundup(
                data['intercon_cap_new[' + key + ']']['solution']))
            instance.intercon_cap_new[z, i].setub(roundup(
                data['intercon_cap_new[' + key + ']']['solution']))
        for r in instance.retire_gen_tech_per_zone[z]:
            key = str(z) + ',' + str(r)
            instance.gen_cap_ret[z, r].setlb(roundup(data['gen_cap_ret[' + key + ']']['solution']))
            instance.gen_cap_ret[z, r].setub(roundup(data['gen_cap_ret[' + key + ']']['solution']))

    return instance


class SolveTemplate:
    """Solve Multi year openCEM simulation based on template"""

    def __init__(self, cfgfile,
                 solver='cbc',
                 log=False, wrkdir=Path(tempfile.mkdtemp()),
                 resume=False,
                 templatetest=False,
                 json_output=False):
        config = configparser.ConfigParser()
        try:
            with open(cfgfile) as f:
                config.read_file(f)
            self.cfgfile = Path(cfgfile)
        except FileNotFoundError:
            raise FileNotFoundError('openCEM Scenario config file not found')

        self.resume = resume
        self.templatetest = templatetest
        Scenario = config['Scenario']
        self.Name = Scenario['Name']
        self.Years = json.loads(Scenario['Years'])
        # Read model options and policy constraints from config file
        options = {}
        for option in model_options()._fields:
            if config.has_option('Scenario', option):
                setattr(self, option, json.loads(Scenario[option]))
                options.update({option: True})
            else:
                setattr(self, option, None)
        # Keep track of policy options to configure model instances down the line
        self.model_options = model_options(**options)

        self.discountrate = Scenario['discountrate']
        self.cost_emit = None
        if config.has_option('Scenario', 'cost_emit'):
            self.cost_emit = json.loads(Scenario['cost_emit'])

        self.manual_intercon_build = None
        if config.has_option('Scenario', 'manual_intercon_build'):
            self.manual_intercon_build = json.loads(Scenario['manual_intercon_build'])
        # Miscelaneous options
        self.description = None
        if config.has_option('Scenario', 'Description'):
            self.description = Scenario['Description']
        # Advanced configuration options
        Advanced = config['Advanced']
        self.Template = make_file_path(Advanced['Template'], self.cfgfile)

        self.custom_costs = None
        if config.has_option('Advanced', 'custom_costs'):
            self.custom_costs = make_file_path(Advanced['custom_costs'], self.cfgfile)

        self.exogenous_capacity = None
        if config.has_option('Advanced', 'exogenous_capacity'):
            self.exogenous_capacity = make_file_path(Advanced['exogenous_capacity'], self.cfgfile)

        self.exogenous_transmission = None
        if config.has_option('Advanced', 'exogenous_transmission'):
            self.exogenous_transmission = make_file_path(Advanced['exogenous_transmission'],
                                                         self.cfgfile)

        self.cluster = Advanced.getboolean('cluster')

        self.cluster_max_d = int(Advanced['cluster_sets'])

        self.regions = cemo.const.REGION.keys()
        if config.has_option('Advanced', 'regions'):
            self.regions = json.loads(Advanced['regions'])

        self.zones = cemo.const.ZONE.keys()
        if config.has_option('Advanced', 'zones'):
            self.zones = json.loads(Advanced['zones'])

        self.all_tech = cemo.const.TECH_TYPE.keys()
        if config.has_option('Advanced', 'all_tech'):
            self.all_tech = json.loads(Advanced['all_tech'])
        self.all_tech_per_zone = dict(
            json.loads(Advanced['all_tech_per_zone']))

        # Specify solver and options in cfg file as well
        if config.has_option('Solver', 'solver'):
            self.solver = config['Solver']['solver']
        else:
            self.solver = solver

        if config.has_option('Solver', 'cluster_solver_options'):
            self.cluster_solver_options = config['Solver']['cluster_solver_options']
        else:
            self.cluster_solver_options = None

        if config.has_option('Solver', 'dispatch_solver_options'):
            self.dispatch_solver_options = parse_solver_options(config['Solver']['dispatch_solver_options'])

        else:
            self.dispatch_solver_options = {}

        self.wrkdir = wrkdir
        self.log = log
        self.json_output = json_output
        # initialisation functions
        self.tracetechs()  # TODO refactor this

    # Validate configuration file entries before continuing
    @property
    def Years(self):
        '''Property getter for Years'''
        return self._Years

    @Years.setter
    def Years(self, y):
        if max(y) > 2050:
            raise ValueError("openCEM-Years: Last full year of data is fy2050")
        if min(y) < 2018:
            raise Exception("openCEM-Years: No historical data available")
        self._Years = sorted(y)

    @property
    def discountrate(self):
        '''Property getter for discountrate'''
        return self._discountrate

    @discountrate.setter
    def discountrate(self, data):
        if float(data) < 0 or float(data) > 1:
            raise ValueError(
                'openCEM-discountrate: Value must be between 0 and 1')
        self._discountrate = data

    @property
    def cost_emit(self):
        '''Property getter for cost_emit'''
        return self._cost_emit

    @cost_emit.setter
    def cost_emit(self, data):
        if data is not None:
            if len(data) != len(self.Years):
                raise ValueError(
                    'openCEM-cost_emit: List length does not match Years list')
            if any(x < 0 for x in data):
                raise ValueError(
                    'openCEM-cost_emit: Value must be greater than 0')
        self._cost_emit = data

    @property
    def nem_ret_ratio(self):
        '''Property getter for nem_ret_ratio'''
        return self._nem_ret_ratio

    @nem_ret_ratio.setter
    def nem_ret_ratio(self, data):
        if data is not None:
            if len(data) != len(self.Years):
                raise ValueError(
                    'openCEM-nem_ret_ratio: List length does not match Years list')
            if any(x < 0 for x in data) or any(x > 1 for x in data):
                raise ValueError(
                    'openCEM-nem_ret_ratio: List element(s) outside range [0,1]')
        self._nem_ret_ratio = data

    @property
    def nem_ret_gwh(self):
        '''Property getter for nem_ret_gwh'''
        return self._nem_ret_gwh

    @nem_ret_gwh.setter
    def nem_ret_gwh(self, data):
        if data is not None:
            if len(data) != len(self.Years):
                raise ValueError(
                    'openCEM-nem_ret_gwh: List length does not match Years list')
            if any(x < 0 for x in data):
                raise ValueError(
                    'openCEM-nem_ret_gwh: List element(s) outside range [0,1]')
        self._nem_ret_gwh = data

    @property
    def region_ret_ratio(self):
        '''Property getter for region_ret_ratio'''
        return self._region_ret_ratio

    @region_ret_ratio.setter
    def region_ret_ratio(self, data):
        if data is not None:
            for d in data:
                if len(d[1]) != len(self.Years):
                    raise ValueError(
                        'openCEM-region_ret_ratio: List %s length does not match Years list'
                        % d)
                if any(x < 0 for x in d[1]) or any(x > 1 for x in d[1]):
                    raise ValueError(
                        'openCEM-region_ret_ratio: Element(s) in list %s outside range [0,1]'
                        % d)
        self._region_ret_ratio = dict(data) if data is not None else data

    @property
    def nem_emit_limit(self):
        '''Property getter for nem_emit_limit'''
        return self._emitrate

    @nem_emit_limit.setter
    def nem_emit_limit(self, data):
        if data is not None:
            if len(data) != len(self.Years):
                raise ValueError(
                    'openCEM-nem_emit_limit: List %s length does not match Years list'
                )
            if any(x < 0 for x in data):
                raise ValueError(
                    'openCEM-nem_emit_limit: Element(s) in list must be positive')
        self._emitrate = data

    @property
    def nem_disp_ratio(self):
        '''Property getter for nem_disp_ratio'''
        return self._nem_disp_ratio

    @nem_disp_ratio.setter
    def nem_disp_ratio(self, data):
        if data is not None:
            if len(data) != len(self.Years):
                raise ValueError(
                    'openCEM-nem_disp_ratio: List %s length does not match Years list'
                )
            if any(x < 0 for x in data) or any(x > 1 for x in data):
                raise ValueError(
                    'openCEM-nem_disp_ratio: Element(s) in list must be between 0 and 1')
        self._nem_disp_ratio = data

    @property
    def nem_re_disp_ratio(self):
        '''Property getter for nem_re_disp_ratio'''
        return self._nem_re_disp_ratio

    @nem_re_disp_ratio.setter
    def nem_re_disp_ratio(self, data):
        if data is not None:
            if len(data) != len(self.Years):
                raise ValueError(
                    'openCEM-nem_re_disp_ratio: List %s length does not match Years list'
                )
            if any(x < 0 for x in data) or any(x > 1 for x in data):
                raise ValueError(
                    'openCEM-nem_re_disp_ratio: Element(s) in list must be between 0 and 1')
        self._nem_re_disp_ratio = data

    @property
    def manual_intercon_build(self):
        '''Property getter for manual_intercon_build'''
        return self._manual_intercon_build

    @manual_intercon_build.setter
    def manual_intercon_build(self, data):
        if data is not None:
            if len(data) != len(self.Years):
                raise ValueError(
                    'openCEM-manual_intercon_build: List %s length does not match Years list'
                )
            if any(not isinstance(x, bool) for x in data):
                raise ValueError(
                    'openCEM-manual_intercon_build: Element(s) in list must be boolean')
        self._manual_intercon_build = data

    @property
    def Template(self):
        '''Propery setter for Template'''
        return self._Template

    @Template.setter
    def Template(self, a):
        if not a.exists():
            raise OSError("openCEM-Template: File not found")
        self._Template = a

    @property
    def custom_costs(self):
        '''Property setter for custom_costs'''
        return self._custom_costs

    @custom_costs.setter
    def custom_costs(self, a):
        if a is not None:
            if not Path(a).exists():
                raise OSError("openCEM-custom_costs: File not found")
        self._custom_costs = a

    @property
    def exogenous_capacity(self):
        '''Property setter for exogenous_capacity'''
        return self._exogenous_capacity

    @exogenous_capacity.setter
    def exogenous_capacity(self, a):
        if a is not None:
            if not Path(a).exists():
                raise OSError("openCEM-exogenous_capacity: File not found")
        self._exogenous_capacity = a

    @property
    def exogenous_transmission(self):
        '''Property setter for exogenous_transmission'''
        return self._exogenous_transmission

    @exogenous_transmission.setter
    def exogenous_transmission(self, a):
        if a is not None:
            if not Path(a).exists():
                raise OSError("openCEM-exogenous_transmission: File not found")
        self._exogenous_transmission = a

    def tracetechs(self):  # TODO refactor this and how tech sets populate template DICT comprehension perhaps? see intercons
        '''Reproduce sparse sets to correctly populate templates'''
        self.fueltech = {}
        self.committech = {}
        self.regentech = {}
        self.dispgentech = {}
        self.redispgentech = {}
        self.hybtech = {}
        self.gentech = {}
        self.stortech = {}
        self.retiretech = {}
        self.intercons = {i: [j for j in cemo.const.ZONE_INTERCONS[i].keys()]
                          for i in cemo.const.ZONE_INTERCONS.keys()}
        for i in self.all_tech_per_zone:
            self.fueltech.update({
                i: [j for j in self.all_tech_per_zone[i] if j in cemo.const.FUEL_TECH]
            })
            self.committech.update({
                i: [j for j in self.all_tech_per_zone[i] if j in cemo.const.COMMIT_TECH]
            })
            self.regentech.update({
                i: [j for j in self.all_tech_per_zone[i] if j in cemo.const.RE_GEN_TECH]
            })
            self.dispgentech.update({
                i: [j for j in self.all_tech_per_zone[i] if j in cemo.const.DISP_GEN_TECH]
            })
            self.redispgentech.update({
                i: [j for j in self.all_tech_per_zone[i] if j in cemo.const.RE_DISP_GEN_TECH]
            })
            self.hybtech.update({
                i: [j for j in self.all_tech_per_zone[i] if j in cemo.const.HYB_TECH]
            })
            self.gentech.update({
                i: [j for j in self.all_tech_per_zone[i] if j in cemo.const.GEN_TECH]
            })
            self.stortech.update({
                i: [j for j in self.all_tech_per_zone[i] if j in cemo.const.STOR_TECH]
            })
            self.retiretech.update({
                i: [j for j in self.all_tech_per_zone[i] if j in cemo.const.RETIRE_TECH]
            })

    def carryforwardcap(self, year):
        '''Generate initial capacity for each year.
        For the first year it is a database query of the capacity table.
        For subsequent years it is the net carry forward capacity stored in JSON
        in the temporary directory'''
        if self.Years.index(year):
            prevyear = self.Years[self.Years.index(year) - 1]
            opcap0 = "load '" + str(self.wrkdir / ('gen_cap_op' + str(prevyear) + '.json')) \
                     + "' : [zones,all_tech] gen_cap_initial stor_cap_initial hyb_cap_initial intercon_cap_initial;"
        else:
            opcap0 = '''#operating capacity for generating techs regions
load "opencem-isp2020.cyisekdyolmb.ap-southeast-2.rds.amazonaws.com" database=opencem_input
user=select password=select_password1 using=pymysql
query="select ntndp_zone_id as zones, technology_type_id as all_tech, sum(reg_cap) as gen_cap_initial
from capacity
where (ntndp_zone_id,technology_type_id) in
''' + sql_tech_pairs(self.gentech) + '''
and commissioning_year is NULL and source_id=3
group by zones,all_tech;" : [zones,all_tech] gen_cap_initial;

# operating capacity storage techs in regions
load "opencem-isp2020.cyisekdyolmb.ap-southeast-2.rds.amazonaws.com" database=opencem_input
user=select password=select_password1 using=pymysql
query="select ntndp_zone_id as zones, technology_type_id as all_tech, sum(reg_cap) as stor_cap_initial
from capacity
where (ntndp_zone_id,technology_type_id) in
''' + sql_tech_pairs(self.stortech) + '''
and commissioning_year is NULL and source_id=3
group by zones,all_tech;" : [zones,all_tech] stor_cap_initial;

# operating capacity for hybrid techs in regions
load "opencem-isp2020.cyisekdyolmb.ap-southeast-2.rds.amazonaws.com" database=opencem_input
user=select password=select_password1 using=pymysql
query="select ntndp_zone_id as zones, technology_type_id as all_tech, sum(reg_cap) as hyb_cap_initial
from capacity
where (ntndp_zone_id,technology_type_id) in
''' + sql_tech_pairs(self.hybtech) + '''
and commissioning_year is NULL and source_id=3
group by zones,all_tech;" : [zones,all_tech] hyb_cap_initial;

# operating capacity for intercons in nodes
# Currently extracted from cemo.const during initalisation
'''
        return opcap0

    def carry_forward_cap_costs(self, year):
        '''Fill template to retrieve carry forward annualised capital costs from gen_cap_op json'''
        carry_fwd_cost = ''
        if self.Years.index(year):
            carry_fwd_cost = "#Carry forward annualised capital costs\n"
            prevyear = self.Years[self.Years.index(year) - 1]
            carry_fwd_cost += "load '" + str(self.wrkdir / ('gen_cap_op' + str(prevyear) + '.json'))\
                              + "' : cost_cap_carry_forward_sim;\n"
        return carry_fwd_cost

    def produce_custom_costs(self, y):
        '''Produce custom costs in template from data.

        These costs override costs as defined by default or template queries.
        Custom costs are specified in the configuration file as a separate csv file
        read with pandas.
        Template is a pyomo data command file where parameter
        values correspond to the last data command instruction statement'''
        year = str(y)
        custom_costs = '\n'
        keywords = {
            'cost_gen_build': 'zonetech',
            'cost_hyb_build': 'zonetech',
            'cost_stor_build': 'zonetech',
            'cost_fuel': 'zonetech',
            'build_cost': 'tech',
            'cost_gen_fom': 'tech',
            'cost_gen_vom': 'tech',
            'cost_hyb_fom': 'tech',
            'cost_hyb_vom': 'tech',
            'cost_stor_fom': 'tech',
            'cost_stor_vom': 'tech'}
        if self.custom_costs is not None:
            costs = pd.read_csv(self.custom_costs, skipinitialspace=True)
            for key in keywords:
                if year in costs.columns:
                    cost = costs[
                        (costs['name'] == key)
                        & (costs['tech'].isin(self.all_tech))
                    ].dropna(subset=[year])
                else:
                    cost = pd.DataFrame()
                if not cost.empty:
                    custom_costs += '#Custom cost entry for ' + key + '\n'
                    custom_costs += 'param ' + key + ':=\n'
                    if keywords[key] == 'tech':
                        custom_costs += cost[['tech', year]].to_string(header=False,
                                                                       index=False,
                                                                       formatters={
                                                                           'tech': lambda x: '%i' % x,  # noqa
                                                                           year: lambda x: '%12.6f' % x,  # noqa
                                                                       })
                    else:
                        cost = cost[cost[['zone', 'tech']].apply(tuple, 1).isin([
                            (i, j) for i in self.all_tech_per_zone
                            for j in self.all_tech_per_zone[i]])]
                        custom_costs += cost[['zone', 'tech', year]
                                             ].to_string(header=False, index=False,
                                                         formatters={
                                                             'zone': lambda x: '%i' % x,
                                                             'tech': lambda x: '%i' % x,
                                                             year: lambda x: '%12.6f' % x,
                                                         })
                    custom_costs += '\n;\n'

        return custom_costs

    def produce_exogenous_capacity(self, year):
        '''Produce exogenous capacity builds in template based on instructions
         from configuration file'''
        keywords = {
            'gen_cap_exo': 'zonetech',
            'stor_cap_exo': 'zonetech',
            'hyb_cap_exo': 'zonetech',
            'ret_gen_cap_exo': 'zonetech',
        }
        exogenous_capacity = '\n'
        if self.exogenous_capacity is not None:
            capacity = pd.read_csv(
                self.exogenous_capacity, skipinitialspace=True)
            prevyear = 2017
            if self.Years.index(year) > 0:
                prevyear = self.Years[self.Years.index(year) - 1]

            for key in keywords:
                cap = capacity[
                    (capacity['year'] > int(prevyear))
                    & (capacity['year'] <= int(year))
                    & (capacity['name'] == key)
                    & (capacity['tech'].isin(self.all_tech))
                    & (capacity['zone'].isin(self.zones))
                ]
                if not cap.empty:
                    cap = cap.groupby(by=['zone', 'tech']).sum().reset_index()
                    # TODO reject entries for techs that are not in techs_in_zones
                    exogenous_capacity += '# Exogenous capacity entry ' + key + '\n'
                    exogenous_capacity += 'param ' + key + ':=\n'
                    exogenous_capacity += cap[['zone', 'tech', 'value']
                                              ].to_string(header=False, index=False,
                                                          formatters={
                                                              'zone': lambda x: '%i' % x,
                                                              'tech': lambda x: '%i' % x,
                                                              'value': lambda x: '%10.2f' % x,
                                                          })
                    exogenous_capacity += '\n;\n'
        return exogenous_capacity

    def produce_exogenous_transmission(self, year):
        '''Produce exogenous transmission builds in template based on instructions
         from configuration file'''
        keywords = {
            'intercon_cap_exo': 'zonezone',
        }
        if self.exogenous_transmission is not None:
            capacity = pd.read_csv(
                self.exogenous_transmission, skipinitialspace=True)
            prevyear = 2017
            if self.Years.index(year) > 0:
                prevyear = self.Years[self.Years.index(year) - 1]

            exo_trans = '\n'
            for key in keywords:
                cap = capacity[
                    (capacity['year'] > int(prevyear))
                    & (capacity['year'] <= int(year))
                    & (capacity['name'] == key)
                    & (capacity['zone_source'].isin(self.zones))
                    & (capacity['zone_dest'].isin(self.zones))
                    ]
                if not cap.empty:
                    cap = cap.groupby(by=['zone_source', 'zone_dest']).sum().reset_index()
                    # remove entries that violate intercon link list
                    for row in cap.itertuples():
                        if row.zone_dest not in self.intercons[row.zone_source]:
                            cap = cap.drop(row.Index)
                    exo_trans += '# Exogenous transmission entry ' + key + '\n'
                    exo_trans += 'param ' + key + ':=\n'
                    exo_trans += cap[['zone_source', 'zone_dest', 'value']
                                     ].to_string(header=False,
                                                 index=False,
                                                 formatters={
                                                  'zone_source': lambda x: '%i' % x,
                                                  'zone_dest': lambda x: '%i' % x,
                                                  'value': lambda x: '%10.2f' % x,
                                                          })
                    exo_trans += '\n;\n'
                    return exo_trans
        return '\n'

    def generateyeartemplate(self, year, test=False):
        """Generate data command file template used for clusters and full runs"""
        dcfName = self.wrkdir / ('Sim' + str(year) + '.dat')
        fcr = "\n#Discount rate for project\n"\
            + "param all_tech_discount_rate := " + \
            str(self.discountrate) + ";\n"

        opcap0 = self.carryforwardcap(year)
        carry_fwd_cap = self.carry_forward_cap_costs(year)
        custom_costs = self.produce_custom_costs(year)
        exogenous_capacity = self.produce_exogenous_capacity(year)
        exogenous_transmission = self.produce_exogenous_transmission(year)

        cemit = ""
        if self.cost_emit:
            cemit = "#Cost of emissions $/Ton\n"\
                + "param cost_emit:= " + \
                    str(self.cost_emit[self.Years.index(year)]) + ";\n"

        nem_ret_ratio = ""
        if self.nem_ret_ratio:
            nem_ret_ratio = "\n # NEM wide RET\n"\
                + "param nem_ret_ratio :=" + \
                str(self.nem_ret_ratio[self.Years.index(year)]) + ";\n"

        nem_ret_gwh = ""
        if self.nem_ret_gwh:
            nem_ret_gwh = "\n # NEM wide RET\n"\
                + "param nem_ret_gwh :=" + \
                str(self.nem_ret_gwh[self.Years.index(year)]) + ";\n"

        region_ret_ratio = ""
        if self.region_ret_ratio:
            region_ret_ratio = "\n #Regional based RET\n"\
                + "param region_ret_ratio := " +\
                ' '.join(str(i) + " " + str(self.region_ret_ratio[i][self.Years.index(year)])
                         for i in self.region_ret_ratio) + ";\n"

        nem_emit_limit = ""
        if self.nem_emit_limit:
            nem_emit_limit = "\n #NEM wide emission limit (in GT)\n"\
                + "param nem_emit_limit := " +\
                  str(self.nem_emit_limit[self.Years.index(year)]) + ";\n"

        nem_disp_ratio = ""
        if self.nem_disp_ratio:
            nem_disp_ratio = "\n #NEM wide minimum generation ratio from dispatchable tech\n"\
                + "param nem_disp_ratio := " +\
                  str(self.nem_disp_ratio[self.Years.index(year)]) + ";\n"

        nem_re_disp_ratio = ""
        if self.nem_re_disp_ratio:
            nem_re_disp_ratio = "\n #NEM wide minimum generation ratio from dispatchable tech\n"\
                + "param nem_re_disp_ratio := " +\
                  str(self.nem_re_disp_ratio[self.Years.index(year)]) + ";\n"

        if self.Years.index(year) == 0:
            prevyear = 2017
        else:
            prevyear = self.Years[self.Years.index(year) - 1]

        with open(self.Template, 'rt') as fin:
            with open(dcfName, 'w') as fo:
                for line in fin:
                    line = line.replace('[regions]', " ".join(
                        str(i) for i in self.regions))
                    line = line.replace('[regionslist]', sql_list(self.regions))
                    line = line.replace('[zones]', " ".join(
                        str(i) for i in self.zones))
                    line = line.replace('[zoneslist]', sql_list(self.zones))
                    line = line.replace('[alltech]', " ".join(
                        str(i) for i in self.all_tech))
                    line = line.replace('[alltechlist]', sql_list(self.all_tech))
                    line = line.replace('XXXX', str(year))
                    line = line.replace('WWWW', str(prevyear))
                    line = line.replace('[gentech]', dclist(self.gentech))
                    line = line.replace('[gentechdb]', sql_tech_pairs(self.gentech))
                    line = line.replace('[athena_gentechdb]', athena_tech_pairs(self.gentech))
                    line = line.replace('[gentechlist]',
                                        sql_list([tech for tech in cemo.const.GEN_TECH
                                                  if tech in self.all_tech]))
                    line = line.replace('[stortech]', dclist(self.stortech))
                    line = line.replace('[stortechdb]', sql_tech_pairs(self.stortech))
                    line = line.replace('[stortechlist]', sql_list([
                        tech for tech in cemo.const.STOR_TECH if tech in self.all_tech]))
                    line = line.replace('[hybtech]', dclist(self.hybtech))
                    line = line.replace('[hybtechdb]', sql_tech_pairs(self.hybtech))
                    line = line.replace('[hybtechlist]', sql_list(
                        [tech for tech in cemo.const.HYB_TECH if tech in self.all_tech]))
                    line = line.replace('[retiretech]',
                                        dclist(self.retiretech))
                    line = line.replace('[retiretechdb]',
                                        sql_tech_pairs(self.retiretech))
                    line = line.replace(
                        '[retiretechset]', " ".join(
                            str(i) for i in cemo.const.RETIRE_TECH))
                    line = line.replace('[fueltech]', dclist(self.fueltech))
                    line = line.replace('[fueltechdb]', sql_tech_pairs(self.fueltech))
                    line = line.replace(
                        '[fueltechset]', " ".join(
                            str(i) for i in cemo.const.FUEL_TECH))
                    line = line.replace(
                        '[committech]', dclist(self.committech))
                    line = line.replace('[regentech]', dclist(self.regentech))
                    line = line.replace(
                        '[dispgentech]', dclist(self.dispgentech))
                    line = line.replace(
                        '[redispgentech]', dclist(self.redispgentech))
                    line = line.replace(
                        '[stortechset]', " ".join(
                            str(i) for i in cemo.const.STOR_TECH))
                    line = line.replace(
                        '[hybtechset]', " ".join(
                            str(i) for i in cemo.const.HYB_TECH))
                    line = line.replace(
                        '[nobuildset]', " ".join(
                            str(i) for i in cemo.const.NOBUILD_TECH))
                    line = line.replace('[carryforwardcap]', opcap0)
                    line = line.replace('[timerange]', gen_timerange(year, test))
                    line = line.replace('[athena_timerange]',
                                        gen_timerange(year, test, athena=True))
                    fo.write(line)
                fo.write(custom_costs)
                fo.write(exogenous_capacity)
                fo.write(exogenous_transmission)
                fo.write(fcr)
                fo.write(cemit)
                fo.write(carry_fwd_cap)
                fo.write(nem_ret_ratio)
                fo.write(nem_ret_gwh)
                fo.write(region_ret_ratio)
                fo.write(nem_emit_limit)
                fo.write(nem_disp_ratio)
                fo.write(nem_re_disp_ratio)
        return str(dcfName)

    def get_model_options(self, year):
        '''Return model options appropriate for each year based on cfg'''
        OPTIONS = {}
        for option in self.model_options._fields:
            OPTIONS.update({option: getattr(self.model_options, option)})

        manual_intercon_build = self.manual_intercon_build[self.Years.index(
            year)] if self.manual_intercon_build is not None else False

        OPTIONS.update(
         {'build_intercon_manual': manual_intercon_build}
        )
        return model_options(**OPTIONS)

    def solve(self):
        """
        Multi year simulation:
        Instantiate a template instance for each year in the simulation.
        Calcualte capacity using clustering and dispatch with full year.
        Alternatively caculate capacity and dispatch simultanteously using full year instance
        Save capacity results for carry forward in json file.
        Save full results for year in parquet/JSON file.
        Assemble full simulation output as metadata + full year results in each simulated year
        """
        for y in self.Years:
            if self.resume:
                if self.json_output:
                    if (self.wrkdir / (str(y)+'.json')).exists():
                        print("Skipping year %s" % y)
                        continue
                else:
                    if (self.wrkdir / (str(y))).exists():
                        print("Skipping year %s" % y)
                        continue
            else:
                shutil.rmtree(self.wrkdir/str(y), ignore_errors=True)

            if self.log:
                print("openCEM multi: Starting simulation for year %s" % y)
            # Populate template with this inv period's year and timestamps
            year_template = self.generateyeartemplate(y, self.templatetest)
            # Solve full year capacity and dispatch instance
            # Create model based on policy configuration options
            model = CreateModel(y, self.get_model_options(y)).create_model()
            # create model instance based in template data
            inst = model.create_instance(year_template)
            # These solve capacity on a clustered form
            if self.cluster and not self.templatetest:
                clus = InstanceCluster(inst, self.cluster_max_d)
                ccap = ClusterRun(
                    clus,
                    year_template,
                    model_options=self.get_model_options(y),
                    solver=self.solver,
                    solver_options=self.cluster_solver_options,
                    log=self.log).run_cluster()
                inst = setinstancecapacity(inst, ccap.data)

            # Solve the model (or just dispatch if capacity has been solved)
            opt = SolverFactory(self.solver)
            opt.options = self.dispatch_solver_options
            if self.log:
                print("openCEM multi: Starting full year dispatch simulation")
            opt.solve(inst, tee=self.log, keepfiles=False)
            del opt

            # Carry forward operating capacity to next Inv period
            opcap = json_carry_forward_cap(inst)
            if y != self.Years[-1]:
                with open(self.wrkdir / ('gen_cap_op' + str(y) + '.json'), 'w') as op:
                    json.dump(opcap, op)
            # Dump simulation result in JSON forma
            if self.log:
                print("openCEM multi: Saving year %s results to directory" % y)
            if self.json_output:
                with open(self.wrkdir / (str(y) + '.json'), 'w') as json_out:
                    json.dump(jsonify(inst, y), json_out)
                    json_out.write('\n')
            else:
                parquetify(inst, self.wrkdir, y)

            if self.json_output:
                printstats(inst)  # REVIEW this summary printing is slow compared to parquet summary
            [cdu, cost] = Summary(self.wrkdir, [i for i in self.Years if i <= y], cache=False).get_summary()
            cdu.to_csv(self.wrkdir/("cdeu.zip"), compression={'method': 'zip', 'archive_name': 'cdeu.csv'})
            cost.to_csv(self.wrkdir/("cost.zip"), compression={'method': 'zip', 'archive_name': 'cost.csv'})

            del inst  # to keep memory down
        if self.json_output:
            # Merge JSON output for all investment periods
            if self.log:
                print("openCEM multi: Saving final results to JSON file")
            if not self.templatetest:
                self.mergejsonyears()
        else:
            meta = self.generate_metadata()
            with open(self.wrkdir / (self.cfgfile.stem + '_meta.json'), 'w') as metadata:
                json.dump(meta, metadata, indent=0)

    def mergejsonyears(self):
        '''Merge the full year JSON output for each simulated year in a single dictionary'''
        data = self.generate_metadata()
        # Save json output named after .cfg file
        with open(self.cfgfile.with_name(self.cfgfile.stem + '.json'), 'w') as out_file:
            json.dump(data, out_file)
            out_file.write('\n')
            for year in self.Years:
                with open(self.wrkdir / (str(year) + '.json'), 'r') as in_file:
                    copyfileobj(in_file, out_file)

    def generate_metadata(self):
        '''Append simulation metadata to full JSON output'''
        meta = {
            "Name": self.Name,
            "Years": self.Years,
            "Template": str(self.Template),
            "Clustering": self.cluster,
            "Cluster_number":  self.cluster_max_d if self.cluster else 0,
            "Solver": self.solver,
            "Discount_rate": self.discountrate,
            "Emission_cost": self.cost_emit,
            "Description": self.description,
            "NEM wide RET as ratio": self.nem_ret_ratio,
            "NEM wide RET as GWh": self.nem_ret_gwh,
            "Regional based RET": self.region_ret_ratio,
            "System emission limit": self.nem_emit_limit,
            "Dispatchable generation ratio ": self.nem_disp_ratio,
            "Renewable Dispatchable generation ratio ": self.nem_re_disp_ratio,
            "Custom costs": pd.read_csv(self.custom_costs).fillna(value={'zone': 0}).fillna(99e7).to_dict(orient='records') if self.custom_costs is not None else None,  # noqa
            "Exogenous Capacity decisions": pd.read_csv(self.exogenous_capacity).to_dict(orient='records') if self.exogenous_capacity is not None else None,  # noqa
            "Exogenous Transmission decisions": pd.read_csv(self.exogenous_transmission).to_dict(orient='records') if self.exogenous_transmission is not None else None,  # noqa
        }

        return {'meta': meta}
