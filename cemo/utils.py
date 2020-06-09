""" Utility scripts for openCEM"""
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "GPLv3"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"

import locale
import sys

import matplotlib.pyplot as plt
import numpy as np
from pyomo.environ import value
from si_prefix import si_format

import cemo.const
import cemo.rules


def printonly(instance, key):  # pragma: no cover
    '''pprint specified instance variable and exit'''
    if key == "all":
        instance.pprint()  # pprint whole instance
    else:
        try:
            instance.component(key).pprint()  # pprint for provided key
        except KeyError:
            print("openCEM solve.py (printonly): Model key '%s' does not exist in model"
                  % key)
            sys.exit(1)


def _get_textid(table):
    '''Return text label for technology from const module'''
    switch = {
        'technology_type': cemo.const.TECH_TYPE,
        'region': cemo.const.REGION
    }
    return switch.get(table, lambda: "Name list not found")


def _techsinregion(instance, region):  # pragma: no cover
    techsinregion = set()
    # Populate with intersecton of .gen_tech_per_zone set for all zones in region
    for z in instance.zones_per_region[region]:
        techsinregion = techsinregion | instance.gen_tech_per_zone[z]()
        techsinregion = techsinregion | instance.hyb_tech_per_zone[z]()
        techsinregion = techsinregion | instance.stor_tech_per_zone[z]()
    return sorted(techsinregion, key=cemo.const.DISPLAY_ORDER.index)


def palette(instance, techsinregion):  # pragma: no cover
    '''Return a palette of tech colours for the set of techs in region given'''
    pal = cemo.const.PALETTE
    return [pal[k] for k in techsinregion]


def plotresults(instance):  # pragma: no cover
    """ Process results to plot.
     Feel free to improve the efficiency of this code
    """
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    # Process results to plot.
    # Feel free to improve the efficiency of this code
    # create set of plots that fits all NEM regions
    fig = plt.figure(figsize=(14, 9))
    # horizontal axis with timesamps
    ts = np.array([t for t in instance.t], dtype=np.datetime64)
    # cycle through NEM regions`
    for r in instance.regions:
        # Set of all technologies in a region
        techsinregion = _techsinregion(instance, r)
        # gather technology text_ids in region for plot labels
        plabels = []
        for t in techsinregion:
            plabels.append(tname[t])
        # append the label load
        plabels.insert(0, 'load')

        # gather load for NEM region from solved model instance
        load = np.array([value(instance.region_net_demand[r, t])
                         for t in instance.t])
        # Empty array of dispatch qtt
        q_z_r = np.zeros([len(techsinregion), len(instance.t)])
        # positions of each tech in numpy array
        pos = dict(zip(list(techsinregion), range(len(techsinregion))))
        # collect the total dispatch for each technology across Zones in region
        for z in instance.zones_per_region[r]:
            for n in instance.gen_tech_per_zone[z]:
                q_z_r[pos[n], :] = q_z_r[pos[n], :] + \
                    np.array([value(1e3 * instance.gen_disp[z, n, t])
                              for t in instance.t])
            for s in instance.stor_tech_per_zone[z]:
                q_z_r[pos[s], :] = q_z_r[pos[s], :] + \
                    np.array([value(1e3 * instance.stor_disp[z, s, t])
                              for t in instance.t])
            for h in instance.hyb_tech_per_zone[z]:
                q_z_r[pos[h], :] = q_z_r[pos[h], :] + \
                    np.array([value(1e3 * instance.hyb_disp[z, h, t])
                              for t in instance.t])
        # Plotting instructions
        # pick respective subplot
        if r % 2 == 0:
            ax = fig.add_subplot(2, 2, r)
        else:
            ax = fig.add_subplot(3, 2, r)
        palr = palette(instance, techsinregion)
        ax.stackplot(ts, q_z_r, colors=palr)  # dispatch values
        ax.plot(ts, load, color='black')  # Put load on top
        ax.legend(plabels)  # put labels
        ax.set_title(rname[r])  # Region names

        fig.autofmt_xdate()
    plt.show()


def plotcapacity(instance):  # pragma: no cover
    """ Stacked plot of capacities
     Feel free to improve the efficiency of this code
    """
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    # create set of plots that fits all NEM regions
    fig = plt.figure(figsize=(14, 9))
    # horizontal axis with timesamps
    # cycle through NEM regions`
    for r in instance.regions:
        # gather load for NEM region from solved model instance
        # empty set of all technologies in a region
        techsinregion = _techsinregion(instance, r)
        # gather technology text_ids in region for plot labels
        plabels = []
        for t in techsinregion:
            plabels.append(tname[t])

        # Empty array of gen_cap_op_r
        gen_cap_op_r = np.zeros([len(techsinregion)])
        gen_cap_new_r = np.zeros([len(techsinregion)])
        # positions of each tech in numpy array
        pos = dict(zip(list(techsinregion), range(len(techsinregion))))
        # collect the total dispatch for each technology across Zones in region
        for z in instance.zones_per_region[r]:
            for n in instance.gen_tech_per_zone[z]:
                gen_cap_op_r[pos[n]] = gen_cap_op_r[pos[n]] + \
                    np.array([value(instance.gen_cap_op[z, n])])
                gen_cap_new_r[pos[n]] = gen_cap_new_r[pos[n]] + \
                    np.array([value(instance.gen_cap_new[z, n])])
            for s in instance.stor_tech_per_zone[z]:
                gen_cap_op_r[pos[s]] = gen_cap_op_r[pos[s]] + \
                    np.array([value(instance.stor_cap_op[z, s])])
                gen_cap_new_r[pos[s]] = gen_cap_new_r[pos[s]] + \
                    np.array([value(instance.stor_cap_new[z, s])])
            for h in instance.hyb_tech_per_zone[z]:
                gen_cap_op_r[pos[h]] = gen_cap_op_r[pos[h]] + \
                    np.array([value(instance.hyb_cap_op[z, h])])
                gen_cap_new_r[pos[h]] = gen_cap_new_r[pos[h]] + \
                    np.array([value(instance.hyb_cap_new[z, h])])

        N = np.arange(len(techsinregion))
        ExCap_r = gen_cap_op_r - gen_cap_new_r
        width = 0.35
        # Plotting instructions
        colour = palette(instance, techsinregion)
        if r % 2 == 0:
            ax = fig.add_subplot(2, 2, r)
        else:
            ax = fig.add_subplot(3, 2, r)
        ax.bar(N, ExCap_r.tolist(), width, color=colour)  # Existing capacity
        ax.bar(N, gen_cap_new_r, width, bottom=ExCap_r,
               color=colour, edgecolor='white', hatch='////')  # New Capacity
        ax.set_xticks(N)
        ax.set_xticklabels([tname[t] for t in techsinregion])
        for tick in ax.get_xticklabels():
            tick.set_rotation(90)
        ax.set_title(rname[r], position=(0.9, 0.9))  # Region names
    plt.show()


def _printcosts(inst):
    locale.setlocale(locale.LC_ALL, 'en_AU.UTF-8')
    print("Total Cost:\t %20s" %
          locale.currency(value(cemo.rules.system_cost(inst)), grouping=True))
    print("Build cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_capital(inst)),
                          grouping=True))
    print("Repayment cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_repayment(inst)),
                          grouping=True))
    print("Operating cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_operating(inst)),
                          grouping=True))
    print("Fixed cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_fixed(inst)),
                          grouping=True))
    print("Trans. build cost:\t %12s" %
          locale.currency(value(cemo.rules.cost_trans_build(inst)),
                          grouping=True))
    print("Trans. flow cost:\t %12s" %
          locale.currency(value(cemo.rules.cost_trans_flow(inst)),
                          grouping=True))
    print("Unserved cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_unserved(inst)),
                          grouping=True))
    print("Emission cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_emissions(inst)),
                          grouping=True))
    print("Retirmt cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_retirement(inst)),
                          grouping=True))


def _printemissionrate(instance):
    emrate = sum(value(cemo.rules.emissions(instance, r))
                 for r in instance.regions) /\
        (sum(value(cemo.rules.dispatch(instance, r)) for r in instance.regions) + 1.0e-12)
    print("Total Emission rate: %6.3f kg/MWh" % emrate)


def _printunserved(instance):
    regions = list(instance.regions)
    unserved = np.zeros(len(regions), dtype=float)
    for region in regions:
        unserved[regions.index(region)] \
            = 100.0 * sum(value(instance.unserved[zone, time])
                          for zone in instance.zones_per_region[region]
                          for time in instance.t) \
            / sum(value(instance.region_net_demand[region, time]) for time in instance.t)

    print('Unserved %:' + str(unserved))


def _printcapacity(instance):
    tname = _get_textid('technology_type')
    hours = float(len(instance.t))
    techtotal = [0] * len(instance.all_tech)
    disptotal = [0] * len(instance.all_tech)
    capftotal = [0] * len(instance.all_tech)
    nperz = [0] * len(instance.all_tech)
    idx = list(instance.all_tech)
    for z in instance.zones:
        for n in instance.gen_tech_per_zone[z]:
            techtotal[idx.index(n)] += value(instance.gen_cap_op[z, n])
            disptotal[idx.index(n)] += value(sum(1e3 * instance.gen_disp[z, n, t]
                                                 for t in instance.t))
            capftotal[idx.index(n)] += value(sum(instance.gen_cap_factor[z, n, t]
                                                 for t in instance.t))
            nperz[idx.index(n)] += 1
        for s in instance.stor_tech_per_zone[z]:
            techtotal[idx.index(s)] += value(instance.stor_cap_op[z, s])
            disptotal[idx.index(s)] += value(sum(1e3 * instance.stor_disp[z, s, t]
                                                 for t in instance.t))
            capftotal[idx.index(s)] += 0.5 * hours
            nperz[idx.index(s)] += 1

        for h in instance.hyb_tech_per_zone[z]:
            techtotal[idx.index(h)] += value(instance.hyb_cap_op[z, h])
            disptotal[idx.index(h)] += value(sum(1e3 * instance.hyb_disp[z, h, t]
                                                 for t in instance.t))
            capftotal[idx.index(h)] += value(sum(instance.hyb_cap_factor[z, h, t]
                                                 for t in instance.t))
            nperz[idx.index(h)] += 1

    NEMcap = sum(techtotal)
    NEMdis = sum(disptotal)
    print("NEM Capacity total: %sW\tNEM Dispatch total: %sWh" % (
          si_format(NEMcap * 1e6, precision=2),
          si_format(NEMdis * 1e6, precision=2)
          ))

    for j in instance.all_tech:
        if techtotal[idx.index(j)] > 0:
            print("%17s: %7sW | dispatch: %7sWh | avg cap factor: %.2f(%.2f)" % (
                tname[j],
                si_format(techtotal[idx.index(j)] * 1e6, precision=1),
                si_format(disptotal[idx.index(j)] * 1e6, precision=1),
                disptotal[idx.index(j)] / hours / techtotal[idx.index(j)],
                capftotal[idx.index(j)] / hours / nperz[idx.index(j)]
            ))


def printstats(instance):
    """Print summary of results for model instance"""
    _printcapacity(instance)
    _printcosts(instance)
    _printunserved(instance)
    _printemissionrate(instance)
    print("End of results for %s" % instance.name, flush=True)


def plotcluster(cluster, row=3, col=4, ylim=None, show=False):  # pragma: no cover
    '''Plot cluster result from full set of weeks, cluster weeks and weights'''
    t = range(1, cluster.nplen + 1)
    # Make  row * col subplots
    axarr = plt.subplots(row, col, sharex=True)[1]
    # Plot each observation in their respective cluster plot
    for i in range(cluster.periods):
        axarr.flat[cluster.cluster[i]
                   - 1].plot(t, cluster.X[i][:cluster.nplen], '0.01', alpha=0.3, linewidth=0.75)

    # Add mean and nearest incluster for each cluster plit
    plotrange = cluster.max_d - 2 if isinstance(cluster, cemo.cluster.InstanceCluster) else cluster.max_d
    for j in range(plotrange):

        axarr.flat[j].plot(t, cluster.Xsynth[j], 'r')  # mean
        axarr.flat[j].plot(t,
                           cluster.X[cluster.Xcluster['week']
                                     [j] - 1][:cluster.nplen],
                           'k',
                           # linestyle='None',
                           # marker='+'
                           )  # closest observation
    # make yrange the same in all plots
    for ax in axarr.flat:
        if ylim is None:
            # default
            ax.set_ylim(0, 16000)
        else:
            ax.set_ylim(ylim[0], ylim[1])
    # Show results
    if show:
        plt.show()
    return plt
