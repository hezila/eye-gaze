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

import random

att_keys = ['price', 'manufacturer', 'operating_system',
            'battery_life', 'display_size', 'hard_drive_capacity',
            'installed_memory', 'processor_class', 'processor_speed',
            'weight']

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

am = {}
for a in att_keys:


    m = {}

    for i in range(6):
        m[i] = {}
        for j in range(4):
            m[i][j] = []
    am[a] = m

tm = {}

for i in range(5):
    tm[i] = {}
    for j in range(4):
        tm[i][j] = {}
        for o in ['+', '-', '=', 'a']:
            tm[i][j][o] = 0


def process_session(session, pids, pdb):
    # print pids
    # print '>>>>>> %d' % len(pids)
    # print pids
    prds = [pdb[pid] for pid in pids if len(pid)> 0]

    prd_freqs ={}
    prd_ds = {}

    prd_in ={}
    prd_out = {}

    m = {}
    m['freq'] = 0.0
    m['duration'] = 0.0
    m['avg_freq'] = 0.0
    m['indegree'] = 0.0
    m['outdegree'] = 0.0
    m['degree'] = 0.0

    att_freqs = {}
    att_ds = {}

    for x in att_keys:
        att_freqs[x] = 0.0
        att_ds[x] = 0.0

    n = {}
    n['freq'] = 0.0
    n['ds'] = 0.0
    n['avg'] = 0.0

    vp = 0.0
    vpc = 0.0
    vnp = 0.0
    vnpc = 0.0

    zero_crit = 0.0
    zero_keep = 0.0
    zero_any = 0.0
    zeros = 0.0

    keep_zero = 0.0
    keeps = 0.0



    pre_pid = None
    pids = []
    for r in session:
        pid = r[2] # pid
        if pid not in pids:
            pids.append(pid)

        if pre_pid is None:
            #prd_in[pid] = 1
            pass
        else:
            if pid not in prd_in:
                prd_in[pid] = 1
            else:
                prd_in[pid] += 1

            if pre_pid not in prd_out:
                prd_out[pre_pid] = 1
            else:
                prd_out[pre_pid] += 1

        pre_pid = pid

        d = float(r[17]) # duration
        if pid not in prd_freqs:
            prd_freqs[pid] = 1
            prd_ds[pid] = d
        else:
            prd_freqs[pid] += 1
            prd_ds[pid] += d


        att_fixated = r[5:15]


        if '1' in att_fixated:
            fi = att_fixated.index('1')
            ak = att_keys[fi]

            if ak not in att_freqs:
                att_freqs[ak] = 1.0
                att_ds[ak] = d
            else:
                att_freqs[ak] += 1.0
                att_ds[ak] += d


        critique_pid = r[31] # critiqued product

        if len(critique_pid) > 0: # the last line
            critiques = r[19:29]

            crits = []
            for ci, c in enumerate(critiques):
                if c.startswith('<>'):
                    crits.append(1)
                elif c.startswith('<'):
                    crits.append(1)
                elif c.startswith('>'):
                    crits.append(1)
                elif c.startswith('any'):
                    if att_freqs[att_keys[ci]] < 0.001:
                        vp += 1.0
                    vpc += 1.0
                else:
                    crits.append(0)

                ck = att_keys[ci]

                if len(c.strip()) == 0:
                    keeps += 1.0
                    if att_freqs[ck] <= 0.001:
                        keep_zero += 1.0


                if att_freqs[ck] <= 0.001:
                    zeros += 1.0
                    if c.startswith('any'):
                        zero_any += 1.0
                    elif len(c.strip()) == 0:
                        zero_keep += 1.0
                    else:
                        zero_crit += 1

            for ai, ak in enumerate(att_keys):
                if att_freqs[ak] < 0.001:
                    vnpc += 1.0
                    if critiques[ai] == 'any':
                        vnp += 1.0

            freq_orders = order_dict(att_freqs)[::-1]
            ds_orders = order_dict(att_ds)[::-1]

            att_avgs = {}
            for ak in att_keys:
                if att_freqs[ak] < 0.0001:
                    att_avgs[ak] = 0.0
                else:
                    att_avgs[ak] = att_ds[ak]/att_freqs[ak]

            avg_orders = order_dict(att_avgs)[::-1]
            for ci, cv in enumerate(crits):
                if cv != 0:
                    k = att_keys[ci]
                    rank = freq_orders.index(k) + 1
                    n['freq'] += 1.0/rank

                    rank = ds_orders.index(k) + 1
                    n['ds'] += 1.0/rank

                    rank = avg_orders.index(k) + 1
                    n['avg'] += 1.0/rank

            # print '%s' % ('\t'.join(att_keys))
            # print '\t'.join(critiques)
            # print '%s' % ('\t'.join([str(att_freqs[x]) for x in att_keys]))


            # print '%s' % ('\t'.join(['%.2f' % att_ds[x] for x in att_keys]))
            # print '%s' % ('\t'.join(['%.2f' % (att_ds[x]/(att_freqs[x] + 0.001)) for x in att_keys]))
            # print






            # fixation freq
            att_freqs = att_ds
            orders = order_dict(att_freqs)[::-1]



            # l = ['%s:%d' % (k, prd_freqs[k]) for k in orders]
            # m['freq'] = 1.0 / (orders.index(critique_pid) + 1.0)

            # print '\t'.join(orders)

            critiques = r[19:29]
            cts = {}

            for ci, c in enumerate(critiques):
                cts[att_keys[ci]] = c
            # print cts

            top = prds[0]
            last_level = 3
            last_freq = 0
            ls = group_levels(att_freqs, 3)
            cates = ['manufacturer', 'operating_system',
                        'processor_class'
                    ]
            for i, o in enumerate(orders):
                if o not in cates:
                    continue
                fix_level = ls[o]
                # if dist[i] >= 1.0/3:
                #     fix_level = 1
                # elif dist[i] >= .5/3 and dist[i] > 0:
                #     fix_level = 2
                # elif dist[i] > 0:
                #     fix_level = 3
                # else:
                #     fix_level = 4


                # fix_level = 3
                # if i <= 1 and att_freqs[o] > 0:
                #     fix_level = 1
                #     last_level = 1
                #     last_freq = att_freqs[o]
                #
                # elif i > 1 and i <= 3 and att_freqs[o] > 0:
                #     fix_level = 2
                #     if att_freqs[o] == last_freq:
                #         fix_level = last_level
                #     else:
                #         fix_level = 2
                #         last_level = 2
                #         last_freq = att_freqs[o]
                #
                # elif i > 3 and i <= 5 and att_freqs[o] > 0:
                #     fix_level = 3
                #     if att_freqs[o] == last_freq:
                #         fix_level = last_level
                #     else:
                #         fix_level = 3
                #         last_level = 3
                #         last_freq = att_freqs[o]
                #
                # elif i > 5 and i <= 7 and att_freqs[o] > 0:
                #     fix_level = 4
                #     if att_freqs[o] == last_freq:
                #         fix_level = last_level
                #     else:
                #         fix_level = 4
                #         last_level = 4
                #         last_freq = att_freqs[o]
                #
                # elif att_freqs[o] > 0:
                #     fix_level = 5
                # else:
                #     fix_level = 6


                prds = [pdb[pid] for pid in pids if len(pid)> 0]

                # print 'prds: %d' % len(prds)

                value_levels = [0, 0, 0]
                av = top[o]

                for v in [p[o] for p in prds[1:]]:
                    if av >= v:
                        value_levels[0] += 1
                    elif av < v:
                        value_levels[2] += 1

                if value_levels[0] == (len(prds) - 1):
                    v_level = 1
                elif value_levels[2] == (len(prds) - 1):
                    v_level = 3
                else:
                    v_level = 2

                v_level = 1


                c = cts[o]

                if c.startswith("<>"):
                    ctype = '+'
                elif c.startswith("any"):
                    ctype = 'a'
                elif c.startswith('>'):
                    if o in ['price', 'weight']:
                        ctype = '-'
                    else:
                        ctype = '+'
                elif c.startswith('<'):
                    if o in ['price', 'weight']:
                        ctype = '+'
                    else:
                        ctype = '-'
                else:
                    ctype = '='

                # print '%s -> %d -> %d -> %s' % (o, fix_level, v_level, ctype)

                am[o][fix_level][v_level].append(ctype)
                tm[fix_level][v_level][ctype] += 1            # print '<>>>>>>>>>'


            return None


        best_select_pid = r[29] # best or selected product

        final_pid = r[-5]
        target_pid = r[-4]
    return None
def draw_sub(array, color='rby'):
    for i, n in enumerate(array):
        lx = 2.5
        ly = 2.5

        tx = 20
        ty = 20

        if i == 1:
            lx = -lx
            tx = -tx
        elif i == 2:
            ly = -ly
            lx = 0

            ty = -ty

        plt.annotate(
            '%d' % n,
            xy = (lx, ly), xytext = (tx, ty),
            textcoords = 'offset points', ha = 'right', va = 'bottom',
            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
            arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

        for j in range(n):
            x = random.random() * 5
            y = random.random() * 5

            if i == 1:
                x = -x
            elif i == 2:
                y = -y
                if random.random() > 0.5:
                    x = -x

            plt.plot(x, y, 'o%s' % color[i])



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
    user_sessions = {}
    index = 0
    session = []
    m_scores = {}
    m_scores['freq'] = 0.0
    m_scores['duration'] = 0.0
    m_scores['avg_freq'] = 0.0
    m_scores['indegree'] = 0.0
    m_scores['outdegree'] = 0.0
    m_scores['degree'] = 0.0
    m_count = 0

    n_scores = {}
    n_scores['freq'] = 0.0
    n_scores['ds'] = 0.0
    n_scores['avg'] = 0.0

    total_p = 0.0
    total_pc = 0.0
    total_np = 0.0
    total_npc = 0.0


    total_zero_crit = 0.0
    total_zero_keep = 0.0
    total_zero_any = 0.0

    total_zeros = 0.0

    total_keep_zero = 0.0
    total_keeps = 0.0

    # print options.prd
    # print options.att
    pdb = load_prds(options.prd, options.att)

    for line in input:
        if index == 0: # header
            index += 1
            continue

        items = line.strip().split(',')
        if items[0].startswith("Session"): # session begin

            if len(items[-1]) > 5:
                cpids = items[-1].split('::')
            else:
                continue

            if len(session) > 0:
                result = process_session(session, cpids, pdb)

                # print 'session'

                if uid not in user_sessions:
                    user_sessions[uid] = [session]
                else:
                    user_sessions[uid].append(session)

                session = [items]

            else:
                session.append(items) # the first session
        else:
            session.append(items)

        uid = items[-3]

    result = process_session(session, cpids, pdb) # the last session

    pprint.pprint(tm)

    axs = []
    vts = ['+', '-', '=']
    labels = ['better than all', 'better than some', 'worse than all']
    # label = 'Fixation durations & numerical attributes (red: improvement; blue: compromise; yellow: keep)'
    label = 'Fixation duration & category attributes (red: improvement; blue: compromise; yellow: keep)'
    fig = plt.figure()
    fig.suptitle(label)
    for i in range(1, 5):
        for j in range(1, 4):
            # print 531 + i * 3 + j
            ax = plt.subplot(4,1, i)
            # axs.append(ax)

            # plt.sca(ax)
            if j == 1:
                ax.set_yticklabels(['','','', 'level %d' % i,'',''])
            else:
                ax.set_yticklabels(['','','','',''])
            if i == 4:
                ax.set_xticklabels(['', '','','','category attributes','',''])
            else:
                ax.set_xticklabels(['','',''])


            # n = [tm[i][c][vts[j-1]] for c in range(1,4)]
            # # n[1] += tm[i][]['a']
            # for c in range(1, 4):
            #     n[c-1] += tm[i][c]['a']


            n = [tm[i][j][v] for v in vts]
            n[1] += tm[i][j]['a']


            draw_sub(n)
            break

    plt.show()


if __name__ == '__main__':
    main()
