"""Constants module for openCEM"""
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "GPLv3"
__version__ = "0.9.2"
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
    21: 'Snowy 2.0',
    22: 'Other tech 2',
    23: 'Other tech 3',
    24: 'Other tech 4',
    25: 'Other tech 5',
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
# REVIEW obsolete
REGION_INTERCONS = [
    (4, 5),
    (5, 4),
    (5, 1),
    (1, 5),
    (3, 5),
    (5, 3),
    (1, 2),
    (2, 1),
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
        2: {'loss': 0, 'limit': 1501, 'length': 600}
    },
    2: {
        1: {'loss': 0, 'limit': 1501, 'length': 600},
        3: {'loss': 0, 'limit': 1313, 'length': 385},
        4: {'loss': 0, 'limit': 1421, 'length': 500}
    },
    3: {
        2: {'loss': 0, 'limit': 1313, 'length': 385},
        4: {'loss': 0, 'limit': 5288, 'length': 130},
        8: {'loss': 0, 'limit': 1078, 'length': 415},
    },
    4: {
        2: {'loss': 0, 'limit': 1421, 'length': 500},
        3: {'loss': 0, 'limit': 5288, 'length': 130},
        8: {'loss': 0, 'limit': 234, 'length': 375},
    },
    5: {
        6: {'loss': 0, 'limit': 2022, 'length': 85},
        # REVIEW Estimate thermal limit based on 265MVAR capacity
        11: {'loss': 0, 'limit': 200, 'length': 20},
        # REVIEW Use limitations linked to Hydro generation at each side
        12: {'loss': 0, 'limit': 1300, 'length': 150},
        13: {'loss': 0, 'limit': 0, 'length': 600},
    },
    6: {
        5: {'loss': 0, 'limit': 2022, 'length': 85},
        7: {'loss': 0, 'limit': 2304, 'length': 115},
        # REVIEW Murray to Guthega is folded into 5-11 link
        12: {'loss': 0, 'limit': 0, 'length': 60},
    },
    7: {
        6: {'loss': 0, 'limit': 2304, 'length': 115},
        8: {'loss': 0, 'limit': 929, 'length': 220},
    },
    8: {
        3: {'loss': 0, 'limit': 486, 'length': 415},
        4: {'loss': 0, 'limit': 105, 'length': 375},
        7: {'loss': 0, 'limit': 929, 'length': 220},
    },
    9: {
        10: {'loss': 0, 'limit': 8907, 'length': 136},
        16: {'loss': 0.5, 'limit': 469, 'length': 320},
    },
    10: {
        9: {'loss': 0, 'limit': 8907, 'length': 136},
        11: {'loss': 0, 'limit': 542, 'length': 450},
        12: {'loss': 0, 'limit': 1422, 'length': 216},
        15: {'loss': 0, 'limit': 460, 'length': 125},
        16: {'loss': 0, 'limit': 0, 'length': 320},  # Estimate based on ISP VIC-TAS options
    },
    11: {
        # REVIEW Estimate thermal limit based on 265MVAR capacity
        5: {'loss': 0, 'limit': 200, 'length': 20},
        10: {'loss': 0, 'limit': 542, 'length': 450},
        12: {'loss': 0, 'limit': 284, 'length': 490},
        13: {'loss': 0, 'limit': 220, 'length': 150},
    },
    12: {
        5: {'loss': 0, 'limit': 1300, 'length': 150},  # REVIEW Use thermal limit worst case?
        6: {'loss': 0, 'limit': 0, 'length': 60},  # REVIEW Murray to Guthega is folded into 5-11 link
        10: {'loss': 0, 'limit': 1422, 'length': 216},
        11: {'loss': 0, 'limit': 284, 'length': 490},
    },
    13: {
        5: {'loss': 0, 'limit': 0, 'length': 600},
        11: {'loss': 0, 'limit': 220, 'length': 150},
        14: {'loss': 0, 'limit': 537, 'length': 100},
    },
    14: {
        13: {'loss': 0, 'limit': 537, 'length': 100},
        15: {'loss': 0, 'limit': 547, 'length': 380},
    },
    15: {
        10: {'loss': 0, 'limit': 460, 'length': 125},
        14: {'loss': 0, 'limit': 547, 'length': 380},
    },
    16: {
        9: {'loss': 0, 'limit': 594, 'length': 320},
        10: {'loss': 0, 'limit': 0, 'length': 320},  # Estimate based on ISP 2018 VIC-TAS option
    }
}
# REVIEW obsolete
INTERCON_PROP_FACTOR = {
    1: {
        2: 0.61,
        5: 0.2
    },
    2: {},
    3: {},
    4: {},
    5: {
        3: 0.5,
        4: 0.5
    }
}
# REVIEW obsolete
INTERCON_TRANS_LIMIT = {
    1: {
        2: 360,
        5: 400
    },
    2: {
        1: 1175
    },
    3: {
        5: 850
    },
    4: {
        5: 480
    },
    5: {
        1: 700,
        3: 870,
        4: 480
    },
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
    4: 8.66,
    5: 11.52,
    6: 12.4,
    7: 17.4,
    8: 10.15,
    16: 7.6,
    19: 10.7
}

DEFAULT_FUEL_EMIT_RATE = {
    1: 57.13,
    2: 410.0,
    3: 432.5,
    4: 850.0,
    5: 1150.0,
    6: 1100.0,
    7: 1683.0,
    8: 602.0,
    16: 602.0,
    19: 705.0
}

DEFAULT_HYDRO_MWH_MAX = {
    1: 195000,  # openNEM data shows the 2010-2017 yearly average is 662262
    3: 0,
    4: 0,
    5: 3294000,  # openNEM data shows the 2009-2018 yearly average is 2326421
    6: 0,
    7: 0,
    8: 0,
    9: 0,
    10: 0,
    12:
    4753000,  # openNEM data shows the 2009-2018 yearly average to be 2747264
    14: 0,
    16: 11287000  # openNEM 2009-2018 LTA is 9165993
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
    19: 52439.9  # FIXME Should this be 10k like for gas?
}

DEFAULT_TECH_LIFETIME = {
    1: 30.0,
    2: 30.0,
    4: 30.0,
    8: 30.0,
    11: 30.0,
    12: 30.0,
    13: 30.0,
    14: 50.0,
    15: 15.0,
    21: 50.0,
}
# Numbers are sum of ISP Build limits plus initial capacity as per capex table
# TODO impose a limit of 0 to PHES and CSP for regions that do not allow it
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
    1: 1,
    2: 1,
    3: 1,
    4: 1,
    5: 1,
    6: 1,
    7: 1,
    8: 1,
    9: 0,
    10: 0,
    11: 0,
    12: 0,
    16: 1,
    17: 0,
    18: 1,
    19: 1,
}

DEFAULT_STOR_PROPS = {
    "rt_eff": {
        14: 0.8,
        15: 0.8,
        21: 0.8
    },
    "charge_hours": {
        14: 6,
        15: 2,
        21: 168
    }
}

DEFAULT_HYB_PROPS = {
    "col_mult": {13: 1},
    "charge_hours": {13: 0}
}

DEFAULT_COSTS = {
    "unserved": 980000,
    "trans": 0.02339,  # AEMO 2018-2019 budget
    "emit": 0,
}

MAX_MWH_CAP_FACTOR = {
    1: {
        1: 0.5
    },
    2: {
        1: 0.5
    },
    3: {
        1: 0.5
    },
    4: {
        1: 0.5
    },
    5: {
        1: 0.5,
        4: 0.85
    },
    6: {
        1: 0.5,
        4: 0.85
    },
    7: {
        1: 0.5,
        4: 0.85
    },
    8: {
        1: 0.5,
        4: 0.85
    },
    9: {
        1: 0.5
    },
    10: {
        1: 0.5
    },
    11: {
        1: 0.5
    },
    12: {
        1: 0.5
    },
    13: {
        1: 0.5
    },
    14: {
        1: 0.5
    },
    15: {
        1: 0.5
    },
    16: {
        1: 0.5
    }
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
    },
    "rate up": {
        2: 0.68,
        3: 0.68,
        4: 0.67,
        5: 0.67,
        6: 0.45,
        7: 0.99,
        19: 0.67
    },
    "rate down": {
        2: 0.87,
        3: 0.87,
        4: 0.67,
        5: 0.67,
        6: 0.41,
        7: 0.41,
        19: 0.67
    },
    "uptime": {
        2: 4,
        3: 4,
        4: 12,
        5: 12,
        6: 12,
        7: 12,
        19: 12
    },
    "mincap": {
        2: 0.5,
        3: 0.5,
        4: 0.5,
        5: 0.5,
        6: 0.5,
        7: 0.5,
        19: 0.5
    }
}

ALL_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

DISPLAY_ORDER = [
    6, 7, 4, 5, 1, 16, 19, 2, 3, 8, 15, 18, 14, 12, 17, 13, 9, 10, 11, 21, 22,
    23, 24, 25
]

GEN_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 18, 19, 20]
RE_GEN_TECH = [1, 9, 10, 11, 12, 17, 18]
DISP_GEN_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 16, 18, 19]
RE_DISP_GEN_TECH = [1, 18]
GEN_TRACE = [9, 10, 11, 12, 17]
FUEL_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 16, 19]
COMMIT_TECH = [2, 3, 4, 5, 6, 7, 19]
HYB_TECH = [13]
STOR_TECH = [14, 15, 21]

RETIRE_TECH = [2, 3, 4, 5, 6, 7, 8, 16, 19]
NOBUILD_TECH = [3, 5, 6, 7, 9, 16, 18, 19, 21]
SYNC_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 13, 15, 16, 18, 19]

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
