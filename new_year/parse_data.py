#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys, os
import math
import json
import xml.etree.ElementTree as ET

from optparse import OptionParser

from utils import *

import pprint
import matplotlib.pyplot as plt
import matplotlib

import random

att_keys = ['price', 'manufacturer', 'operating_system',
            'battery_life', 'display_size', 'hard_drive_capacity',
            'installed_memory', 'processor_class', 'processor_speed',
            'weight']

value_keys = ["price",  "battery_life",
        "display_size", "hard_drive_capacity", "installed_memory",
        "processor_speed", "weight"]

def load_prds(filepath, att_filepath):
    # print att_filepath
    atts = json.load(open(att_filepath, 'r'))
    prd_container = {}
    tree = ET.parse(filepath)
    # for dirname, dirnames, filenames in os.walk(container_path):
    #         for filename in filenames:
    #             file_path = os.path.join(dirname, filename)
    #             tree = ET.parse(file_path)
    #             root = tree.getroot()
    root = tree.getroot()

    for child in root:
        prd = {}
        for item in child:
            tag = item.tag
            if tag == 'id':
                prd['id'] = item.text
            elif tag == 'price':
                prd['price'] = float(item.text)
            elif tag == 'brand':
                prd['name'] = item.text
            elif tag == 'manufacturer':
                prd['manufacturer'] = item.text
            elif tag == 'operating_system':
                prd['operating_system'] = item.text
            elif tag == 'battery_life':

                if item.text is None:
                    prd['battery_life'] = atts[tag]['default']
                else:
                    prd['battery_life'] = float(item.text)
            elif tag == 'display_size':
                prd['display_size'] = float(item.text)
            elif tag == 'hard_drive_capacity':
                if item.text is None:
                    prd['hard_drive_capacity'] = atts[tag]['default']
                else:
                    prd['hard_drive_capacity'] = float(item.text)
            elif tag == 'installed_memory':
                prd['installed_memory'] = float(item.text)
            elif tag == "processor_class":
                prd['processor_class'] = item.text
            elif tag == "processor_speed":
                prd['processor_speed'] = float(item.text)
            elif tag == "weight":
                if item.text is None:
                    prd['weight'] = atts[tag]['default']
                else:
                    prd['weight'] = float(item.text)

        prd_container[prd['id']] = prd

    return prd_container

ax_id = 0

def parse_session(session, pdb, ax_id, sid, sname, dm):
    if sid in [9, 19, 73, 89, 90]:
        return False
    print '%d,%s' % (sid, sname),

    stype = 1
    if sid in [7, 9, 11, 14, 17, 19, 23, 27, 31, 33,
                37, 39, 50, 53, 55, 60, 64, 66, 67,
                68, 70, 71, 73, 74, 88, 89, 90, 93]:
        stype = 3

    ax = plt.subplot(43, 1, ax_id)

    ax.set_xticks([2, 6, 10, 14])
    ax.set_xticklabels(['high','middle','low', 'zero'])
    ax.set_yticklabels([])

    plt.plot(0, 0.5, 'wo')
    plt.plot(16, 0.5, 'wo')

    for l in [4, 8, 12, 16]:
        ax.axvline(l, color='black', lw=1)

    viewed_pids = []
    critiqued_pid = session[-1][31] # the last one
    displayed_pids = []

    fix_freqs = {}
    fix_ds = {}
    for k in att_keys:
        fix_freqs[k] = 0
        fix_ds[k] = 0

    cts = {}
    cts_types = {}

    prd_fix_freqs = {}
    prd_fix_ds = {}

    for i, items in enumerate(session):
        if i == 0:
            displayed_pids = items[-1].split('::')
            new_disps = []
            for pid in displayed_pids:
                if pid == '100':
                    pid = '81'

                new_disps.append(pid)
            displayed_pids = new_disps

        pid = items[2]
        if pid == '100':
            pid = '81'
        if pid not in viewed_pids:

            viewed_pids.append(pid)

        # fixation data
        att_fixated = items[5:15]
        d = float(items[17]) # duration

        if '1' in att_fixated:
            fi = att_fixated.index('1')
            ak = att_keys[fi]

            if ak not in fix_freqs:
                fix_freqs[ak] = 1.0
                fix_ds[ak] = d
            else:
                fix_freqs[ak] += 1.0
                fix_ds[ak] += d

        if pid not in prd_fix_freqs:
            prd_fix_freqs[pid] = 1.0
            prd_fix_ds[pid] = d
        else:
            prd_fix_freqs[pid] += 1.0
            prd_fix_ds[pid] += d

        # critiques
        critique_pid = items[31]
        if len(critique_pid) > 0: # the last line
            critiques = items[19:29]
            for ci, c in enumerate(critiques):
                ck = att_keys[ci]
                cts[ck] = c

                ctype = '='

                if stype == 1:
                    if c.startswith("<>"):
                        ctype = '+'
                    elif c.startswith("any"):
                        ctype = 'a'

                    elif c.startswith('>'):
                        if ck in ['price', 'weight']:
                            ctype = '-'
                        else:
                            ctype = '+'
                    elif c.startswith('<'):
                        if ck in ['price', 'weight']:
                            ctype = '+'
                        else:
                            ctype = '-'
                    else:
                        ctype = '='

                else:
                    if c.startswith('>') or c.startswith('<'):
                        ctype = '+'
                    elif c.startswith('any'):
                        ctype = 'a'
                    else:
                        ctype = '='

                if ctype == 'a':
                    ctype = '-'

                cts_types[ck] = ctype
            break

    # value levels
    top = pdb[critique_pid]
    prds = [pdb[pid] for pid in viewed_pids if len(pid)> 0]

    print ',%s,' % critique_pid,

    v_levels = {}

    cates = ['manufacturer', 'operating_system',
                        'processor_class'
                    ]
    for k in att_keys:
        value_levels = [0, 0, 0]
        av = top[k]

        if k in cates:
            v_level = 4
            v_levels[k] = v_level
            continue

        if k not in ['price', 'weight']:
            for v in [p[k] for p in prds]:
                if av >= v:
                    value_levels[0] += 1

                if av <= v:
                    value_levels[2] += 1
        else:
            for v in [p[k] for p in prds]:
                if av <= v:
                    value_levels[0] += 1

                if av >= v:
                    value_levels[2] += 1

        if value_levels[0] == len(prds):
            v_level = 1
        elif value_levels[2] == len(prds):
            v_level = 3
        else:
            v_level = 2


        v_levels[k] = v_level

    # fix_freqs = fix_ds
    fix_levels = group_levels(fix_freqs, 3)
    orders = order_dict(fix_freqs)[::-1]

    if critique_pid in prd_fix_freqs:
        del prd_fix_freqs[critique_pid]
        del prd_fix_ds[critique_pid]
    prd_fix_avg = {}
    for pi in prd_fix_freqs:
        prd_fix_avg[pi] = prd_fix_ds[pi] / prd_fix_freqs[pi]

    prd_ranks = [critique_pid] + order_dict(prd_fix_freqs)[::-1]

    print '%s,' % ','.join(['%d' % int(fix_freqs[k]) for k in att_keys]),
    print '%s,' % ','.join(['%d' % int(fix_ds[k]) for k in att_keys]),
    print '%s,' % '::'.join(viewed_pids),
    print '%s,' % ','.join([cts_types[k] for k in att_keys]),
    print '%s,' % '::'.join(displayed_pids),

    v_labels = []
    for k in value_keys:
        if v_levels[k] == 1:
            v_labels.append('better than all')
        elif v_levels[k]== 2:
            v_labels.append('better than some')
        else:
            v_labels.append('worse than all')
    print '%s,' % ','.join(v_labels),


    left = []
    for ppid in viewed_pids:
        if ppid not in displayed_pids:
            left.append(ppid)
    print '%s,' % '::'.join(left),

    print '%s,' % '::'.join(prd_ranks),

    prd_ranks = [critique_pid] + order_dict(prd_fix_ds)[::-1]
    print '%s,' % '::'.join(prd_ranks),

    prd_ranks = [critique_pid] + order_dict(prd_fix_avg)[::-1]
    print '%s' % '::'.join(prd_ranks)


    # stats = {}
    # stats['+'] = {"att_num": 0, "avg_freq": 0.0, "avg_dur": 0.0, "vtypes": {1:0, 2:0, 3:0, 4:0}}
    # stats['-'] = {"att_num": 0, "avg_freq": 0.0, "avg_dur": 0.0, "vtypes": {1:0, 2:0, 3:0, 4:0}}
    # stats['='] = {"att_num": 0, "avg_freq": 0.0, "avg_dur": 0.0, "vtypes": {1:0, 2:0, 3:0, 4:0}}
    # for k in cts_types.keys():
    #     ctype = cts_types[k]
    #     stats[ctype]['att_num'] += 1
    #     stats[ctype]['avg_freq'] += fix_freqs[k]
    #     stats[ctype]['avg_dur'] += fix_ds[k]
    #     stats[ctype]["vtypes"][v_levels[k]] += 1

    # for ck in ['+', '-', '=']:
    #     acount = stats[ck]['att_num']
    #     print '%d,' % acount,
    #     if acount > 0:
    #         print '%.2f,' % (stats[ck]['avg_freq']/acount),
    #         print '%.2f,' % (stats[ck]['avg_dur']/acount),
    #     else:
    #         print '#,#,',
    #     vcounts = stats[ck]['vtypes']
    #     print '%d,%d,%d,%d,,' % (vcounts[1], vcounts[2], vcounts[3], vcounts[4]),
    # print






    last_x = 0
    zs = []
    for c in [1, 2, 3, 4]: # the 3 fix levels

        if c == 4:
            for k, l in fix_levels.items():
                # print l,
                if l == c:
                    # print k,
                    x = 4 * (c - 1)
                    x = x + random.random() * 4.0
                    x += 0.1 + random.random() * 1.5
                    if x >= 15.5:
                        x = 4 * (c - 1) + random.random() * 4.0

                    ctype = cts_types[k]
                    vtype = v_levels[k]
                    zs.append([x, ctype, vtype])

                    dm[l][vtype][ctype] += 1
                    # show_dot(x, 0.5, ctype, vtype)
            continue

        center = 0.0
        count = 0
        atts = []
        vs = []
        total = 0.0
        for k in orders:
            l = fix_levels[k]
        #for k, l in fix_levels.items():
            if l == c:
                atts.append(k)
                vs.append(fix_freqs[k])
                center += fix_freqs[k]
                count += 1
        if count > 0:
            total = center
            center = center/count
        else:
            continue

        # print 'c: %d -> %d' % (c, len(atts))
        if len(atts) >= 3:
            xbegin = 4 * (c - 1) + 3.8
            vs = [x/total for x in vs]
            j = len(vs) - 1
            while j >= 0:

                x = xbegin - vs[j] * 3.6
                k = atts[j]
                ctype = cts_types[k]
                vtype = v_levels[k]
                j = j - 1
                # print '%.2f->%.2f\t' % (vs[j], x),
                xbegin = x
                show_dot(x, 0.5, ctype, vtype)
                dm[c][vtype][ctype] += 1
            # print
        else:

            # print 'level %d: ' % c,
            xcenter = 4 * (c - 1) + 2.0
            for k in atts:
                x = xcenter - (fix_freqs[k] - center)/center * 5
                if x < xcenter - 1.8:
                    x = xcenter - 1.6

                # print '%.2f\t' % x,
                if x - last_x < 0.8:
                    if last_x + 0.8 < xcenter + 1.8:
                        x = last_x + 0.8
                    else:
                        x = xcenter + 1.8

                if last_x == xcenter + 1.8 and x == last_x:
                    x = xcenter + 1.5

                last_x = x
                y = 0.5
                ctype = cts_types[k]
                vtype = v_levels[k]
                # print 'x: %.2f, ctype: %s, vtype: %d' % (x, ctype, vtype)
                show_dot(x, y, ctype, vtype)
                dm[c][vtype][ctype] += 1
        # print
    # print '#######################'

    hx = []
    for x, ctype, vtype in zs:
        for y in hx:
            while abs(y - x) < 0.2:
                x = x + 0.25
                if x >= 15.5:
                    x = 12 + random.random() * 4.0
        hx.append(x)
        show_dot(x, 0.5, ctype, vtype)
    return True
    # plot


    # print 'critiqued pid:\t%s' % critiqued_pid
    # print 'viewd pids:\t%s' % '::'.join(viewed_pids)
    # print 'display pids:\t%s' % '::'.join(displayed_pids)
    # for pid in viewed_pids:
    #     if pid not in displayed_pids:
    #         print '%s\t' % pid,
    # print
def show_dot(x, y, ctype, vtype):
    colors = 'rbky'
    if ctype == '+':
        marker = '$\\bullet{\uparrow}$'
    elif ctype == '-':
        marker = '$\\bullet{\downarrow}$'
    else:
        marker = '$\\bullet{=}$'

    if vtype == 3:
        plt.plot(x, y, marker=marker, color=colors[vtype-1], markersize=18)
    else:
        plt.plot(x, y, marker=marker, color=colors[vtype-1], markersize=18)

def main():
    usage = "usage prog [options] arg"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--input", dest="input",
        help="the input file")
    parser.add_option("-p", "--prd", dest="prd", help="the prd file")
    parser.add_option("-a", "--att", dest="att", help="the att file")

    parser.add_option("-o", "--output", dest="output",
                  help="write out to DIR")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose")
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose")

    (options, remainder) = parser.parse_args()

    input = open(options.input, 'r')

    index = 0
    session = []
    sname = ''

    pdb = load_prds(options.prd, options.att)

    label = 'Fixation duration'
    fig = plt.figure()
    fig.suptitle(label)
    id = 0
    hit = False

    dm = {}
    for i in range(1, 5):
        dm[i] = {}
        for j in range(1, 5):
            dm[i][j] = {}
            for t in ['+', '-', '=']:
                dm[i][j][t] = 0

    for line in input:
        line = line.strip()
        if index == 0: # header
            index += 1
            # print line
            continue

        items = line.strip().split(',')
        if items[0].startswith("Session"): # session begin

            if len(items[-1]) > 5:
                cpids = items[-1].split('::')
                hit = True

            else:
                hit =False

            if len(session) > 0: # WARNING: 1st session
                # process session
                sid = int(sname[8:])

                # if sid == 9:
                #     continue


                # if id > 20:
                #     break

                # if id <= 20:
                #     continue
                # if id > 40:
                #     break

                # if id not in [41, 42, 43]:
                #     continue
                # if sid != 9:



                # print '%d,%s' % (sid, sname),
                id += 1
                if not parse_session(session, pdb, id, sid, sname, dm):
                    id -= 1



            if hit:
                session = [items] # append the first record for the next sesssion
                sname = items[0]
            else:
                session = []

        if hit:
            if not items[0].startswith("Session"):
                session.append(items)

            #print line
    pprint.pprint(dm)

    for c in dm.keys():
        for l in dm[c].keys():
            for t in ['+', '-', '=']:
                print '%d\t' % dm[c][l][t],
            print
        print

    fig = plt.figure(frameon=False)

    # ax = plt.subplot(43, 1, 42)


    for i in range(1, 5):
        ax = fig.add_subplot(1, 4, i)
        ax.axis('off')
        t = 'red:\t%d ($\uparrow$: %d; $\downarrow$: %d; $=$: %d)' % (sum([dm[i][1][k] for k in dm[i][1].keys()]),
                    dm[i][1]['+'], dm[i][1]['-'], dm[i][1]['='])
        t += '\nblue:\t%d ($\uparrow$: %d; $\downarrow$: %d; $=$: %d)' % (sum([dm[i][2][k] for k in dm[i][2].keys()]),
                    dm[i][2]['+'], dm[i][2]['-'], dm[i][2]['='])
        t += '\nblack:\t%d ($\uparrow$: %d; $\downarrow$: %d; $=$: %d)' % (sum([dm[i][3][k] for k in dm[i][3].keys()]),
                    dm[i][3]['+'], dm[i][3]['-'], dm[i][3]['='])
        t += '\nyellow:\t%d ($\uparrow$: %d; $\downarrow$: %d; $=$: %d)' % (sum([dm[i][4][k] for k in dm[i][4].keys()]),
                    dm[i][4]['+'], dm[i][4]['-'], dm[i][4]['='])
        ax.text(0, 0, t,
                bbox={'facecolor':'red', 'alpha':0.5, 'pad':1})
        # plt.annotate(
        #     'red: ',
        #     xy = (x, 0), xytext = (-20, 20),
        #     textcoords = 'axes points', ha = 'right', va = 'bottom',
        #     bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5)
        #     )
    # ax.axis([0, 4, 0, 18])
    plt.show()

if __name__ == '__main__':
    main()
