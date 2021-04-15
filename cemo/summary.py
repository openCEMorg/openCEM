"""Data Summary Class for openCEM"""
import pandas as pd
from pathlib import Path

CAPCOLS = ['cap_op', 'cap_new', 'cap_exo', 'cap_ret', 'cap_ret_exo']
REGIONCOLS_ZT = ['srmc', 'unserved']
REGIONCOLS_RT = ['region_net_demand']
EMITCOLS_ZTT = ['disp', 'disp_com', 'disp_com_p']
EMITCOLS_ZT = ['cost_fuel', 'fuel_heat_rate', ]
EMITCOLS_T = ['gen_com_mincap', 'gen_com_penalty', 'gen_com_effrate', 'fuel_emit_rate']
COSTCOLS_ZT = ['cost_build']
COSTCOLS_Z = ['cost_cap_carry_forward']
COSTCOLS_T = ['fixed_charge_rate', 'opex_fom', 'opex_vom', 'cost_retire']
INTERCONCAPCOLS = ['intercon_cap_new', 'intercon_cap_exo', 'intercon_cap_op', 'cost_intercon_build']
INTERCONDISPCOLS = ['intercon_disp']
REGION_IN_ZONE = {1: 2, 2: 2, 3: 2, 4: 2, 5: 1, 6: 1, 7: 1,
                  8: 1, 9: 5, 10: 5, 11: 5, 12: 5, 13: 3, 14: 3, 15: 3, 16: 4}


class BaseSummary():
    """Base Class for Summary"""

    def __init__(self, datasource, YEARS, cache=True, save=True):
        self.years = YEARS
        self.scen = Path(datasource)
        self.cache = cache
        self.save = save
        self.check_cache()

    def _load_data(self, VAR):
        for idx, year in enumerate(self.years):
            if idx == 0:
                #print("Loading %s %s" % (self.scen, VAR))
                data = pd.DataFrame()
            # Load a bunch of data into a dictionary for easy access
            path = self.scen / Path(str(year)) / VAR
            tmp = pd.read_parquet(path)
            tmp['year'] = year
            data = data.append(tmp)
        return data

    def _misc(self):
        """Load miscelaneous"""
        self.misc = self._load_data('misc.parquet')

    def check_cache(self):
        pass

    def _append_region(self):
        """Append region to zone to dataframes in order to filter by region"""
        self.summary['region'] = self.summary.zone.apply(lambda x: REGION_IN_ZONE[x])

    def get_summary(self):
        return self.summary


class TransSummary(BaseSummary):
    """Process Transmission stats"""

    def check_cache(self):
        if self.cache:
            try:
                self.summary = pd.read_parquet(self.scen/"trans_summary.parquet")
                if set(self.summary.year.unique()) != set(self.years):
                    #print("Not equal!")
                    raise Exception
            except Exception as e:
                print(e)
                self.process_data()
        else:
            self.process_data()
        if self.save:
            self.save_cache()

    def save_cache(self):
        self.summary.to_parquet(self.scen/"trans_summary.parquet")

    def process_data(self):
        self._misc()
        self._trans_cap()
        self._trans_flow()
        self._intercon_costs()
        self._append_region()

    def _trans_cap(self):
        for idx, var in enumerate(INTERCONCAPCOLS):
            if idx == 0:
                self.summary = self._load_data(var)
            else:
                self.summary = self.summary.merge(
                    self._load_data(var), on=['zone_source', 'zone_dest', 'year'], how='outer')

    def _trans_flow(self):
        for idx, var in enumerate(INTERCONDISPCOLS):
            if idx == 0:
                flowdata = self._load_data(var)
            else:
                flowdata = flowdata.merge(
                    self._load_data(var),
                    on=['zone_source', 'zone_dest', 'year', 'time'],
                    how='outer')
        flowdata = flowdata.groupby(['zone_source', 'zone_dest', 'year']).sum().reset_index()
        self.summary = self.summary.merge(
            flowdata, on=['zone_source', 'zone_dest', 'year'])

    def _intercon_costs(self):
        self.summary = self.summary.merge(
            self.misc[['year', 'intercon_fixed_charge_rate']], on=['year'], how='outer')
        self.summary = self.summary.merge(
            self.misc[['year', 'cost_trans']], on=['year'], how='outer')

        self.summary['build_intercon_cost'] = self.summary.cost_intercon_build * \
            (self.summary.intercon_cap_new+self.summary.intercon_cap_exo) * \
            self.summary.intercon_fixed_charge_rate
        self.summary['flow_intercon_cost'] = self.summary.intercon_disp * \
            self.summary.cost_trans

    def _append_region(self):
        """Append region to zone to dataframes in order to filter by region"""
        self.summary['region'] = self.summary.zone_source.apply(lambda x: REGION_IN_ZONE[x])

    def summary(self):
        return self.summary


class CapSummary(BaseSummary):
    def check_cache(self):
        if self.cache:
            try:
                self.summary = pd.read_parquet(self.scen/"cap_summary.parquet")
                if set(self.summary.year.unique()) != set(self.years):
                    #print("Not equal!")
                    raise Exception
            except Exception as e:
                print(e)
                self.process_data()
        else:
            self.process_data()
        if self.save:
            self.save_cache()

    def save_cache(self):
        self.summary.to_parquet(self.scen/"cap_summary.parquet")

    def process_data(self):
        self._capacity()
        self._fuel_and_emissions()
        self._cap_costs()
        self._misc()
        self._append_region()

    def _capacity(self):
        for idx, var in enumerate(CAPCOLS):
            if idx == 0:
                self.summary = self._load_data(var)
            else:
                self.summary = self.summary.merge(self._load_data(
                    var), on=['zone', 'tech', 'year'], how='outer')

    def _fuel_and_emissions(self):
        '''Process dispatch, fuel usage and emissions'''
        for idx, var in enumerate(EMITCOLS_ZTT):
            if idx == 0:
                nfuel = self._load_data(var)
            else:
                nfuel = nfuel.merge(self._load_data(var), on=[
                                    'zone', 'tech', 'year', 'time'], how='outer')
        for var in EMITCOLS_ZT:
            nfuel = nfuel.merge(self._load_data(var), on=['zone', 'tech', 'year'], how='outer')
        for var in EMITCOLS_T:
            nfuel = nfuel.merge(self._load_data(var), on=['tech', 'year'], how='outer')
        nfuel['penalty'] = nfuel.cost_fuel * nfuel.gen_com_penalty * nfuel.disp_com_p
        nfuel['inflex_cost'] = nfuel.cost_fuel * (nfuel.gen_com_mincap
                                                  * nfuel.disp_com
                                                  * nfuel.fuel_heat_rate
                                                  / nfuel.gen_com_effrate
                                                  + (nfuel.disp
                                                     - nfuel.gen_com_mincap
                                                     * nfuel.disp_com)
                                                  * nfuel.fuel_heat_rate
                                                  * (1 - nfuel.gen_com_mincap
                                                     / nfuel.gen_com_effrate)
                                                  / (1 - nfuel.gen_com_mincap)) + nfuel.penalty
        nfuel['flex_cost'] = nfuel.cost_fuel * nfuel.fuel_heat_rate * nfuel.disp
        nfuel['fuel_cost'] = nfuel[['inflex_cost', 'flex_cost']].max(axis=1)
        nfuel['emissions'] = nfuel.fuel_cost / \
            (nfuel.fuel_heat_rate+1e-12)/(nfuel.cost_fuel+1e-12)*nfuel.fuel_emit_rate/1e9
        nfuel = nfuel.groupby(['zone', 'tech', 'year']).sum()
        nfuel = nfuel.reset_index()

        self.summary = self.summary.merge(
            nfuel[['zone', 'tech', 'year', 'disp', 'fuel_cost', 'emissions']],
            on=['zone', 'tech', 'year'], how='outer')

    def _cap_costs(self):
        """Add cost colums for all sorts of stuff"""
        for idx, var in enumerate(COSTCOLS_ZT):
            if idx == 0:
                costs = self._load_data(var)
            else:
                costs = costs.merge(self._load_data(var), on=[
                                    'zone', 'tech', 'year'], how='outer')
        for var in COSTCOLS_T:
            costs = costs.merge(self._load_data(var), on=['tech', 'year'], how='outer')
        self.summary = self.summary.merge(costs, on=['zone', 'tech', 'year'], how='outer')
        self.summary['build_cost'] = self.summary.cost_build * 1000 * \
            self.summary.fixed_charge_rate*(self.summary.cap_new+self.summary.cap_exo)
        self.summary['retire_cost'] = self.summary.cost_retire * \
            (self.summary.cap_ret+self.summary.cap_ret_exo)
        self.summary['fom_cost'] = self.summary.opex_fom * 1000 * self.summary.cap_op
        self.summary['vom_cost'] = self.summary.opex_vom * self.summary.disp
        self.summary = self.summary[self.summary.cap_op > 0]


class ZoneSummary(BaseSummary):
    def check_cache(self):
        if self.cache:
            try:
                self.summary = pd.read_parquet(self.scen/"zone_summary.parquet")
                if set(self.summary.year.unique()) != set(self.years):
                    #print("Not equal!")
                    raise Exception
            except Exception as e:
                print(e)
                self.process_data()
        else:
            self.process_data()
        if self.save:
            self.save_cache()

    def save_cache(self):
        self.summary.to_parquet(self.scen/"zone_summary.parquet")

    def process_data(self):
        self._carry_fwd_costs()
        self._append_region()

    def _carry_fwd_costs(self):
        """Carryfwd costs are per zone only"""
        for idx, var in enumerate(COSTCOLS_Z):
            if idx == 0:
                costs = self._load_data(var)
            else:
                costs = costs.merge(self._load_dat(var), on=['zone', 'year'], how='outer')
        self.summary = costs


class RegSummary(BaseSummary):
    def check_cache(self):
        if self.cache:
            try:
                self.summary = pd.read_parquet(self.scen/"dual_summary.parquet")
                if set(self.summary.year.unique()) != set(self.years):
                    #print("Not equal!")
                    raise Exception
            except Exception as e:
                print(e)
                self.process_data()
        else:
            self.process_data()

        if self.save:
            self.save_cache()

    def save_cache(self):
        self.summary.to_parquet(self.scen/"dual_summary.parquet")

    def process_data(self):
        self._duals()
        self._demand()

    def _duals(self):
        """SRMC as the max per """
        for idx, var in enumerate(REGIONCOLS_ZT):
            if idx == 0:
                duals = self._load_data(var)
            else:
                duals = duals.merge(self._load_data(var), on=['zone', 'year', 'time'], how='outer')
        duals['region'] = duals.zone.apply(lambda x: REGION_IN_ZONE[x])

        self.summary = duals[['year', 'region', 'time', 'srmc']].groupby(['year', 'region', 'time']
                                                                         ).max().groupby(['year', 'region']).mean()
        self.summary['srmc_std'] = duals[['year', 'region', 'time', 'srmc']].groupby(['year', 'region', 'time']
                                                                                     ).max().groupby(['year', 'region']).std()
        self.summary['unserved'] = duals[['year', 'region', 'time', 'unserved']].groupby(['year', 'region', 'time']
                                                                                         ).max().groupby(['year', 'region']).sum()
        self.summary = self.summary.reset_index()

    def _demand(self):
        for idx, var in enumerate(REGIONCOLS_RT):
            if idx == 0:
                region = self._load_data(var)
            else:
                region = region.merge(self._load_data(var), on=[
                                      'region', 'year', 'time'], how='outer')
        region = region.groupby(['year', 'region']).sum()
        self.summary = self.summary.merge(region, on=['year', 'region'])


class Summary(BaseSummary):
    def check_cache(self):
        self.cap_summary = CapSummary(self.scen, self.years, self.cache).get_summary()
        self.zone_summary = ZoneSummary(self.scen, self.years, self.cache).get_summary()
        self.trans_summary = TransSummary(self.scen, self.years, self.cache).get_summary()
        self.region_summary = RegSummary(self.scen, self.years, self.cache).get_summary()
        self._misc()

    def _market_stats():
        """Process USE, wholesale price and wholesale price spread"""
        pass

    def cdu(self, regions=[1, 2, 3, 4, 5]):
        """Return Capacity Dispatch Utilisation table"""
        cdu = self.cap_summary[['region', 'zone', 'tech', 'year', 'cap_op', 'disp', 'emissions']]
        cdu = cdu[cdu.region.isin(regions)]
        cdu = cdu.groupby(['year', 'zone', 'tech']).sum()
        cdu['cap_factor'] = cdu.disp/(cdu.cap_op*8760)*100
        return cdu

    def cost(self, regions=[1, 2, 3, 4, 5]):
        cost = self.cap_summary[['zone', 'tech', 'year',
                                 'build_cost', 'fom_cost', 'vom_cost',
                                 'fuel_cost', 'retire_cost', 'emissions']]
        market = self.region_summary[['region', 'year', 'srmc', 'srmc_std', 'unserved', 'region_net_demand']].groupby([
                                                                                     'year', 'region']).sum().reset_index()

        cost = cost.groupby(['year', 'zone']).sum()
        cost = cost.merge(self.zone_summary, on=['zone', 'year'])
        trans_cost = self.trans_summary.groupby(
            ['year', 'zone_source']).sum().reset_index()
        trans_cost = trans_cost[['year', 'zone_source',
                                 'build_intercon_cost', 'flow_intercon_cost']]
        trans_cost = trans_cost.rename(columns={'zone_source': 'zone'})
        cost = cost.merge(trans_cost, on=['year', 'zone'])

        cost = cost.merge(self.misc[['year', 'cost_emit']], on='year')
        market = market.merge(self.misc[['year', 'cost_unserved']],
                              on='year').set_index(['year', 'region'])
        cost['emit_cost'] = cost.emissions*cost.cost_emit
        cost['lrmc'] = cost.build_cost+cost.fom_cost+cost.retire_cost + \
            cost.cost_cap_carry_forward+cost.build_intercon_cost
        cost = cost.groupby(['year', 'region']).sum()
        cost['unserved_cost'] = market.cost_unserved*market.unserved
        cost['total'] = cost.lrmc+cost.vom_cost + cost.fuel_cost + cost.flow_intercon_cost
        cost['wholesale'] = (cost.lrmc/market.region_net_demand+market.srmc)
        cost['wholesale_spread'] = market.srmc_std
        return cost[['total', 'build_cost', 'cost_cap_carry_forward', 'fom_cost', 'vom_cost',
                     'fuel_cost', 'emit_cost', 'retire_cost',
                     'build_intercon_cost', 'flow_intercon_cost', 'unserved_cost',
                     'wholesale', 'wholesale_spread']]

    def get_summary(self):
        return [self.cdu(), self.cost()]
