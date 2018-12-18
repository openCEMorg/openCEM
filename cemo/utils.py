# Utility scripts for openCEM
import sys
import numpy as np
from pyomo.environ import value
import cemo.rules
import cemo.const
import matplotlib.pyplot as plt
import locale
from si_prefix import si_format

locale.setlocale(locale.LC_ALL, '')


def printonly(instance, key):
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
    switch = {
        'technology_type': cemo.const.TECH_TYPE,
        'region': cemo.const.REGION
    }
    return switch.get(table, lambda: "Name list not found")


def _techsinregion(instance, region):
    techsinregion = set()
    # Populate with intersecton of .gen_tech_per_zone set for all zones in region
    for z in instance.zones_per_region[region]:
        techsinregion = techsinregion | instance.gen_tech_per_zone[z]()
        techsinregion = techsinregion | instance.hyb_tech_per_zone[z]()
        techsinregion = techsinregion | instance.stor_tech_per_zone[z]()
    return sorted(techsinregion, key=lambda x: cemo.const.DISPLAY_ORDER.index(x))

# TODO copy colour scheme from openCEM website


def pallette(instance, techsinregion):
    pal = [(161 / 255, 135 / 255, 111 / 255, 1),  # biomass
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
           (0 / 255, 96 / 255, 1, 1)  # pumps vibrant blue
           ]
    return [pal[k - 1] for k in techsinregion]


def plotresults(instance):
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
                    np.array([value(instance.gen_disp[z, n, t])
                              for t in instance.t])
            for s in instance.stor_tech_per_zone[z]:
                q_z_r[pos[s], :] = q_z_r[pos[s], :] + \
                    np.array([value(instance.stor_disp[z, s, t])
                              for t in instance.t])
            for h in instance.hyb_tech_per_zone[z]:
                q_z_r[pos[h], :] = q_z_r[pos[h], :] + \
                    np.array([value(instance.hyb_disp[z, h, t])
                              for t in instance.t])
        # Plotting instructions
        # pick respective subplot
        if r % 2 == 0:
            ax = fig.add_subplot(2, 2, r)
        else:
            ax = fig.add_subplot(3, 2, r)
        palr = pallette(instance, techsinregion)
        ax.stackplot(ts, q_z_r, colors=palr)  # dispatch values
        ax.plot(ts, load, color='black')  # Put load on top
        ax.legend(plabels)  # put labels
        ax.set_title(rname[r])  # Region names

        fig.autofmt_xdate()
    plt.show()


def plotcapacity(instance):
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
        colour = pallette(instance, techsinregion)
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


def _printcosts(instance):
    print("Total Cost:\t %20s" %
          locale.currency(value(instance.Obj - cemo.rules.cost_shadow(instance)), grouping=True))
    print("Capital cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_capital(instance)),
                          grouping=True))
    print("Operating cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_operating(instance)),
                          grouping=True))
    print("Fixed cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_fixed(instance)),
                          grouping=True))
    print("Transm. cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_transmission(instance)),
                          grouping=True))
    print("Unserved cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_unserved(instance)),
                          grouping=True))
    print("Emission cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_emissions(instance)),
                          grouping=True))
    print("Retirmt cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_retirement(instance)),
                          grouping=True))


def _printemissionrate(instance):
    emrate = sum(value(cemo.rules.emissions(instance, r))
                 for r in instance.regions) /\
        sum(value(cemo.rules.dispatch(instance, r)) for r in instance.regions)
    print("Total Emission rate: %s kg/MWh" % str(emrate))


def _printunserved(instance):
    uns = np.zeros(5, dtype=float)
    for r in instance.regions:
        uns[r - 1] = 100.0 * sum(value(instance.unserved[r, t])
                                 for t in instance.t) \
            / sum(value(instance.region_net_demand[r, t]) for t in instance.t)

    print('Unserved %:' + str(uns))


def _printcapacity(instance):
    tname = _get_textid('technology_type')
    hours = float(len(instance.t))
    techtotal = [0] * len(instance.all_tech)
    disptotal = [0] * len(instance.all_tech)
    capftotal = [0] * len(instance.all_tech)
    nperz = [0] * len(instance.all_tech)
    for z in instance.zones:
        for n in instance.gen_tech_per_zone[z]:
            techtotal[n - 1] += value(instance.gen_cap_op[z, n])
            disptotal[n - 1] += value(sum(instance.gen_disp[z, n, t]
                                          for t in instance.t))
            capftotal[n - 1] += value(sum(instance.gen_cap_factor[z, n, t]
                                          for t in instance.t))
            nperz[n - 1] += 1
        for s in instance.stor_tech_per_zone[z]:
            techtotal[s - 1] += value(instance.stor_cap_op[z, s])
            disptotal[s - 1] += value(sum(instance.stor_disp[z, s, t]
                                          for t in instance.t))
            capftotal[s - 1] += 0.5 * hours
            nperz[s - 1] += 1

        for h in instance.hyb_tech_per_zone[z]:
            techtotal[h - 1] += value(instance.hyb_cap_op[z, h])
            disptotal[h - 1] += value(sum(instance.hyb_disp[z, h, t]
                                          for t in instance.t))
            capftotal[h - 1] += value(sum(instance.hyb_cap_factor[z, h, t]
                                          for t in instance.t))
            nperz[h - 1] += 1

    NEMcap = sum(techtotal)
    NEMdis = sum(disptotal)
    print("NEM Capacity total: %sW\tNEM Dispatch total: %sWh" % (
          si_format(NEMcap * 1e6, precision=2),
          si_format(NEMdis * 1e6, precision=2)
          ))

    for j in instance.all_tech:
        if techtotal[j - 1] > 0:
            print("%17s: %7sW | dispatch: %7sWh | avg cap factor: %.2f(%.2f)" % (
                tname[j],
                si_format(techtotal[j - 1] * 1e6, precision=1),
                si_format(disptotal[j - 1] * 1e6, precision=1),
                disptotal[j - 1] / hours / techtotal[j - 1],
                capftotal[j - 1] / hours / nperz[j - 1]
            ))


def printstats(instance):
    """Print summary of results for model instance"""
    _printcapacity(instance)
    _printcosts(instance)
    _printunserved(instance)
    _printemissionrate(instance)
    print("End of results for %s" % instance.name, flush=True)


def plotcluster(cluster, row=3, col=4, ylim=[5500, 16000]):
    # Plot cluster result from full set of weeks, cluster weeks and weights
    t = range(1, cluster.nplen + 1)
    # Make  row * col subplots
    f, axarr = plt.subplots(row, col, sharex=True)
    # Plot each observation in their respective cluster plot
    for i in range(cluster.periods):
        axarr.flat[cluster.cluster[i] -
                   1].plot(t, cluster.X[i][:cluster.nplen], alpha=0.5)

    # Add mean and nearest incluster for each cluster plit
    for j in range(cluster.max_d):
        axarr.flat[j].plot(t, cluster.Xsynth[j], 'k')  # mean
        axarr.flat[j].plot(t,
                           cluster.X[cluster.Xcluster['week']
                                     [j] - 1][:cluster.nplen],
                           'r',
                           linestyle='None',
                           marker='+')  # closest observation
    # make yrange the same in all plots
    for ax in axarr.flat:
        ax.set_ylim(ylim[0], ylim[1])
    # Show results
    plt.show(figsize=(14, 9))
