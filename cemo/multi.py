# Multi year simulation module
import configparser
import datetime
import json
import os.path
import tempfile

from pyomo.opt import SolverFactory

import cemo.const
from cemo.cluster import ClusterRun, InstanceCluster
from cemo.core import create_model
from cemo.jsonify import json_carry_fwd_cap, jsonify
from cemo.utils import printstats


def sqllist(techset):
    """Generate a technology set for SQL statement"""
    out = []
    for i in techset.keys():
        for j in techset[i]:
            out.append((i, j))
    if not out:
        out.append((99, 99))  # preserve query syntax if list is empty
    return "(" + ", ".join(map(str, out)) + ")"


def dclist(techset):
    """Generate a technology set for a data command statement"""
    out = ""
    for i in techset.keys():
        for j in techset[i]:
            out = out + str(i) + " " + str(j) + "\n"
    return out


def roundup(cap):
    '''
    Round results to 2 signigicant digits.
    Catching small negative numbers due to solver numerical tolerance.
    Let big negative numners pass to raise exception.
    '''
    if cap > -1e-6 and cap < 0:
        return 0
    return round(cap, 2)


def setinstancecapacity(instance, clustercap):
    ''' write cluster gen_cap_op results for instance'''
    data = clustercap.data
    for z in instance.zones:
        for n in instance.gen_tech_per_zone[z]:
            key = str(z) + ',' + str(n)
            instance.gen_cap_new[z, n] = roundup(
                data['gen_cap_new[' + key + ']']['solution'])
        for s in instance.stor_tech_per_zone[z]:
            key = str(z) + ',' + str(s)
            instance.stor_cap_new[z, s] = roundup(
                data['stor_cap_new[' + key + ']']['solution'])
        for h in instance.hyb_tech_per_zone[z]:
            key = str(z) + ',' + str(h)
            instance.hyb_cap_new[z, h] = roundup(
                data['hyb_cap_new[' + key + ']']['solution'])
        for r in instance.retire_gen_tech_per_zone[z]:
            key = str(z) + ',' + str(r)
            instance.gen_cap_ret[z, r] \
                = roundup(data['gen_cap_ret[' + key + ']']['solution'])

    instance.gen_cap_new.fix()
    instance.stor_cap_new.fix()
    instance.hyb_cap_new.fix()
    instance.gen_cap_ret.fix()
    return instance


class SolveTemplate:
    """Solve Multi year openCEM simulation based on template"""

    def __init__(self, cfgfile, solver='cbc', tmpdir=tempfile.mkdtemp() + '/'):
        config = configparser.ConfigParser()
        try:
            with open(cfgfile) as f:
                config.read_file(f)
        except FileNotFoundError:
            raise FileNotFoundError('openCEM Scenario config file not found')

        Scenario = config['Scenario']
        self.Name = Scenario['Name']
        self.Years = json.loads(Scenario['Years'])
        # Create NEM wide ret constraint based on data
        if config.has_option('Scenario', 'nemret'):
            self.nemret = json.loads(Scenario['nemret'])
        else:
            self.nemret = None

        if config.has_option('Scenario', 'regionret'):
            if config.has_option('Scenario', 'nemret'):
                raise Exception(
                    "Cannot have both NEM and Region RET constraints")
            self.regionret = dict(json.loads(Scenario['regionret']))
        else:
            self.regionret = None

        if config.has_option('Scenario', 'emitlimit'):
            self.emitlimit = json.loads(Scenario['emitlimit'])
        else:
            self.emitlimit = None

        self.discountrate = Scenario['discountrate']
        self.cost_emit = Scenario['cost_emit']

        try:
            self.description = Scenario['Description']
        except KeyError:
            self.description = None

        Advanced = config['Advanced']
        self.Template = Advanced['Template']
        self.cluster = Advanced.getboolean('cluster')
        self.cluster_max_d = int(Advanced['cluster_sets'])
        self.techs = dict(json.loads(Advanced['all_tech_per_zone']))

        self.tmpdir = tmpdir
        self.solver = solver
        # initialisation functions
        self.tracetechs()

    @property
    def Years(self):
        return self._Years

    @Years.setter
    def Years(self, y):
        if max(y) > 2050:
            raise ValueError("openCEM-Years: Last full year of data is 2050")
        if min(y) < 2018:
            raise Exception("openCEM-Years: First year of data is  2018")
        self._Years = sorted(y)

    @property
    def discountrate(self):
        return self._discountrate

    @discountrate.setter
    def discountrate(self, data):
        if float(data) < 0 or float(data) > 1:
            raise ValueError(
                'openCEM-discountrate: Value must be between 0 and 1')
        self._discountrate = data

    @property
    def cost_emit(self):
        return self._discountrate

    @cost_emit.setter
    def cost_emit(self, data):
        if float(data) < 0:
            raise ValueError('openCEM-cost_emit: Value must be greater than 0')
        self._cost_emit = data

    @property
    def nemret(self):
        return self._nemret

    @nemret.setter
    def nemret(self, data):
        if data is not None:
            if len(data) != len(self.Years):
                raise ValueError(
                    'openCEM-nemret: List length does not match Years list')
            if any(x < 0 for x in data) or any(x > 1 for x in data):
                raise ValueError(
                    'openCEM-nemret: List element(s) outside range [0,1]')
        self._nemret = data

    @property
    def regionret(self):
        return self._regionret

    @regionret.setter
    def regionret(self, data):
        if data is not None:
            for d in data:
                if len(data[d]) != len(self.Years):
                    raise ValueError(
                        'openCEM-regionret: List %s length does not match Years list'
                        % d)
                if any(x < 0 for x in data[d]) or any(x > 1 for x in data[d]):
                    raise ValueError(
                        'openCEM-regionret: Element(s) in list %s outside range [0,1]'
                        % d)
        self._regionret = data

    @property
    def emitlimit(self):
        return self._emitrate

    @emitlimit.setter
    def emitlimit(self, data):
        if data is not None:
            if len(data) != len(self.Years):
                raise ValueError(
                    'openCEM-emitlimit: List %s length does not match Years list'
                )
            if any(x < 0 for x in data):
                raise ValueError(
                    'openCEM-emitlimit: Element(s) in list must be positive')
        self._emitrate = data

    @property
    def Template(self):
        return self._Template

    @Template.setter
    def Template(self, a):
        if not os.path.isfile(a):
            raise OSError("openCEM-Template: File not found")
        self._Template = a

    def tracetechs(self):
        self.fueltech = {}
        self.regentech = {}
        self.hybtech = {}
        self.gentech = {}
        self.stortech = {}
        self.retiretech = {}
        for i in self.techs:
            self.fueltech.update({
                i: [j for j in self.techs[i] if j in cemo.const.FUEL_TECH]
            })
            self.regentech.update({
                i: [j for j in self.techs[i] if j in cemo.const.RE_GEN_TECH]
            })
            self.hybtech.update({
                i: [j for j in self.techs[i] if j in cemo.const.HYB_TECH]
            })
            self.gentech.update({
                i: [j for j in self.techs[i] if j in cemo.const.GEN_TECH]
            })
            self.stortech.update({
                i: [j for j in self.techs[i] if j in cemo.const.STOR_TECH]
            })
            self.retiretech.update({
                i: [j for j in self.techs[i] if j in cemo.const.RETIRE_TECH]
            })

    def carryforwardcap(self, year):
        if self.Years.index(year):
            prevyear = self.Years[self.Years.index(year) - 1]
            opcap0 = "load '" + self.tmpdir + "gen_cap_op" + \
                str(prevyear) + \
                ".json' : [zones,all_tech] gen_cap_initial stor_cap_initial hyb_cap_initial;"
        else:
            opcap0 = '''#operating capacity for all technilogies and regions
load "cemo.ckvu5hxg6w5z.ap-southeast-1.rds.amazonaws.com" database=cemo
user=cemo_select password=cemo_password using=pymysql
query="select ntndp_zone_id as zones, technology_type_id as all_tech, sum(reg_cap) as gen_cap_initial
from capacity
where (ntndp_zone_id,technology_type_id) in
''' + sqllist(self.gentech) + '''
and commissioning_year is NULL
group by zones,all_tech;" : [zones,all_tech] gen_cap_initial;

# operating capacity for all technilogies and regions
load "cemo.ckvu5hxg6w5z.ap-southeast-1.rds.amazonaws.com" database=cemo
user=cemo_select password=cemo_password using=pymysql
query="select ntndp_zone_id as zones, technology_type_id as all_tech, sum(reg_cap) as stor_cap_initial
from capacity
where (ntndp_zone_id,technology_type_id) in
''' + sqllist(self.stortech) + '''
and commissioning_year is NULL
group by zones,all_tech;" : [zones,all_tech] stor_cap_initial;

# operating capacity for all technilogies and regions
load "cemo.ckvu5hxg6w5z.ap-southeast-1.rds.amazonaws.com" database=cemo
user=cemo_select password=cemo_password using=pymysql
query="select ntndp_zone_id as zones, technology_type_id as all_tech, sum(reg_cap) as hyb_cap_initial
from capacity
where (ntndp_zone_id,technology_type_id) in
''' + sqllist(self.hybtech) + '''
and commissioning_year is NULL
group by zones,all_tech;" : [zones,all_tech] hyb_cap_initial;
'''
        return opcap0

    def carry_forward_cap_costs(self, year):
        '''Save total annualised capital costs in carry forward json'''
        carry_fwd_cost = "#Carry forward annualised capital costs\n"
        if self.Years.index(year):
            prevyear = self.Years[self.Years.index(year) - 1]
            carry_fwd_cost += "load '" + self.tmpdir + "gen_cap_op" + \
                str(prevyear) + \
                ".json' : cost_cap_carry_forward;\n"
        else:
            carry_fwd_cost += "param cost_cap_carry_forward:=0;\n"

        return carry_fwd_cost

    def generateyeartemplate(self, year):
        """Generate data command file template used for clusters and full runs"""
        date1 = datetime.datetime(year, 1, 1, 0, 0, 0)
        strd1 = "'" + str(date1) + "'"
        date2 = datetime.datetime(year, 12, 31, 23, 0, 0)
        strd2 = "'" + str(date2) + "'\n"
        drange = "WHERE timestamp BETWEEN " + strd1 + " AND " + strd2
        dcfName = self.tmpdir + 'Sim' + str(year) + '.dat'
        fcr = "\n#Discount rate for project\n"\
            + "param all_tech_discount_rate := " + \
            str(self.discountrate) + ";\n"
        cemit = "#Cost of emissions $/Mhw \n"\
            + "param cost_emit:= " + str(self.cost_emit) + ";\n"
        opcap0 = self.carryforwardcap(year)
        carry_fwd_cap = self.carry_forward_cap_costs(year)

        if self.nemret:
            nemret = "\n # NEM wide RET\n"\
                + "param nem_ret_ratio :=" + \
                str(self.nemret[self.Years.index(year)]) + ";\n"
        else:
            nemret = ""

        if self.regionret:
            regionret = "\n #Regional based RET\n"\
                + "param region_ret_ratio := " +\
                ' '.join(str(i) + " " + str(self.regionret[i][self.Years.index(year)])
                         for i in self.regionret) + ";\n"
        else:
            regionret = ""

        if self.emitlimit:
            emitlimit = "\n #NEM wide emission limit (in GT)\n"\
                + "param nem_year_emit_limit := " +\
                  str(self.emitlimit[self.Years.index(year)]) + ";\n"
        else:
            emitlimit = ""

        if self.Years.index(year) == 0:
            prevyear = 2017
        else:
            prevyear = self.Years[self.Years.index(year) - 1]

        with open(self.Template, 'rt') as fin:
            with open(dcfName, 'w') as fo:
                for line in fin:
                    line = line.replace('XXXX', str(year))
                    line = line.replace('WWWW', str(prevyear))
                    line = line.replace('[gentech]', dclist(self.gentech))
                    line = line.replace('[gentechdb]', sqllist(self.gentech))
                    line = line.replace(
                        '[gentechlist]', ", ".join(
                            str(i) for i in cemo.const.GEN_TECH))
                    line = line.replace('[stortech]', dclist(self.stortech))
                    line = line.replace('[stortechdb]', sqllist(self.stortech))
                    line = line.replace(
                        '[stortechlist]', ", ".join(
                            str(i) for i in cemo.const.STOR_TECH))
                    line = line.replace('[hybtech]', dclist(self.hybtech))
                    line = line.replace('[hybtechdb]', sqllist(self.hybtech))
                    line = line.replace(
                        '[hybtechlist]', ", ".join(
                            str(i) for i in cemo.const.HYB_TECH))
                    line = line.replace('[retiretech]',
                                        dclist(self.retiretech))
                    line = line.replace('[retiretechdb]',
                                        sqllist(self.retiretech))
                    line = line.replace(
                        '[retiretechset]', " ".join(
                            str(i) for i in cemo.const.RETIRE_TECH))
                    line = line.replace('[fueltech]', dclist(self.fueltech))
                    line = line.replace('[fueltechdb]', sqllist(self.fueltech))
                    line = line.replace(
                        '[fueltechset]', " ".join(
                            str(i) for i in cemo.const.FUEL_TECH))
                    line = line.replace('[regentech]', dclist(self.regentech))
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
                    if 'WHERE timestamp BETWEEN' in line:
                        line = drange
                    fo.write(line)
                fo.write(fcr)
                fo.write(cemit)
                fo.write(carry_fwd_cap)
                fo.write(nemret)
                fo.write(regionret)
                fo.write(emitlimit)
        return dcfName

    def solve(self):
        """
        Multi year simulation:
        Instantiate a template instance for each year in the simulation.
        Calcualte capacity using clustering and dispatch with full year.
        Alternatively caculate capacity and dispatch simultanteously using full year instance
        Save capacity results for carry forward in json file.
        Save full results for year in JSON file.
        Assemble full simulation output as metadata+ full year results in each simulated year
        """
        for y in self.Years:
            # Populate template with this inv period's year and timestamps
            dcfName = self.generateyeartemplate(y)
            # Solve full year capacity and dispatch instance
            nemret_enable = (True if self.nemret is not None else False)
            regionret_enable = (True if self.regionret is not None else False)
            emitrate_enable = (True if self.emitlimit is not None else False)
            model = create_model(
                y,
                nemret=nemret_enable,
                regionret=regionret_enable,
                emitlimit=emitrate_enable)
            inst = model.create_instance(dcfName)
            # These presolve capacity on a clustered form
            if self.cluster:
                clus = InstanceCluster(inst, self.cluster_max_d)
                ccap = ClusterRun(
                    clus,
                    dcfName,
                    nemret=nemret_enable,
                    regionret=regionret_enable,
                    emitlimit=emitrate_enable,
                    solver=self.solver,
                    log=False).run_cluster()
                inst = setinstancecapacity(inst, ccap)

            # Solve the model (or just dispatch if capacity has been solved)
            opt = SolverFactory(self.solver)
            opt.solve(inst)

            # Carry forward operating capacity to next Inv period
            opcap = json_carry_fwd_cap(inst)
            if y != self.Years[-1]:
                with open(self.tmpdir + 'gen_cap_op' + str(y) + '.json',
                          'w') as op:
                    json.dump(opcap, op)
            # Dump simulation result in JSON forma
            out = jsonify(inst)
            with open(self.tmpdir + str(y) + '.json', 'w') as jo:
                json.dump(out, jo)

            printstats(inst)

            del inst  # to keep memory down
        # Merge JSON output for all investment periods
        self.mergejsonyears()

    def mergejsonyears(self):
        '''Merge the full year JSON output for each simulated year in a single dictionary'''
        data = self.generate_metadata()
        for y in self.Years:
            with open(self.tmpdir + str(y) + '.json', 'r') as f:
                yeardata = {str(y): json.load(f)}
            data.update(yeardata)

        with open(self.Name + '_sol.json', 'w') as fo:
            json.dump(data, fo)

    def generate_metadata(self):
        '''Append simulation metadata to full JSON output'''
        if self.cluster:
            clusterno = self.cluster_max_d
        else:
            clusterno = "N/A"
        meta = {
            "Name": self.Name,
            "Years": self.Years,
            "Template": self.Template,
            "Clustering": self.cluster,
            "Cluster_number": clusterno,
            "Solver": self.solver,
            "Discount_rate": self.discountrate,
            "Emission_cost": self.cost_emit,
        }
        if self.description is not None:
            meta.update({"Description": self.description})

        return {'meta': meta}
