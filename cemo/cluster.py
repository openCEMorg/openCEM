'''Hierachical clustering of demand weeks for openCEM'''
# pylint: disable=bad-continuation
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "GPLv3"
__version__ = "1.0.0"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"
__status__ = "Development"
import datetime
import json
import shutil
import subprocess
import sys
import tempfile
from collections import deque

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist

from cemo.jsonify import fill_complex_param, fill_complex_mutable_param
from cemo.const import GEN_TECH, HYB_TECH, TRACE_TECH


def next_weekday(date, int_weekday):
    '''Calculate next date from given date that is a specified weekday.
    Weekdays are specified as integers from 0 (Mon) to 6(Sun) '''
    days_ahead = int_weekday - date.weekday()
    if days_ahead < 0:  # Target day already happened this week
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)


def prev_weekday(date, int_weekday):
    '''Return closest date before given date that is a specified weekday.
    Weekdays are specified as integers from 0 (Mon) to 6(Sun) '''
    days_behind = date.weekday() - int_weekday
    if days_behind < 0:  # Target day already happened this week
        days_behind += 7
    return date - datetime.timedelta(days_behind)


class ClusterData:
    '''Demand clustering class.
      It takes a financial year of demand data for 1 or multiple regions and uses
      Hierachical clustering to group weekly periods of demand.
      Individuals consist of the concatenated hourly demand for each region in
      a 7 day period defined by a first day of week and last day of week range.
      The cityblock metric is used to measure the distance between indiviuals
      but other metrics are possible.
      Class returns the weight of each cluster (number of individuals) and the
      representative individual for the cluster. Representative individuals are
      the closest to an average for the cluster.'''

    def __init__(self,
                 firstdow=4,
                 lastdow=3,
                 max_d=12,
                 regions=None,
                 maxsynth=False):
        self.firstdow = firstdow  # Day of week starting period
        self.lastdow = lastdow  # Day of week ending period`
        self.max_d = max_d  # Maximum number of clusters
        # NEM region tuple
        self.regions = range(1, 6) if regions is None else regions
        self.maxsynth = maxsynth

        # make week pattern into a list
        self.pdays = (self.lastdow - self.firstdow + 8) % 7
        if self.pdays == 0:
            self.pdays = 7
        dq = deque(range(7), maxlen=7)
        dq.rotate(-self.lastdow)  # rotate to first day in yrange
        self.days = list(dq)[:self.pdays]  # trim week to pdays

        # these are initialised after the first call to _init_timeseries_data
        self.plen = None
        self.dates = None
        self.periods = None

        # Data "indivduals" available as a numpy array
        self.X = self._init_timeseries_data()
        self.nplen = len(self.regions) * self.plen

        # generate a set of max_d clusters
        self.generate_cluster()

    def __repr__(self):
        return 'Cluster Data generator\n %r' % self.Xcluster

    def _init_timeseries_data(self):
        X = np.array([])
        for r in self.regions:
            Xd = self._get_region_data(r)
            X = np.column_stack([X, Xd]) if X.size else Xd
        return X

    def _get_region_data(self, region):
        df = self._data_query(region)
        # arrange data back into rows of days with 48 half hour periods
        df.set_index([df.index.date, df.index.time], inplace=True)
        df = df.unstack()
        # top and tail year to start and finish within week interval
        first_doy = next_weekday(datetime.date(
            self.year - 1, 7, 1), self.firstdow)
        last_doy = prev_weekday(datetime.date(self.year, 6, 30), self.lastdow)
        df = df[df.index >= pd.to_datetime(first_doy)]
        df = df[df.index <= pd.to_datetime(last_doy)]
        # now keep those days you want to keep, eg. sunday to Wednesday
        df = df[df.index.dayofweek.isin(self.days)]

        if self.dates is None:
            self.dates = np.array(df.index.values[::self.pdays], dtype='M8[s]')

        # Data rows in X are days. Rearrange into pday periods
        X = df.values
        ndays = X.shape[0]  # total days in given year
        nperiods = X.shape[1]  # dispatch periods in data
        if self.plen is None:
            self.plen = nperiods * self.pdays
        # number of whole pday periods
        if self.periods is None:
            self.periods = int((ndays - ndays % self.pdays) / self.pdays)
        # rearange into pdays
        X1 = np.empty((self.periods, self.plen))
        for j in range(self.periods):
            X1[j] = np.concatenate(
                [X[self.pdays * j + i] for i in range(self.pdays)])

        return X1

    def _calc_Xsynth(self, max_p=False):
        # empty array of synthetic individual in each cluster
        self.Xsynth = np.empty((self.max_d, self.nplen))

        for k in range(self.max_d):
            # calculate synthetic individual per clusters
            if max_p:
                self.Xsynth[k] = self.Xclus[k].max(axis=0)[:self.nplen]
            else:
                self.Xsynth[k] = self.Xclus[k].mean(axis=0)[:self.nplen]

    def clusterset(self, max_d, method='average', metric='cityblock'):
        """Group period observations into clusters and save into Xcluster"""
        self.max_d = max_d
        # Perform selected clustering algorithm on dataset
        Z = linkage(self.X, method, metric=metric)
        # vector indicating the cluster to which each member of X belongs
        self.cluster = fcluster(Z, self.max_d, criterion='maxclust')
        # Add index to dataset to backtrack day of the year
        X2 = np.column_stack((self.X, range(1, self.X.shape[0] + 1)))
        # Break down X into a list of numpy arrays, one for each cluster
        self.Xclus = [np.empty((0, self.nplen + 1))] * self.max_d
        for j in range(X2.shape[0]):
            self.Xclus[self.cluster[j] - 1] \
                = np.row_stack((self.Xclus[self.cluster[j] - 1], X2[j, :]))
        # genereate Xsynth (by default is the max of all features in cluster)
        self._calc_Xsynth(max_p=self.maxsynth)

        # Obtain the date index for the observation in each cluster
        # closest to their respective cluster mean
        Xcl = []  # initialise array
        for k in range(self.max_d):
            # slice into data and indices
            Xclusidx = self.Xclus[k][:, self.nplen:]  # date indices
            # observations in each cluster
            Xclusobs = self.Xclus[k][:, :self.nplen]
            # append mean to each cluster
            Xclusobs = np.row_stack((self.Xsynth[k], Xclusobs))
            # determine distance between mean and each observation in cluster
            pdist_temp = pdist(Xclusobs, metric=metric)[:Xclusobs.shape[0] - 1]
            idx = pdist_temp.argmin()  # nearest observation to Xsynth in clus
            # save day of the year index plus the cluster relative weight
            Xcl.append((int(Xclusidx[idx]), self.dates[int(Xclusidx[idx]) - 1],
                        (Xclusobs.shape[0] - 1) / self.periods))

        # store cluster information in a convenient pandas DataFrame
        self.Xcluster = pd.DataFrame(
            Xcl, columns=['week', 'date', 'weight']).sort_values(by='date')

    def append_to_cluster(self, date):
        '''Append arbitrary weeks to cluster'''
        if date is None:
            return
        cluster = self.Xcluster
        # rescale weights to weeks
        cluster.weight *= self.periods
        # deduct 1 week from the largest cluster
        row = cluster.weight.idxmax()
        cluster.at[row, 'weight'] -= 1
        # Add injected week
        clus = cluster.append(pd.DataFrame.from_dict(
            {'week': [52 if cluster.week.max() < 52 else cluster.week.max()+1],
             'date': [pd.Timestamp(date)],
             'weight': [1]
             }
        ))
        # scale back weights to sum 1
        clus.weight *= 1 / self.periods
        clus.reset_index(drop=True, inplace=True)
        # save cluster back in object
        self.Xcluster = clus
        self.max_d += 1

    def _detect_dunkelflaute(self):
        return None

    def generate_cluster(self):
        self.clusterset(self.max_d)
        self.append_to_cluster(self._detect_dunkelflaute())


class CSVCluster(ClusterData):
    """Weekly Cluster from CSV file, to perform unit tests and standalone clustering studies"""

    def __init__(
            self,
            max_d=12,
            source='tests/SampleDemand.csv.gz',
    ):
        self.source = source
        ClusterData.__init__(self, max_d=max_d)

    def _data_query(self, region):
        try:
            df = pd.read_csv(
                filepath_or_buffer=self.source,
                compression='infer',
                index_col='timestamp',
                parse_dates=['timestamp'])
            self.year = df.index[-1].year
            return df
        except FileNotFoundError:
            raise SystemExit("CSVCluster: Unable to open data file")


class InstanceCluster(ClusterData):
    """Create weekly clusters from demand data in model instance"""

    def __init__(self, instance, max_d=12):
        self.demand = fill_complex_param(instance.region_net_demand)
        self.time = instance.t
        self.gen_cap_factor = fill_complex_mutable_param(instance.gen_cap_factor)
        self.hyb_cap_factor = fill_complex_mutable_param(instance.hyb_cap_factor)
        self.regions = instance.regions
        self.zones_per_region = instance.zones_per_region
        self.windowidth = 24*7
        ClusterData.__init__(self, max_d=max_d, regions=instance.regions)

    def _data_query(self, region):
        # Pandas from demandionary
        df = pd.DataFrame.from_dict(self.demand)
        # split the index string into two columns, region and timestamp
        df2 = pd.DataFrame(
            df['index'].values.tolist(), columns=['region', 'timestamp'])
        # replace index with region and timestamp
        df = pd.concat([df2, df['value']], axis=1)
        # filter by region
        df = df[df['region'] == region]
        # drop region column
        df = df.drop('region', axis=1)
        # format timestamp as a datetime object and index
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index(pd.DatetimeIndex(df['timestamp']))
        # drop timestamp column now that we have an index
        df = df.drop('timestamp', axis=1)
        # set year parameter based on trace data
        self.year = df.iloc[-1].name.year
        return df

    def _detect_dunkelflaute(self):
        '''Return a date as string with the beginning of a dark/doldrum week period'''
        MAXLOAD = np.array([i['value'] for i in self.demand]).max()
        TIME = np.array([np.datetime64(i) for i in self.time])
        RATIO = np.zeros(len(TIME))
        for region in self.regions:
            LOAD = np.array([j if j >= 100 else 100
                             for j in [i['value'] for i in self.demand if i['index'][0] == region]])
            VRE_RESOURCE = np.zeros(len(TIME))
            for tech in TRACE_TECH:
                if tech in GEN_TECH:
                    tech_trace = 'gen_cap_factor'
                if tech in HYB_TECH:
                    tech_trace = 'hyb_cap_factor'
                for zone in self.zones_per_region[region]:
                    TRACE = np.array([i['value']
                                      for i in getattr(self, tech_trace)
                                      if i['index'][0] == zone and i['index'][1] == tech])
                    if len(TRACE) == len(TIME):
                        VRE_RESOURCE += TRACE
            RATIO += (VRE_RESOURCE / LOAD) * MAXLOAD
        ww = int(self.windowidth / 2)
        RATIO = np.pad(RATIO, (ww, ww), 'wrap')
        W_RATIO = pd.Series(RATIO).rolling(self.windowidth,
                                           center=True,
                                           win_type='boxcar').mean()[ww:-ww].reset_index(drop=True)
        return str(TIME[W_RATIO.idxmin()] - np.timedelta64(3, 'D'))[:10]


class ClusterRun:
    """Class to run a model based on supplied cluster information"""

    def __init__(self,
                 cluster,
                 template,
                 model_options,
                 solver='cbc',
                 log=False):
        self.cluster = cluster
        self.model_options = model_options
        if self.cluster:
            # Force unserved constraint for cluster run
            self.model_options = model_options._replace(unslim=True)
        self.template = template
        self.solver = solver
        self.log = log
        # Internal variables to class
        self.data = None
        self.tmpdir = tempfile.mkdtemp()

    def _gen_dat_files(self):
        # generate a 1 week timestamp range for each cluster member
        # and produce a data control file for each member
        for k in range(self.cluster.max_d):
            date1 = self.cluster.Xcluster['date'][k]
            date2 = date1 + datetime.timedelta(
                days=self.cluster.pdays, seconds=-1)
            sdate1 = "'" + str(date1) + "'"
            sdate2 = "'" + str(date2) + "'\n"
            drange = "WHERE timestamp BETWEEN " + sdate1 + " AND " + sdate2
            with open(self.template, 'rt') as fin:
                with open(self.tmpdir + '/S' + str(k + 1) + '.dat', 'w') as fo:
                    for line in fin:
                        if 'WHERE timestamp BETWEEN' in line:
                            line = drange
                        fo.write(line)

    def _gen_scen_struct(self):
        setNodes = 'set Nodes:= Root '
        paramNodeStage = 'param NodeStage:= Root FS '
        setChildRoot = 'set Children[Root]:= '
        parCondProb = 'param ConditionalProbability := Root 1.0 '
        setScenarios = 'set Scenarios := '
        paramScenLeaf = 'param ScenarioLeafNode := '
        for k in range(self.cluster.max_d):
            Scenario = 'S' + str(k + 1)
            Node = Scenario + 'Node '
            setNodes += Node
            paramNodeStage += Node + 'SS '
            setChildRoot += Node
            parCondProb += Node + str(self.cluster.Xcluster['weight'][k]) + ' '
            setScenarios += Scenario + ' '
            paramScenLeaf += Scenario + ' ' + Node

        setNodes += ';'
        paramNodeStage += ';'
        setChildRoot += ';'
        parCondProb += ';'
        setScenarios += ';'
        paramScenLeaf += ';'
        template = {
            'control file': '# generated template DO NOT EDIT',
            'stages': 'set Stages := FS SS;',
            'setNodesrep': setNodes,
            'paramNodesrep': paramNodeStage,
            'setChildRootrep': setChildRoot,
            'parCondProbrep': parCondProb,
            'setScenariosrep': setScenarios,
            'paramScenLeafrep': paramScenLeaf,
            'setstagevars1':
            'set StageVariables[FS] := gen_cap_new[*,*] stor_cap_new[*,*] hyb_cap_new[*,*] intercon_cap_new[*,*] gen_cap_ret[*,*];',
            'setstagevars2':
            'set StageVariables[SS] := gen_cap_new[*,*] stor_cap_new[*,*] hyb_cap_new[*,*] intercon_cap_new[*,*] gen_cap_ret[*,*];',
            'stagecost': 'param StageCost := FS FSCost SS SSCost;',
        }
        with open(self.tmpdir + '/ScenarioStructure.dat', 'wt') as fo:
            for t in template:
                line = template[t] + '\n\n'
                fo.write(line)

    def _gen_ref_model(self):
        # Not pretty but it will do
        with open(self.tmpdir + '/ReferenceModel.py', 'wt') as fo:
            refmodel = "'''Temporary openCEM model instance for runef simulations'''\n"
            refmodel += "from cemo.model import CreateModel, model_options\n"
            refmodel += "options = " + str(self.model_options) + " \n"
            refmodel += "model = CreateModel('openCEM', options).create_model()\n"
            fo.write(refmodel)

    def run_cluster(self):
        '''Create a stochastic program to run in pyomo runef based on demand
         clustering. The objective is to find a set of capacity expansion
         decisions that work across all clusters'''
        self._gen_dat_files()  # generate .dat files for cluster members
        self._gen_scen_struct()  # generate .dat file for runef tree
        self._gen_ref_model()  # generate reference model for runef
        cmd = [
            "runef", "-m", self.tmpdir, "-s", self.tmpdir, "--solve",
            "--solver=" + self.solver,
            "--solution-writer=pyomo.pysp.plugins.jsonsolutionwriter"
        ]
        stdout = subprocess.DEVNULL

        if self.log:
            cmd.append("--output-solver-log")
            cmd.append("--traceback")
            stdout = subprocess.PIPE

        proc = subprocess.run(cmd, stdout=stdout)
        if proc.returncode == 0:
            shutil.move("ef_solution.json", self.tmpdir)
        else:
            sys.exit(proc.returncode)

        with open(self.tmpdir + '/ef_solution.json') as f:
            clusterresult = json.load(f)

        self.data = clusterresult['node solutions']['Root']['variables']
        return self
