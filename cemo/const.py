# Constants module for cemo.
REGION = {
    1: 'NSW',
    2: 'QLD',
    3: 'SA',
    4: 'TAS',
    5: 'VIC'
}

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
    21: 'Other tech 1',
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

ZONES_IN_REGIONS = [(1, 5), (1, 6), (1, 7), (1, 8),
                    (2, 1), (2, 2), (2, 3), (2, 4),
                    (3, 13), (3, 14), (3, 15),
                    (4, 16),
                    (5, 9), (5, 10), (5, 11), (5, 12),
                    ]

REGION_INTERCONS = [(4, 5), (5, 4),
                    (5, 1), (1, 5),
                    (3, 5), (5, 3),
                    (1, 2), (2, 1),
                    ]

INTERCON_PROP_FACTOR = {
    1: {2: 0.61, 5: 0.2},
    2: {},
    3: {},
    4: {5: 0.66},
    5: {3: 0.5}
}
INTERCON_TRANS_LIMIT = {
    1: {2: 360, 5: 400},
    2: {1: 360},
    3: {5: 850},
    4: {5: 480},
    5: {1: 700, 3: 870, 4: 480},
}


DEFAULT_FUEL_PRICE = {
    1: 0.5,
    2: 9.68,
    3: 9.68,
    4: 3,
    5: 3,
    6: 3,
    7: 3,
    8: 9.68,
    16: 9.68,
    19: 9.68
}

DEFAULT_HEAT_RATE = {
    1: 12.66,
    2: 6.93,
    3: 6.93,
    4: 8.66,
    5: 8.66,
    6: 12.4,
    7: 12.4,
    8: 10.15,
    16: 7.6,
    19: 10.7
}

DEFAULT_FUEL_EMIT_RATE = {
    1: 57.13,
    2: 420.0,
    3: 420.0,
    4: 850.0,
    5: 850.0,
    6: 1100.0,
    7: 1100.0,
    8: 602.0,
    16: 602.0,
    19: 705.0
}

DEFAULT_HYDRO_MWH_MAX = {
    1: 195000,
    3: 0,
    4: 0,
    5: 3294000,
    6: 0,
    7: 0,
    8: 0,
    9: 0,
    10: 0,
    12: 4753000,
    14: 0,
    16: 11287000
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
    19: 52439.9  # Sould this be 10 like for gas?
}

DEFAULT_TECH_LIFETIME = {
    1: 60.0,
    2: 40.0,
    4: 60.0,
    8: 40.0,
    11: 30.0,
    12: 30.0,
    13: 30.0,
    14: 30.0,
    15: 30.0,

}
# First number in the sum is AEMO ISP build limits
# Second number in the sum is existing tech as per capacity by 2020
# TODO Check that wind existing is by 2020
# TODO impose a limit of 0 to PHES and CSP for regions that do not allow it
# TODO Make sure that wind is not double counted in Riverina and Murray river
DEFAULT_BUILD_LIMIT = {
    1: {
        11: 9250 + 1001,
        12: 8350 + 235
    },
    2: {
        11: 6000 + 170,
        12: 2105
    },
    3: {
        11: 4000 + 135,
        12: 2090 + 453
    },
    4: {
        11: 0 + 52.5,
        12: 0
    },
    5: {
        11: 8000 + 29.9,
        12: 5475 + 199
    },
    6: {
        11: 1000 + 0,
        12: 1735 + 914
    },
    7: {
        11: 6750 + 150,
        12: 2265 + 431
    },
    8: {
        11: 5000 + 57,
        12: 2760 + 270
    },
    9: {
        11: 0,
        12: 105 + 445
    },
    10: {
        11: 30,
        12: 1725 + 1220
    },
    11: {
        11: 3000 + 822,
        12: 1185 + 2069
    },
    12: {
        11: 0 + 453,
        12: 0
    },
    13: {
        11: 11950 + 330,
        12: 2770 + 1462
    },
    14: {
        11: 0,
        12: 1820 + 35
    },
    15: {
        11: 0,
        12: 1355 + 484
    },
    16: {
        11: 0,
        12: 3480 + 592
    }
}

DEFAULT_CAP_FACTOR = {
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
    13: 0,
    14: 1,
    15: 1,
    16: 1,
    17: 1,
    18: 1,
    19: 1
}

DEFAULT_STOR_PROPS = {
    "rt_eff": {
        14: 0.8,
        15: 0.8},
    "charge_hours": {
        14: 6,
        15: 2}
}

DEFAULT_HYB_PROPS = {
    "col_mult": {
        13: 1},
    "charge_hours": {
        13: 0}
}

DEFAULT_COSTS = {
    "unserved": 9800000,
    "trans": 50,
    "emit": 0,
}


MAX_MWH_CAP_FACTOR = {
    1: {1: 0.5},
    2: {1: 0.5},
    3: {1: 0.5},
    4: {1: 0.5},
    5: {1: 0.5},
    6: {1: 0.5},
    7: {1: 0.5},
    8: {1: 0.5},
    9: {1: 0.5},
    10: {1: 0.5},
    11: {1: 0.5},
    12: {1: 0.5},
    13: {1: 0.5},
    14: {1: 0.5},
    15: {1: 0.5},
    16: {1: 0.5}
}

DEFAULT_GEN_RAMP_PENALTY = {
    4: 5,
    6: 100,
    19: 25
}

ALL_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

DISPLAY_ORDER = [6, 7, 4, 5, 1, 16, 19, 2, 3, 8, 15, 18, 14, 12, 13, 9, 10, 11, 21, 22, 23, 24, 25]

GEN_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 18, 19, 20]
RE_GEN_TECH = [1, 9, 10, 11, 12, 18]
GEN_TRACE = [9, 10, 11, 12]
FUEL_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 16, 19]
HYB_TECH = [13]
STOR_TECH = [14, 15]

# IDEA These three may be exposed to users?
RETIRE_TECH = [2, 3, 4, 5, 6, 7, 8, 16, 19]
NOBUILD_TECH = [3, 4, 5, 6, 7, 9, 10, 16, 18, 19]
SYNC_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 13, 15, 16, 18, 19]

PALETTE = [(161 / 255, 135 / 255, 111 / 255, 1),  # biomass
           (251 / 255, 177 / 255, 98 / 255, 1),  # ccgt
           (251 / 255, 177 / 255, 98 / 255, 0.75),  # ccgt_sc
           (25 / 255, 25 / 255, 25 / 255, 1),  # coal_sc
           (25 / 255, 25 / 255, 25 / 255, 0.75),  # coal_sc_scc
           (137 / 255, 87 / 255, 45 / 255, 1),  # brown_coal_sc
           (137 / 255, 87 / 255, 45 / 255, 0.75),   # brown_coal_sc_scc
           (253 / 255, 203 / 255, 148 / 255, 1),  # ocgt
           (220 / 255, 205 / 255, 0, 0.6),  # PV DAT
           (220 / 255, 205 / 255, 0 / 255, 0.8),  # PV fixed
           (220 / 255, 205 / 255, 0 / 255, 1),  # PV SAT
           (67 / 255, 116 / 255, 14 / 255, 1),  # Wind
           (1, 209 / 255, 26 / 255, 1),  # CST 6h duck yellow
           (137 / 255, 174 / 255, 207 / 255, 1),  # PHES 6 h darker blue
           (43 / 255, 161 / 255, 250 / 255, 1),  # Battery some weird red
           (240 / 255, 79 / 255, 35 / 255, 1),  # recip engine, ugly gray
           (128 / 255, 191 / 255, 1, 1),  # Wind high light blue
           (75 / 255, 130 / 255, 178 / 255, 1),  # Hydro vibrant blue
           (241 / 255, 140 / 255, 31 / 255, 1),  # Gas thermal weird purple
           (0 / 255, 96 / 255, 1, 1),  # pumps vibrant blue
           (140 / 255, 140 / 255, 140 / 255, 1),  # Light gray other tech 1
           (145 / 255, 145 / 255, 145 / 255, 1),  # Light gray other tech 2
           (150 / 255, 150 / 255, 150 / 255, 1),  # Light gray other tech 3
           (155 / 255, 155 / 255, 155 / 255, 1),  # Light gray other tech 4
           (160 / 255, 160 / 255, 160 / 255, 1),  # Light gray other tech 5
           ]
