"""openCEM model structure"""
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "GPLv3"
__version__ = "0.9.2"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"
__status__ = "Development"

from pyomo.environ import (AbstractModel, BuildAction, Constraint, Expression,
                           NonNegativeReals, Objective, Param, Set, Suffix,
                           Var)
import cemo.const
from cemo.initialisers import (init_cap_factor, init_cost_retire,
                               init_default_fuel_emit_rate,
                               init_default_fuel_price, init_default_heat_rate,
                               init_default_lifetime, init_fcr,
                               init_gen_build_limit, init_hyb_charge_hours,
                               init_hyb_col_mult, init_intercon_cap_initial,
                               init_intercon_fcr, init_intercon_loss_factor,
                               init_intercons_in_zones, init_stor_charge_hours,
                               init_stor_rt_eff, init_year_correction_factor,
                               init_zone_demand_factors, init_zones_in_regions)
from cemo.rules import (ScanForHybridperZone, ScanForStorageperZone,
                        ScanForTechperZone, ScanForZoneperRegion,
                        build_intercon_per_zone, con_caplim, con_chargelim,
                        con_chargelimhy, con_committed_cap, con_dischargelim,
                        con_dischargelimhy, con_disp_ramp_down,
                        con_disp_ramp_up, con_emissions, con_gen_cap,
                        con_hyb_cap, con_hybcharge, con_intercon_cap,
                        con_ldbal, con_max_mhw_per_zone, con_max_mwh_nem_wide,
                        con_max_trans, con_maxcap, con_maxcharge,
                        con_maxchargehy, con_min_load_commit,
                        con_nem_disp_ratio, con_nem_re_disp_ratio,
                        con_nem_ret_gwh, con_nem_ret_ratio,
                        con_ramp_down_uptime, con_region_ret_ratio,
                        con_slackbuild, con_slackretire, con_stor_cap,
                        con_storcharge, con_uns, con_uptime_commitment,
                        obj_cost)


def create_model(namestr,
                 unslim=False,
                 emitlimit=False,
                 nem_ret_ratio=False,
                 nem_ret_gwh=False,
                 region_ret_ratio=False,
                 nem_disp_ratio=False,
                 nem_re_disp_ratio=False):
    """Creates an instance of the pyomo definition of openCEM"""
    m = AbstractModel(name=namestr)
    # Sets
    m.regions = Set(initialize=cemo.const.REGION.keys())  # Set of NEM regions
    m.zones = Set(
        initialize=cemo.const.ZONE.keys())  # Set of NTNDP planning zones
    m.all_tech = Set(
        initialize=cemo.const.ALL_TECH)  # Set of generation technologies
    # set of fuel based gen technologies
    m.fuel_gen_tech = Set(initialize=cemo.const.FUEL_TECH) & m.all_tech
    # set of gen techs that obey linearised unit commitment constraints
    m.commit_gen_tech = Set(initialize=cemo.const.COMMIT_TECH) & m.all_tech
    # set of retireable technologies
    m.retire_gen_tech = Set(initialize=cemo.const.RETIRE_TECH) & m.all_tech
    # set of retireable technologies
    m.nobuild_gen_tech = Set(initialize=cemo.const.NOBUILD_TECH) & m.all_tech
    # Set of storage technologies
    m.stor_tech = Set(initialize=cemo.const.STOR_TECH) & m.all_tech
    # set of hybrid (gen+storage) technologies
    m.hyb_tech = Set(initialize=cemo.const.HYB_TECH) & m.all_tech
    # Set of dispatch intervals
    m.t = Set(ordered=True)

    # Sparse set of zones per region
    m.zones_in_regions = Set(dimen=2, initialize=init_zones_in_regions)
    # Set listing technologies avaialable per zone (like a sparsity pattern)
    m.gen_tech_in_zones = Set(dimen=2)
    # Retirable technologies avaialable per zone (like a sparsity pattern)
    m.retire_gen_tech_in_zones = Set(dimen=2)
    # Fuel/emmitting technologies avaialable per zone (like a sparsity pattern)
    m.fuel_gen_tech_in_zones = Set(dimen=2)
    # Fuel/emmitting technologies avaialable per zone (like a sparsity pattern)
    m.commit_gen_tech_in_zones = Set(dimen=2)
    # Renewable technologies avaialable per zone (like a sparsity pattern)
    m.re_gen_tech_in_zones = Set(dimen=2)
    # Dispatchable technologies avaialable per zone (like a sparsity pattern)
    m.disp_gen_tech_in_zones = Set(dimen=2)
    # Renewable Dispatchable technologies avaialable per zone (like a sparsity pattern)
    m.re_disp_gen_tech_in_zones = Set(dimen=2)
    # Set listing storage avaialable per zone (like a sparsity pattern)
    m.hyb_tech_in_zones = Set(dimen=2)
    # Set listing storage avaialable per zone (like a sparsity pattern)
    m.stor_tech_in_zones = Set(dimen=2)
    # Set listing transmission lines to other regions in each region
    m.intercons_in_zones = Set(dimen=2, initialize=init_intercons_in_zones)

    # sparse sets built by build actions
    # Returns a list of planning zones for each region in R
    m.zones_per_region = Set(m.regions, within=m.zones, initialize=[])
    # Returns a tuple with generating techs in each zone
    m.gen_tech_per_zone = Set(m.zones, within=m.all_tech, initialize=[])
    # Returns a tuple with emitting techs in each zone
    m.fuel_gen_tech_per_zone = Set(m.zones, within=m.all_tech, initialize=[])
    # tuple for techs that obey linearised unit commitment constraints
    m.commit_gen_tech_per_zone = Set(m.zones, within=m.all_tech, initialize=[])
    m.re_gen_tech_per_zone = Set(m.zones, within=m.all_tech, initialize=[])
    m.disp_gen_tech_per_zone = Set(m.zones, within=m.all_tech, initialize=[])
    m.re_disp_gen_tech_per_zone = Set(
        m.zones, within=m.all_tech, initialize=[])
    # Returns a tuple with retirable techs in each zone
    m.retire_gen_tech_per_zone = Set(m.zones, within=m.all_tech, initialize=[])
    # Returns a tuple with storage techs in each zone
    m.stor_tech_per_zone = Set(m.zones, within=m.stor_tech, initialize=[])
    # Returns a tuple with emitting techs in each zone
    m.hyb_tech_per_zone = Set(m.zones, within=m.all_tech, initialize=[])
    # returns a tuple with transmission links in each region
    m.intercon_per_zone = Set(m.zones, initialize=[])

    # @@ Build actions
    # Scan TechinZones and populate ?_gen_tech_per_zone
    m.TpZ_build = BuildAction(rule=ScanForTechperZone)
    # Scan HybTechinZones and populate hyb_tech_per_zone
    m.HpZ_build = BuildAction(rule=ScanForHybridperZone)
    # Scan ZinR and populate ZperR
    m.ZpR_build = BuildAction(rule=ScanForZoneperRegion)
    # Scan TransLines and populate intercon_per_zone
    m.intercon_build = BuildAction(rule=build_intercon_per_zone)
    # Scan StorinZones and populate stor_tech_per_zone
    m.SpZ_build = BuildAction(rule=ScanForStorageperZone)

    # @@ Parameters
    # Capital costs generators
    # Build costs for generators
    m.cost_gen_build = Param(m.gen_tech_in_zones, default=9e7)
    m.cost_stor_build = Param(m.stor_tech_in_zones)  # Capital costs storage
    m.cost_hyb_build = Param(m.hyb_tech_in_zones)  # Capital costs hybrid
    m.cost_intercon_build = Param(m.intercons_in_zones, default=2300)  # Capital costs $/MW/km trans

    m.cost_fuel = Param(
        m.fuel_gen_tech_in_zones,
        initialize=init_default_fuel_price)  # Fuel cost

    # Fixed operating costs generators
    m.cost_gen_fom = Param(m.all_tech)
    # Variable operating costs generators
    m.cost_gen_vom = Param(m.all_tech)
    # Fixed operating costs storage
    m.cost_stor_fom = Param(m.stor_tech)
    # Variable operating costs storage
    m.cost_stor_vom = Param(m.stor_tech)
    # Fixed operating costs hybrid
    m.cost_hyb_fom = Param(m.hyb_tech)
    # Variable operating costs hybrid
    m.cost_hyb_vom = Param(m.hyb_tech)
    # Technology lifetime in years
    m.all_tech_lifetime = Param(m.all_tech, initialize=init_default_lifetime)
    # Project discount rate
    m.all_tech_discount_rate = Param(default=0.05)

    # Generator tech fixed charge rate
    m.fixed_charge_rate = Param(m.all_tech, initialize=init_fcr)
    # Transmission tech fixed charge rate
    m.intercon_fixed_charge_rate = Param(initialize=init_intercon_fcr)
    # Per year cost adjustment for sims shorter than 1 year of dispatch
    m.year_correction_factor = Param(initialize=init_year_correction_factor)

    m.cost_retire = Param(m.retire_gen_tech, initialize=init_cost_retire)
    m.cost_unserved = Param(
        initialize=cemo.const.
        DEFAULT_COSTS["unserved"])  # cost of unserved power
    # cost in $/kg of total emissions
    m.cost_emit = Param(initialize=cemo.const.DEFAULT_COSTS["emit"])
    m.cost_trans = Param(
        initialize=cemo.const.DEFAULT_COSTS["trans"])  # cost of transmission

    # Round trip efficiency of storage technology
    m.stor_rt_eff = Param(m.stor_tech, initialize=init_stor_rt_eff)
    # Number of hours of storage technology
    m.stor_charge_hours = Param(m.stor_tech, initialize=init_stor_charge_hours)

    # Collector multiple of hybrid technology
    m.hyb_col_mult = Param(m.hyb_tech, initialize=init_hyb_col_mult)
    # Number of hours of storage technology
    m.hyb_charge_hours = Param(m.hyb_tech, initialize=init_hyb_charge_hours)

    m.fuel_heat_rate = Param(
        m.fuel_gen_tech_in_zones, initialize=init_default_heat_rate)
    # Emission rates
    m.fuel_emit_rate = Param(
        m.fuel_gen_tech, initialize=init_default_fuel_emit_rate)
    # proportioning factors for notional interconnectors
    m.intercon_loss_factor = Param(
        m.intercons_in_zones, initialize=init_intercon_loss_factor)

    m.gen_cap_factor = Param(
        m.gen_tech_in_zones, m.t,
        initialize=init_cap_factor)  # Capacity factors for generators
    m.hyb_cap_factor = Param(
        m.hyb_tech_in_zones, m.t,
        initialize=init_cap_factor)  # Capacity factors for generators

    # Maximum capacity per generating technology per zone
    m.gen_build_limit = Param(
        m.gen_tech_in_zones, initialize=init_gen_build_limit)
    m.gen_cap_initial = Param(
        m.gen_tech_in_zones, default=0)  # operating capacity
    m.stor_cap_initial = Param(
        m.stor_tech_in_zones, default=0)  # operating capacity
    m.hyb_cap_initial = Param(
        m.hyb_tech_in_zones, default=0)  # operating capacity
    m.intercon_cap_initial = Param(
        m.intercons_in_zones, initialize=init_intercon_cap_initial)  # operating capacity
    # exogenous new capacity
    m.gen_cap_exo = Param(m.gen_tech_in_zones, default=0)
    # exogenous new storage capacity
    m.stor_cap_exo = Param(m.stor_tech_in_zones, default=0)
    # exogenous new hybrid capacity
    m.hyb_cap_exo = Param(m.hyb_tech_in_zones, default=0)
    # exogenous transmission capacity
    m.intercon_cap_exo = Param(m.intercons_in_zones, default=0)
    m.ret_gen_cap_exo = Param(m.retire_gen_tech_in_zones, default=0)
    # Net Electrical load (may include rooftop and EV)
    m.region_net_demand = Param(m.regions, m.t)
    # Zone load distribution factors as a pct of region demand
    m.zone_demand_factor = Param(m.zones, m.t, initialize=init_zone_demand_factors)

    # carry forward capital costs
    m.cost_cap_carry_forward = Param(m.zones, default=0)

    # @@ Variables
    m.gen_cap_new = Var(
        m.gen_tech_in_zones, within=NonNegativeReals)  # New capacity
    m.gen_cap_op = Var(
        m.gen_tech_in_zones,
        within=NonNegativeReals)  # Total generation capacity
    m.stor_cap_new = Var(
        m.stor_tech_in_zones, within=NonNegativeReals)  # New storage capacity
    m.stor_cap_op = Var(
        m.stor_tech_in_zones,
        within=NonNegativeReals)  # Total storage capacity
    m.hyb_cap_new = Var(m.hyb_tech_in_zones, within=NonNegativeReals)
    m.hyb_cap_op = Var(m.hyb_tech_in_zones, within=NonNegativeReals)
    m.intercon_cap_new = Var(m.intercons_in_zones, within=NonNegativeReals)
    m.intercon_cap_op = Var(m.intercons_in_zones, within=NonNegativeReals)
    m.gen_cap_ret = Var(
        m.retire_gen_tech_in_zones,
        within=NonNegativeReals)  # retireable capacity
    m.gen_cap_ret_neg = Var(
        m.retire_gen_tech_in_zones, within=NonNegativeReals
    )  # slack for exogenous retires beyond gen_op_cap
    m.gen_cap_exo_neg = Var(
        m.gen_tech_in_zones, within=NonNegativeReals
    )  # slack for exogenous builds exceeding gen_build_limit
    m.gen_disp = Var(
        m.gen_tech_in_zones, m.t, within=NonNegativeReals)  # dispatched power
    # Variables for committed power constraints
    m.gen_disp_com = Var(m.commit_gen_tech_in_zones, m.t, within=NonNegativeReals)
    m.gen_disp_com_p = Var(m.commit_gen_tech_in_zones, m.t, within=NonNegativeReals)
    m.gen_disp_com_m = Var(m.commit_gen_tech_in_zones, m.t, within=NonNegativeReals)
    m.gen_disp_com_s = Var(m.commit_gen_tech_in_zones, m.t, within=NonNegativeReals)

    m.stor_disp = Var(
        m.stor_tech_in_zones, m.t,
        within=NonNegativeReals)  # dispatched power from storage

    m.stor_charge = Var(
        m.stor_tech_in_zones, m.t,
        within=NonNegativeReals)  # power to charge storage

    m.hyb_disp = Var(
        m.hyb_tech_in_zones, m.t,
        within=NonNegativeReals)  # dispatched power from hybrid

    m.hyb_charge = Var(
        m.hyb_tech_in_zones, m.t,
        within=NonNegativeReals)  # charging power from hybrid

    m.stor_level = Var(
        m.stor_tech_in_zones, m.t,
        within=NonNegativeReals)  # Charge level for storage

    m.hyb_level = Var(
        m.hyb_tech_in_zones, m.t,
        within=NonNegativeReals)  # Charge level for storage

    m.unserved = Var(m.zones, m.t, within=NonNegativeReals)  # unserved power
    m.surplus = Var(
        m.zones, m.t, within=NonNegativeReals)  # surplus power (if any)

    # Interconnector flow
    m.intercon_disp = Var(m.intercons_in_zones, m.t, within=NonNegativeReals)

    # @@ Constraints
    # Transmission limits
    m.con_max_trans = Constraint(m.intercons_in_zones, m.t, rule=con_max_trans)
    # Transmission capacity balance
    m.con_intercon_cap = Constraint(m.intercons_in_zones, rule=con_intercon_cap)
    # Load balance
    m.ldbal = Constraint(m.zones, m.t, rule=con_ldbal)
    # Dispatch to be within capacity, RE have variable capacity factors
    m.caplim = Constraint(m.gen_tech_in_zones, m.t, rule=con_caplim)
    # Limit maximum capacity to be built in each region and each technology
    m.maxcap = Constraint(m.gen_tech_in_zones, rule=con_maxcap)
    # gen_cap_op in existing period is previous gen_cap_op plus gen_cap_new
    m.con_gen_cap = Constraint(m.gen_tech_in_zones, rule=con_gen_cap)
    # MaxMWh limit
    m.con_max_mwh_per_zone = Constraint(m.gen_tech_in_zones, rule=con_max_mhw_per_zone)
    # MaxMWh limit (currently only for hydro)
    m.max_mwh_as_cap_factor = Constraint(
        m.gen_tech_in_zones, rule=con_max_mwh_as_cap_factor)
    # Slack constraint on exogenous retirement to prevent it to go nevative
    m.con_slackretire = Constraint(
        m.retire_gen_tech_in_zones, rule=con_slackretire)
    # Slack constraint on exogenous retirement to prevent it to go nevative
    m.con_slackbuild = Constraint(m.gen_tech_in_zones, rule=con_slackbuild)

    # linearised unit commitment constraints
    m.con_min_load_commit = Constraint(
        m.commit_gen_tech_in_zones, m.t, rule=con_min_load_commit)
    m.con_disp_ramp_down = Constraint(
        m.commit_gen_tech_in_zones, m.t, rule=con_disp_ramp_down)
    m.con_disp_ramp_up = Constraint(
        m.commit_gen_tech_in_zones, m.t, rule=con_disp_ramp_up)
    m.con_ramp_down_uptime = Constraint(
        m.commit_gen_tech_in_zones, m.t, rule=con_ramp_down_uptime)
    m.con_uptime_commitment = Constraint(
        m.commit_gen_tech_in_zones, m.t, rule=con_uptime_commitment)
    m.con_committed_cap = Constraint(m.commit_gen_tech_in_zones, m.t, rule=con_committed_cap)
    # Hard constraint on unserved energy
    if unslim:
        m.con_uns = Constraint(m.regions, rule=con_uns)
    # Emmissions constraint
    if emitlimit:
        m.con_emissions = Constraint(rule=con_emissions)
        # maximum kg/MWh rate of total emissions
        m.nem_year_emit_limit = Param()
    # NEM wide RET constraint as a ratio
    if nem_ret_ratio:
        # NEM wide renewable energy target for current year
        m.nem_ret_ratio = Param(default=0)
        # NEM wide renewable energy constraint
        m.con_nem_ret_ratio = Constraint(rule=con_nem_ret_ratio)


# NEM wide RET constraint as a ratio
    if nem_ret_gwh:
        # NEM wide renewable energy target for current year
        m.nem_ret_gwh = Param(default=0)
        # NEM wide renewable energy constraint
        m.con_nem_ret_gwh = Constraint(rule=con_nem_ret_gwh)

    if region_ret_ratio:
        # Regional RET targets for current year
        m.region_ret_ratio = Param(m.regions, default=0)
        # Regional RET constraint
        m.con_region_ret = Constraint(m.regions, rule=con_region_ret_ratio)

    if nem_disp_ratio:
        # NEM wide minimum hour by our generation from "dispatchable" sources
        m.nem_disp_ratio = Param(default=0)
        # NEM wide minimum hourly dispatch from dispatchable sources constraint
        m.con_nem_disp_ratio = Constraint(
            m.regions, m.t, rule=con_nem_disp_ratio)

    if nem_re_disp_ratio:
        # NEM wide minimum hour by our generation from "dispatchable" sources
        m.nem_re_disp_ratio = Param(default=0)
        # NEM wide minimum hourly dispatch from dispatchable sources constraint
        m.con_nem_re_disp_ratio = Constraint(
            m.regions, m.t, rule=con_nem_re_disp_ratio)

    # Storage charge/discharge dynamic
    m.StCharDis = Constraint(m.stor_tech_in_zones, m.t, rule=con_storcharge)
    # Maxiumum rate of storage charge
    m.Chargelimit = Constraint(m.stor_tech_in_zones, m.t, rule=con_chargelim)
    # Maxiumum rate of storage discharge
    m.Dishchargelimit = Constraint(
        m.stor_tech_in_zones, m.t, rule=con_dischargelim)
    # Maxiumum charge capacity of storage
    m.MaxCharge = Constraint(m.stor_tech_in_zones, m.t, rule=con_maxcharge)
    # StCap in existing period is previous stor_cap_op plus stor_cap_new
    m.con_stor_cap = Constraint(m.stor_tech_in_zones, rule=con_stor_cap)

    # Hybrid charge/discharge dynamic
    m.HybCharDis = Constraint(m.hyb_tech_in_zones, m.t, rule=con_hybcharge)
    # Maxiumum rate of hybrid storage discharge
    m.Chargelimithy = Constraint(
        m.hyb_tech_in_zones, m.t, rule=con_chargelimhy)
    # Maxiumum rate of hybrid storage discharge
    m.Dishchargelimithy = Constraint(
        m.hyb_tech_in_zones, m.t, rule=con_dischargelimhy)
    # Maxiumum charge capacity of storage
    m.MaxChargehy = Constraint(m.hyb_tech_in_zones, m.t, rule=con_maxchargehy)
    # HyCap in existing period is previous stor_cap_op plus stor_cap_new
    m.con_hyb_cap = Constraint(m.hyb_tech_in_zones, rule=con_hyb_cap)

    # @@ Objective
    # Minimise capital, variable and fixed costs of system
    m.FSCost = Expression(expr=0)
    m.SSCost = Expression(rule=obj_cost)
    # objective: minimise all other objectives
    m.Obj = Objective(expr=m.FSCost + m.SSCost)

    # Short run marginal prices
    m.dual = Suffix(direction=Suffix.IMPORT)
    return m
