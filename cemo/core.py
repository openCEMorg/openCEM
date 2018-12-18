# openCEM model structure
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "?GPL"
__version__ = "0.1.1"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"
__status__ = "Development"

import cemo.const
from pyomo.environ import (AbstractModel, Var, Param, Constraint,
                           Objective, Set, Suffix,
                           NonNegativeReals,
                           BuildAction, Expression)
from cemo.rules import (con_ldbal, con_maxcap, con_caplim, con_opcap, con_uns,
                        con_storcharge, con_chargelim, con_dischargelim,
                        con_maxcharge, con_stcap,
                        con_maxtrans, con_emissions, con_maxmhw,
                        con_hybcharge,  con_dischargelimhy,
                        con_slackretire, con_nem_wide_ret, con_region_ret,
                        con_maxchargehy, con_hycap, con_chargelimhy,
                        con_ramp_up, con_ramp_down,
                        obj_cost, init_default_lifetime, init_cap_factor,
                        init_fcr, init_AdjustYearFactor, init_default_fuel_price,
                        init_default_heat_rate, init_cost_retire,
                        init_default_fuel_emit_rate, init_max_hydro,
                        init_gen_build_limit,
                        ScanForTechperZone, ScanForZoneperRegion,
                        ScanForStorageperZone, ScanForHybridperZone,
                        ScanForTransLineperRegion)


def create_model(namestr,
                 unslim=False,
                 emitlimit=False,
                 nemret=False,
                 regionret=False):
    """Creates an instance of the pyomo definition of openCEM"""
    model = AbstractModel(name=namestr)
    # Sets
    model.regions = Set()  # Set of NEM regions
    model.zones = Set()  # Set of NTNDP planning zones
    model.all_tech = Set()  # Set of generation technologies
    # set of emitting gen technologies
    model.fuel_gen_tech = Set(within=model.all_tech)
    # set of retireable technologies
    model.retire_gen_tech = Set(within=model.all_tech)
    # set of retireable technologies
    # TODO initialise all sets from const and see how multi now does not need their super initialisation and perhaps build actions take care of it #COMBAK
    model.nobuild_gen_tech = Set(
        within=model.all_tech, initialize=cemo.const.NOBUILD_TECH)
    # Set of storage technologies
    model.stor_tech = Set(within=model.all_tech)
    # set of hybrid (gen+storage) technologies
    model.hyb_tech = Set(within=model.all_tech)
    # Set of dispatch intervals
    model.t = Set(ordered=True)

    # Sparse set of zones per region
    model.zones_in_regions = Set(dimen=2)
    # Set listing technologies avaialable per zone (like a sparsity pattern)
    model.gen_tech_in_zones = Set(dimen=2)
    # Retirable technologies avaialable per zone (like a sparsity pattern)
    model.retire_gen_tech_in_zones = Set(dimen=2)
    # Fuel/emmitting technologies avaialable per zone (like a sparsity pattern)
    model.fuel_gen_tech_in_zones = Set(dimen=2)
    # Renewable technologies avaialable per zone (like a sparsity pattern)
    model.re_gen_tech_in_zones = Set(dimen=2)

    # Set listing storage avaialable per zone (like a sparsity pattern)
    model.hyb_tech_in_zones = Set(dimen=2)
    # Set listing storage avaialable per zone (like a sparsity pattern)
    model.stor_tech_in_zones = Set(dimen=2)
    # Set listing transmission lines to other regions in each region
    model.region_intercons = Set(dimen=2)

    # sparse sets built by build actions
    # Returns a list of planning zones for each region in R
    model.zones_per_region = Set(
        model.regions, within=model.zones, initialize=[])
    # Returns a tuple with generating techs in each zone
    model.gen_tech_per_zone = Set(
        model.zones, within=model.all_tech, initialize=[])
    # Returns a tuple with emitting techs in each zone
    model.fuel_gen_tech_per_zone = Set(
        model.zones, within=model.all_tech, initialize=[])
    model.re_gen_tech_per_zone = Set(
        model.zones, within=model.all_tech, initialize=[])
    # Returns a tuple with retirable techs in each zone
    model.retire_gen_tech_per_zone = Set(
        model.zones, within=model.all_tech, initialize=[])
    # Returns a tuple with storage techs in each zone
    model.stor_tech_per_zone = Set(
        model.zones, within=model.stor_tech, initialize=[])
    # Returns a tuple with emitting techs in each zone
    model.hyb_tech_per_zone = Set(
        model.zones, within=model.all_tech, initialize=[])
    # returns a tuple with transmission links in each region
    model.intercon_per_region = Set(model.regions, initialize=[])

    # @@ Build actions
    # Scan TechinZones and populate ?_gen_tech_per_zone
    model.TpZ_build = BuildAction(rule=ScanForTechperZone)
    # Scan HybTechinZones and populate hyb_tech_per_zone
    model.HpZ_build = BuildAction(rule=ScanForHybridperZone)
    # Scan ZinR and populate ZperR
    model.ZpR_build = BuildAction(rule=ScanForZoneperRegion)
    # Scan TransLines and populate intercon_per_region
    model.TrpR_build = BuildAction(rule=ScanForTransLineperRegion)
    # Scan StorinZones and populate stor_tech_per_zone
    model.SpZ_build = BuildAction(rule=ScanForStorageperZone)

    # @@ Parameters
    # Capital costs generators
    # Build costs for generators
    model.cost_gen_build = Param(model.gen_tech_in_zones, default=9e7)
    model.cost_stor_build = Param(
        model.stor_tech_in_zones)  # Capital costs storage
    model.cost_hyb_build = Param(
        model.hyb_tech_in_zones)  # Capital costs hybrid

    model.cost_fuel = Param(model.fuel_gen_tech_in_zones,
                            initialize=init_default_fuel_price)  # Fuel cost

    # Fixed operating costs generators
    model.cost_gen_fom = Param(model.all_tech)
    # Variable operating costs generators
    model.cost_gen_vom = Param(model.all_tech)
    # Fixed operating costs storage
    model.cost_stor_fom = Param(model.stor_tech)
    # Variable operating costs storage
    model.cost_stor_vom = Param(model.stor_tech)
    # Fixed operating costs hybrid
    model.cost_hyb_fom = Param(model.hyb_tech)
    # Variable operating costs hybrid
    model.cost_hyb_vom = Param(model.hyb_tech)
    # Technology lifetime in years
    model.all_tech_lifetime = Param(
        model.all_tech, initialize=init_default_lifetime)
    # Project discount rate
    model.all_tech_discount_rate = Param(default=0.05)

    # Technology fixed charge rate
    model.fixed_charge_rate = Param(model.all_tech, initialize=init_fcr)
    # Per year cost adjustment for sims shorter than 1 year of dispatch
    model.year_correction_factor = Param(initialize=init_AdjustYearFactor)

    model.cost_retire = Param(model.retire_gen_tech,
                              initialize=init_cost_retire)
    model.cost_unserved = Param()  # cost of unserved power
    model.cost_emit = Param(default=0.0)  # cost in $/kg of total emissions
    model.cost_trans = Param(default=0.22)  # cost of transmission

    # Round trip efficiency of storage technology
    model.stor_rt_eff = Param(model.stor_tech)
    # Number of hours of storage technology
    model.stor_charge_hours = Param(model.stor_tech)

    # Collector multiple of hybrid technology
    model.hyb_col_mult = Param(model.hyb_tech)
    # Number of hours of storage technology
    model.hyb_charge_hours = Param(model.hyb_tech)

    model.fuel_heat_rate = Param(
        model.fuel_gen_tech_in_zones, initialize=init_default_heat_rate)
    # Emission rates
    model.fuel_emit_rate = Param(
        model.fuel_gen_tech, initialize=init_default_fuel_emit_rate)
    # proportioning factors for notional interconnectors
    model.intercon_prop_factor = Param(model.region_intercons)

    model.gen_cap_factor = Param(model.gen_tech_in_zones, model.t,
                                 initialize=init_cap_factor)  # Capacity factors for generators
    model.hyb_cap_factor = Param(model.hyb_tech_in_zones, model.t,
                                 initialize=init_cap_factor)  # Capacity factors for generators

    # Maximum capacity per generating technology per zone
    model.gen_build_limit = Param(
        model.gen_tech_in_zones, initialize=init_gen_build_limit)
    model.gen_cap_initial = Param(model.gen_tech_in_zones,
                                  default=0)  # operating capacity
    model.stor_cap_initial = Param(
        model.stor_tech_in_zones, default=0)  # operating capacity
    model.hyb_cap_initial = Param(model.hyb_tech_in_zones,
                                  default=0)  # operating capacity
    # exogenous new capacity
    model.gen_cap_exo = Param(model.gen_tech_in_zones, default=0)
    # exogenous new storage capacity
    model.stor_cap_exo = Param(model.stor_tech_in_zones, default=0)
    # exogenous new hybrid capacity
    model.hyb_cap_exo = Param(model.hyb_tech_in_zones,
                              default=0)
    model.ret_gen_cap_exo = Param(model.retire_gen_tech_in_zones, default=0)
    # Net Electrical load (may include rooftop and EV)
    model.region_net_demand = Param(model.regions, model.t)

    # Maximum hydro energy
    model.hydro_gen_mwh_limit = Param(model.zones, initialize=init_max_hydro)
    # Transmission line limits
    model.intercon_trans_limit = Param(model.region_intercons)

    # carry forward capital costs
    model.cost_cap_carry_forward = Param(default=0)

    # @@ Variables
    model.gen_cap_new = Var(model.gen_tech_in_zones,
                            within=NonNegativeReals)  # New capacity
    model.gen_cap_op = Var(model.gen_tech_in_zones,
                           within=NonNegativeReals)  # Total generation capacity
    model.stor_cap_new = Var(model.stor_tech_in_zones,
                             within=NonNegativeReals)  # New storage capacity
    model.stor_cap_op = Var(model.stor_tech_in_zones,
                            within=NonNegativeReals)  # Total storage capacity
    model.hyb_cap_new = Var(model.hyb_tech_in_zones,
                            within=NonNegativeReals)
    model.hyb_cap_op = Var(model.hyb_tech_in_zones,
                           within=NonNegativeReals)
    model.gen_cap_ret = Var(model.retire_gen_tech_in_zones,
                            within=NonNegativeReals)  # retireable capacity
    model.gen_cap_ret_neg = Var(model.retire_gen_tech_in_zones,
                                within=NonNegativeReals)  # if exogenous retires is more than opcap0

    model.gen_disp = Var(model.gen_tech_in_zones, model.t,
                         within=NonNegativeReals)  # dispatched power

    model.stor_disp = Var(model.stor_tech_in_zones, model.t,
                          within=NonNegativeReals)  # dispatched power from storage

    model.stor_charge = Var(model.stor_tech_in_zones, model.t,
                            within=NonNegativeReals)  # power to charge storage

    model.hyb_disp = Var(model.hyb_tech_in_zones, model.t,
                         within=NonNegativeReals)  # dispatched power from hybrid

    model.hyb_charge = Var(model.hyb_tech_in_zones, model.t,
                           within=NonNegativeReals)  # charging power from hybrid

    model.stor_level = Var(model.stor_tech_in_zones, model.t,
                           within=NonNegativeReals)  # Charge level for storage

    model.hyb_level = Var(model.hyb_tech_in_zones, model.t,
                          within=NonNegativeReals)  # Charge level for storage

    model.unserved = Var(model.regions, model.t,
                         within=NonNegativeReals)  # unserved power
    model.surplus = Var(model.regions, model.t,
                        within=NonNegativeReals)  # surplus power (if any)

    model.intercon_disp = Var(model.region_intercons,
                              model.t, within=NonNegativeReals)

    # @@ Constraints
    # Transmission limits
    model.transmax = Constraint(
        model.region_intercons, model.t, rule=con_maxtrans)
    # Load balance
    model.ldbal = Constraint(model.regions, model.t, rule=con_ldbal)
    # Dispatch to be within capacity, RE have variable capacity factors
    model.caplim = Constraint(model.gen_tech_in_zones,
                              model.t, rule=con_caplim)
    # Limit maximum capacity to be built in each region and each technology
    model.maxcap = Constraint(model.gen_tech_in_zones, rule=con_maxcap)
    # gen_cap_op in existing period is previous gen_cap_op plus gen_cap_new
    model.opcap = Constraint(model.gen_tech_in_zones, rule=con_opcap)
    # MaxMWh limit (currently only for hydro)
    model.MaxMWh = Constraint(model.gen_tech_in_zones, rule=con_maxmhw)
    # Slack constraint on exogenous retirement to prevent it to go nevative
    model.negativeretirecap = Constraint(
        model.retire_gen_tech_in_zones, rule=con_slackretire)

    model.ramp_up_delta = Var(model.gen_tech_in_zones,
                              model.t, domain=NonNegativeReals)

    model.ramp_dn_delta = Var(model.gen_tech_in_zones,
                              model.t, domain=NonNegativeReals)

# Ramp rate constraints
    model.con_ramp_up = Constraint(
        model.gen_tech_in_zones, model.t, rule=con_ramp_up)
    model.con_ramp_down = Constraint(
        model.gen_tech_in_zones, model.t, rule=con_ramp_down)

    # Hard constraint on unserved energy
    if unslim:
        model.con_uns = Constraint(model.regions, rule=con_uns)
    # Emmissions constraint
    if emitlimit:
        model.con_emissions = Constraint(rule=con_emissions)
        # maximum kg/MWh rate of total emissions
        model.nem_year_emit_limit = Param()
    # NEM wide RET constraint
    if nemret:
        # NEM wide renewable energy target for current year
        model.nem_ret_ratio = Param(default=0)
        # NEM wide renewable energy constraint
        model.con_nem_wide_ret = Constraint(rule=con_nem_wide_ret)
    if regionret:
        # Regional RET targets for current year
        model.region_ret_ratio = Param(model.regions, default=0)
        # Regional RET constraint
        model.con_region_ret = Constraint(model.regions, rule=con_region_ret)

    # Storage charge/discharge dynamic
    model.StCharDis = Constraint(
        model.stor_tech_in_zones, model.t, rule=con_storcharge)
        # Maxiumum rate of storage charge
    model.Chargelimit = Constraint(
        model.stor_tech_in_zones, model.t, rule=con_chargelim)
    # Maxiumum rate of storage discharge
    model.Dishchargelimit = Constraint(
        model.stor_tech_in_zones, model.t, rule=con_dischargelim)
    # Maxiumum charge capacity of storage
    model.MaxCharge = Constraint(
        model.stor_tech_in_zones, model.t, rule=con_maxcharge)
    # StCap in existing period is previous stor_cap_op plus stor_cap_new
    model.stcap = Constraint(model.stor_tech_in_zones, rule=con_stcap)

    # Hybrid charge/discharge dynamic
    model.HybCharDis = Constraint(
        model.hyb_tech_in_zones, model.t, rule=con_hybcharge)
    # Maxiumum rate of hybrid storage discharge
    model.Chargelimithy = Constraint(
        model.hyb_tech_in_zones, model.t, rule=con_chargelimhy)
    # Maxiumum rate of hybrid storage discharge
    model.Dishchargelimithy = Constraint(
        model.hyb_tech_in_zones, model.t, rule=con_dischargelimhy)
    # Maxiumum charge capacity of storage
    model.MaxChargehy = Constraint(
        model.hyb_tech_in_zones, model.t, rule=con_maxchargehy)
    # HyCap in existing period is previous stor_cap_op plus stor_cap_new
    model.hycap = Constraint(model.hyb_tech_in_zones, rule=con_hycap)

    # @@ Objective
    # Minimise capital, variable and fixed costs of system
    model.FSCost = Expression(expr=0)
    model.SSCost = Expression(rule=obj_cost)
    # objective: minimise all other objectives
    model.Obj = Objective(expr=model.FSCost +
                          model.SSCost + model.cost_cap_carry_forward)

    # Short run marginal prices
    model.dual = Suffix(direction=Suffix.IMPORT)
    return model
