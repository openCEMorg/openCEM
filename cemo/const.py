"""Constants module for openCEM"""
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "GPLv3"
__version__ = "0.9.5"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"
__status__ = "Development"
REGION = {1: 'NSW', 2: 'QLD', 3: 'SA', 4: 'TAS', 5: 'VIC'}

TECH_TYPE = {
    1: 'biomass',
    2: 'ccgt',
    3: 'ccgt_ccs',
    4: 'coal_sc',
    5: 'coal_sc_ccs',
    6: 'brown_coal_sc',
    7: 'brown_coal_sc_ccs',
    8: 'ocgt',
    9: 'solar_pv_dat',
    10: 'solar_pv_ffp',
    11: 'solar_pv_sat',
    12: 'wind',
    13: 'cst_6h',
    14: 'phes_6h',
    15: 'battery_2h',
    16: 'recip_engine',
    17: 'wind_h',
    18: 'hydro',
    19: 'gas_thermal',
    20: 'pumps',
    21: 'phes_168h',
    22: 'cst_3h',
    23: 'cst_12h',
    24: 'phes_3h',
    25: 'phes_12h',
    26: 'battery_1h',
    27: 'battery_3h',
    28: 'coal_sc_new'
}

ZONE = {
    1: 'NQ',
    2: 'CQ',
    3: 'SWQ',
    4: 'SEQ',
    5: 'SWNSW',
    6: 'CAN',
    7: 'NCEN',
    8: 'NNS',
    9: 'LV',
    10: 'MEL',
    11: 'CVIC',
    12: 'NVIC',
    13: 'NSA',
    14: 'ADE',
    15: 'SESA',
    16: 'TAS'
}

ZONES_IN_REGIONS = [
    (1, 5),
    (1, 6),
    (1, 7),
    (1, 8),
    (2, 1),
    (2, 2),
    (2, 3),
    (2, 4),
    (3, 13),
    (3, 14),
    (3, 15),
    (4, 16),
    (5, 9),
    (5, 10),
    (5, 11),
    (5, 12),
]

# Source Modelling Transmission Frameworks Review (EPR0019) Roam Consulting,
# Table 4.4, 2029-2030 values, adapted to openCEM zones
ZONE_DEMAND_PCT = {
    1: {
        'peak': 0.08,
        'off peak': 0.18,
        'prov': 'QLD'
    },
    2: {
        'peak': 0.19,
        'off peak': 0.31,
        'prov': 'QLD'
    },
    3: {
        'peak': 0.16,
        'off peak': 0.15,
        'prov': 'QLD'
    },
    4: {
        'peak': 0.57,
        'off peak': 0.36,
        'prov': 'QLD'
    },
    5: {
        'peak': 0.05,
        'off peak': 0.07,
        'prov': 'NSW'
    },
    6: {
        'peak': 0.06,
        'off peak': 0.05,
        'prov': 'ACT'
    },
    7: {
        'peak': 0.83,
        'off peak': 0.84,
        'prov': 'NSW'
    },
    8: {
        'peak': 0.06,
        'off peak': 0.04,
        'prov': 'NSW'
    },
    9: {
        'peak': 0.05,
        'off peak': 0.06,
        'prov': 'VIC'

    },
    10: {
        'peak': 0.82,
        'off peak': 0.81,
        'prov': 'VIC'
    },
    11: {
        'peak': 0.08,
        'off peak': 0.07,
        'prov': 'VIC'
    },
    12: {
        'peak': 0.05,
        'off peak': 0.06,
        'prov': 'VIC'
    },
    13: {
        'peak': 0.36,
        'off peak': 0.55,
        'prov': 'SA'
    },
    14: {
        'peak': 0.59,
        'off peak': 0.39,
        'prov': 'SA'
    },
    15: {
        'peak': 0.05,
        'off peak': 0.06,
        'prov': 'SA'
    },
    16: {
        'peak': 1.0,
        'off peak': 1.0,
        'prov': 'TAS'
    }
}

ZONE_INTERCONS = {
    1: {
        2: {'loss': 0.02, 'limit': 1501, 'length': 600, 'buildcost': 2500}
    },
    2: {
        1: {'loss': 0.02, 'limit': 1501, 'length': 600, 'buildcost': 2500},
        3: {'loss': 0.02, 'limit': 1313, 'length': 385, 'buildcost': 2500},
        4: {'loss': 0.02, 'limit': 1421, 'length': 500, 'buildcost': 2500}
    },
    3: {
        2: {'loss': 0.02, 'limit': 1313, 'length': 385, 'buildcost': 2500},
        4: {'loss': 0.02, 'limit': 5288, 'length': 130, 'buildcost': 2500},
        8: {'loss': 0.02, 'limit': 1078, 'length': 415, 'buildcost': 2500},
    },
    4: {
        2: {'loss': 0.02, 'limit': 1421, 'length': 500, 'buildcost': 2500},
        3: {'loss': 0.02, 'limit': 5288, 'length': 130, 'buildcost': 2500},
        8: {'loss': 0.02, 'limit': 234, 'length': 375, 'buildcost': 2500},
    },
    5: {
        6: {'loss': 0.02, 'limit': 2022, 'length': 85, 'buildcost': 2500},
        # Estimated thermal limit based on 265MVAR capacity
        # Artificial length is 150 so that builds are more comparable
        11: {'loss': 0.2, 'limit': 200, 'length': 150, 'buildcost': 2500},
        12: {'loss': 0.2, 'limit': 1350, 'length': 150, 'buildcost': 2500},
        13: {'loss': 0.02, 'limit': 0, 'length': 600, 'buildcost': 2500},
    },
    6: {
        5: {'loss': 0.02, 'limit': 2022, 'length': 85, 'buildcost': 2500},
        7: {'loss': 0.02, 'limit': 2304, 'length': 115, 'buildcost': 2500},
    },
    7: {
        6: {'loss': 0.02, 'limit': 2304, 'length': 115, 'buildcost': 2500},
        8: {'loss': 0.02, 'limit': 929, 'length': 220, 'buildcost': 2500},
    },
    8: {
        3: {'loss': 0.61, 'limit': 486, 'length': 415, 'buildcost': 2500},
        4: {'loss': 0.61, 'limit': 105, 'length': 375, 'buildcost': 2500},
        7: {'loss': 0.02, 'limit': 929, 'length': 220, 'buildcost': 2500},
    },
    9: {
        10: {'loss': 0.02, 'limit': 8907, 'length': 136, 'buildcost': 2500},
        16: {'loss': 0.5, 'limit': 469, 'length': 320, 'buildcost': 2500},
    },
    10: {
        9: {'loss': 0.02, 'limit': 8907, 'length': 136, 'buildcost': 2500},
        11: {'loss': 0.02, 'limit': 542, 'length': 450, 'buildcost': 2500},
        12: {'loss': 0.02, 'limit': 1422, 'length': 216, 'buildcost': 2500},
        15: {'loss': 0.5, 'limit': 460, 'length': 125, 'buildcost': 2500},
        16: {'loss': 0.5, 'limit': 0, 'length': 320, 'buildcost': 2500},  # West Tas to Geelong
    },
    11: {
        # Estimated thermal limit based on 265MVAR capacity
        5: {'loss': 0.02, 'limit': 200, 'length': 20, 'buildcost': 2500},
        10: {'loss': 0.02, 'limit': 542, 'length': 450, 'buildcost': 2500},
        12: {'loss': 0.02, 'limit': 284, 'length': 490, 'buildcost': 2500},
        13: {'loss': 0.5, 'limit': 220, 'length': 150, 'buildcost': 2500},
    },
    12: {
        5: {'loss': 0.02, 'limit': 1600, 'length': 150, 'buildcost': 2500},
        10: {'loss': 0.02, 'limit': 1422, 'length': 216, 'buildcost': 2500},
        11: {'loss': 0.02, 'limit': 284, 'length': 490, 'buildcost': 2500},
    },
    13: {
        5: {'loss': 0.02, 'limit': 0, 'length': 600, 'buildcost': 2500},
        11: {'loss': 0.02, 'limit': 220, 'length': 150, 'buildcost': 2500},
        14: {'loss': 0.02, 'limit': 537, 'length': 100, 'buildcost': 2500},
    },
    14: {
        13: {'loss': 0.02, 'limit': 537, 'length': 100, 'buildcost': 2500},
        15: {'loss': 0.02, 'limit': 547, 'length': 380, 'buildcost': 2500},
    },
    15: {
        10: {'loss': 0.02, 'limit': 460, 'length': 125, 'buildcost': 2500},
        14: {'loss': 0.02, 'limit': 547, 'length': 380, 'buildcost': 2500},
    },
    16: {
        9: {'loss': 0.02, 'limit': 594, 'length': 320, 'buildcost': 2500},
        10: {'loss': 0.02, 'limit': 0, 'length': 320, 'buildcost': 2500},
        # Estimate based on ISP 2018 VIC-TAS option
    }
}

DEFAULT_CAPEX = {
    16: 1588176  # GHD estimates for AEMO based on Barker Inlet
}

DEFAULT_FUEL_PRICE = {
    1: 0.5,
    2: 9.68,
    3: 9.68,
    4: 3.8,
    5: 3.8,
    6: 3.8,
    7: 3.8,
    8: 9.68,
    16: 9.68,
    19: 9.68
}

DEFAULT_HEAT_RATE = {
    1: 12.66,
    2: 6.93,
    3: 7.93,
    4: 9.66,
    5: 11.52,
    6: 12.4,
    7: 17.4,
    8: 10.15,
    16: 7.6,
    19: 10.7,
    28: 8.66,
}
DEFAULT_FUEL_EMIT_RATE = {
    1: 57.13,
    2: 410.0,
    3: 432.5,  # NTNDP data, not used
    4: 950.0,
    5: 1150.0,  # NTNDP data, not used
    6: 1100.0,
    7: 1683.0,  # NTNDP data, not used
    8: 602.0,
    16: 602.0,
    19: 705.0,
    28: 840.0,
}

DEFAULT_MAX_MWH_PER_ZONE = {
    18: {
        1: 662262,  # openNEM data shows the 2010-2017 yearly average is 662262
        3: 0,
        4: 0,
        5:
        2326421,  # openNEM data shows the 2009-2018 yearly average is 2326421
        6: 0,
        7: 0,
        8: 0,
        9: 0,
        10: 0,
        12:
        2747264,  # openNEM data shows the 2009-2018 yearly average to be 2747264
        14: 0,
        16: 9165993  # openNEM 2009-2018 LTA is 9165993
    }
}

DEFAULT_MAX_MWH_NEM_WIDE = {
    1: 10624e3,  # Source Near term potential for Biomass CEC BioEnergy RoadMap 2008
}


DEFAULT_RETIREMENT_COST = {
    2: 10487.98,
    3: 10487.98,
    4: 52439.9,
    5: 52439.9,
    6: 83903.4,
    7: 83903.4,
    8: 5243.99,
    11: 20975.96,
    12: 10487.98,
    16: 52439.9,
    19: 52439.9  # Copy of 16
}

DEFAULT_TECH_LIFETIME = {  # Source GHD 2018 AEMO cost and technical parameter review data book
    1: 50.0,
    2: 30.0,
    3: 30,
    4: 50,
    5: 50,
    6: 50,
    7: 50,
    8: 30,
    11: 30,
    12: 30,
    13: 40,
    14: 50,
    15: 15,
    17: 30,
    18: 50,
    19: 50,
    20: 50,
    21: 50.0,
    22: 40,
    23: 40,
    24: 50,
    25: 50,
    26: 15,
    27: 15,
    28: 50,

}

# Numbers are sum of ISP Build limits plus initial capacity as per capex table
DEFAULT_BUILD_LIMIT = {
    1: {
        11: 9250 + 1001,
        12: 8350 + 0,
        17: 2785 + 235,
    },
    2: {
        11: 6000 + 170,
        12: 2105,
        17: 695,
    },
    3: {
        11: 4000 + 135,
        12: 2090 + 0,
        17: 695 + 453,
    },
    4: {
        11: 0 + 52.5,
        12: 0,
        17: 0,
    },
    5: {
        11: 4000 + 3000 + 1000 + 29.9,  # Brkn hill + 1/2 of Murray R + 1/2 of Riverland + existing
        12: 1870 + 1620 + 232.5 + 0,
        17: 620 + 527.5 + 77.5 + 199,  #
    },
    6: {
        11: 1000 + 0,
        12: 1735 + 0,
        17: 575 + 914,
    },
    7: {
        11: 6750 + 150,
        12: 2265 + 0,
        17: 755 + 431,
    },
    8: {
        11: 5000 + 57,
        12: 2760 + 0,
        17: 900 + 270,
    },
    9: {
        11: 0,
        12: 105 + 0,
        17: 35 + 445,
    },
    10: {
        11: 30,
        12: 1725 + 0,
        17: 570 + 1220,
    },
    11: {
        11: 0 + 3000 + 822,  # Western Vic + 1/2 Murray R+ Existing
        12: 1185 + 1620 + 0,
        17: 395 + 527.5 + 1918,
    },
    12: {
        11: 0 + 453,
        12: 0,
        17: 0
    },
    13: {
        11: 10950 + 1000 + 330,  # All NSA + 1/2 of Riverland+ existing
        12: 2770 + 232.5 + 0,
        17: 915 + 77.5 + 1462,
    },
    14: {
        11: 0,
        12: 1820 + 0,
        17: 605 + 35,
    },
    15: {
        11: 0,
        12: 1355 + 0,
        17: 455 + 484,
    },
    16: {
        11: 0,
        12: 3480 + 0,
        17: 1155 + 592,
    }
}

GEN_CAP_FACTOR = {
    9: 0,
    10: 0,
    11: 0,
    12: 0,
}

DEFAULT_STOR_PROPS = {
    14: {"rt_eff": 0.8, "charge_hours": 6},
    24: {"rt_eff": 0.8, "charge_hours": 3},
    25: {"rt_eff": 0.8, "charge_hours": 12},
    21: {"rt_eff": 0.8, "charge_hours": 168},
    15: {"rt_eff": 0.8, "charge_hours": 2},
    26: {"rt_eff": 0.8, "charge_hours": 1},
    27: {"rt_eff": 0.8, "charge_hours": 3},
}

DEFAULT_HYB_PROPS = {
    13: {"col_mult": 2.5, "charge_hours": 6},
    22: {"col_mult": 2.1, "charge_hours": 3},
    23: {"col_mult": 3.1, "charge_hours": 12},
}

DEFAULT_COSTS = {
    "unserved": 980000,
    "trans": 0.02339,  # AEMO 2018-2019 budget
    "emit": 0,
}

DEFAULT_MODEL_OPT = {
    "nem_disp_ratio": {"value": 0.075},
    "region_ret_ratio": {"index": 'self.m.regions'}
}


GEN_COMMIT = {
    "penalty": {  # Startup fuel cost in GJ/MWh
        2: 19,
        3: 19,
        4: 41,
        5: 41,
        6: 41,
        7: 41,
        19: 25,
        28: 41,
    },
    "rate up": {
        2: 0.68,
        3: 0.68,
        4: 0.45,
        5: 0.45,
        6: 0.67,
        7: 0.67,
        19: 0.67,
        28: 0.45
    },
    "rate down": {
        2: 0.87,
        3: 0.87,
        4: 0.41,
        5: 0.41,
        6: 0.67,
        7: 0.67,
        19: 0.67,
        28: 0.41,
    },
    "uptime": {
        2: 4,
        3: 4,
        4: 12,
        5: 12,
        6: 12,
        7: 12,
        19: 12,
        28: 12
    },
    "mincap": {
        2: 0.5,
        3: 0.5,
        4: 0.5,
        5: 0.5,
        6: 0.5,
        7: 0.5,
        19: 0.5,
        28: 0.5
    },
    "effrate": {
        2: 0.85,
        3: 0.85,
        4: 0.85,
        5: 0.85,
        6: 0.85,
        7: 0.85,
        19: 0.85,
        28: 0.85
    }
}

ALL_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
            12, 13, 14, 15, 16, 17, 18, 19, 22, 23, 24, 25, 26, 27, 28]

DISPLAY_ORDER = [
    6, 7, 4, 5, 1, 16, 19, 2, 3, 8, 24, 14, 25, 21, 18, 26, 15, 27, 12, 17, 22, 13, 23, 9, 10, 11]

GEN_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 18, 19, 20, 28]
RE_GEN_TECH = [1, 9, 10, 11, 12, 17, 18]
DISP_GEN_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 16, 18, 19, 28]
RE_DISP_GEN_TECH = [1, 18]
TRACE_TECH = [11, 12, 13, 17]
FUEL_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 16, 19, 28]
COMMIT_TECH = [2, 3, 4, 5, 6, 7, 19, 28]
HYB_TECH = [13, 22, 23]
STOR_TECH = [14, 15, 21, 24, 25, 26, 27]

RETIRE_TECH = [2, 3, 4, 5, 6, 7, 8, 16, 19]
NOBUILD_TECH = [3, 4, 5, 6, 7, 9, 16, 18, 19, 21]  # 3, 5 and 7 no build due to incomplete data
SYNC_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 13, 15, 16, 18, 19]

# Variable bounds for numerical solver performance
# Intended to inform solver of magnitude of varables, not to limit solution values
# Select smallest value that will not limit solutions
# Avoid using conservatively large values may negate the effect of speeding up solution
CAP_BOUNDS = (0, 2.5e4)  # maximum capacity per zone
DISP_BOUNDS = (0, 2.5e4)  # maximum dispatch per zone
SCALED_DISP_BOUNDS = (0, 3e1)  # maximum scaled dispatch per zone
STOR_BOUNDS = (0, 7.5e5)  # maximum storage level per zone


PALETTE = {
    1: (161 / 255, 135 / 255, 111 / 255, 1),  # biomass
    2: (251 / 255, 177 / 255, 98 / 255, 1),  # ccgt
    3: (251 / 255, 177 / 255, 98 / 255, 0.75),  # ccgt_sc
    4: (25 / 255, 25 / 255, 25 / 255, 1),  # coal_sc
    5: (25 / 255, 25 / 255, 25 / 255, 0.75),  # coal_sc_scc
    6: (137 / 255, 87 / 255, 45 / 255, 1),  # brown_coal_sc
    7: (137 / 255, 87 / 255, 45 / 255, 0.75),  # brown_coal_sc_scc
    8: (253 / 255, 203 / 255, 148 / 255, 1),  # ocgt
    9: (220 / 255, 205 / 255, 0, 0.6),  # PV DAT
    10: (220 / 255, 205 / 255, 0 / 255, 0.8),  # PV fixed
    11: (220 / 255, 205 / 255, 0 / 255, 1),  # PV SAT
    12: (67 / 255, 116 / 255, 14 / 255, 1),  # Wind
    13: (1, 209 / 255, 26 / 255, 1),  # CST 6h
    14: (137 / 255, 174 / 255, 207 / 255, 1),  # PHES 6 h
    15: (43 / 255, 161 / 255, 250 / 255, 1),  # Battery
    16: (240 / 255, 79 / 255, 35 / 255, 1),  # recip engine,
    17: (70 / 255, 120 / 255, 1, 1),  # Wind high
    18: (75 / 255, 130 / 255, 178 / 255, 1),  # Hydro
    19: (241 / 255, 140 / 255, 31 / 255, 1),  # Gas thermal
    20: (0 / 255, 96 / 255, 1, 1),  # pumps
    21: (140 / 255, 140 / 255, 140 / 255, 1),  # Light gray other tech 1
    22: (145 / 255, 145 / 255, 145 / 255, 1),  # Light gray other tech 2
    23: (150 / 255, 150 / 255, 150 / 255, 1),  # Light gray other tech 3
    24: (155 / 255, 155 / 255, 155 / 255, 1),  # Light gray other tech 4
    25: (160 / 255, 160 / 255, 160 / 255, 1),  # Light gray other tech 5
}
