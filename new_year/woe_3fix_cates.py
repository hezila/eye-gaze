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
import numpy as np

import scipy.stats

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


def parse_session(session, pdb, sid, sname, woes, crit_counts):
    if sid in [9, 19, 73, 89, 90]:
        return False
    # print '%d,%s' % (sid, sname),

    stype = 1
    if sid in [7, 9, 11, 14, 17, 19, 23, 27, 31, 33,
                37, 39, 50, 53, 55, 60, 64, 66, 67,
                68, 70, 71, 73, 74, 88, 89, 90, 93]:
        stype = 3


    viewed_pids = []
    critiqued_pid = session[-1][31] # the last one
    displayed_pids = []

    fix_freqs = {}
    fix_ds = {}
    fix_count = {}
    for k in att_keys:
        fix_freqs[k] = 0
        fix_ds[k] = 0
        fix_count[k] = 0


    cts = {}
    cts_types = {}

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
                fix_count[ak] = 1.0
            else:
                fix_freqs[ak] += 1.0
                fix_ds[ak] += d
                fix_count[ak] += 1

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

    # print ',%s,' % critique_pid,

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
    # fix_levels = group_levels(fix_freqs, 3)

    # avg
    new_fixs = {}
    # fcount = sum(fix_count.values()) + 0.0

    # for k in fix_freqs:
    #     new_fixs[k] = fix_freqs[k] / fcount

    for k in fix_freqs:
        if fix_freqs[k] > 0:
            new_fixs[k] = fix_ds[k]/fix_freqs[k]
        else:
            new_fixs[k] = 0.0


    # print new_fixs.values()

    fix_levels = group_2levels(new_fixs, 2)
    # fix_levels = group_2levels(fix_freqs, 2)
    # fix_levels = group_2levels(fix_ds, 2)

    # print [fix_levels[k] for k in fix_levels],
    # print sum(np.array(fix_levels.values()) == 1),
    # print '\t',
    # print sum(np.array(fix_levels.values()) == 2)

    # print '%s,' % ','.join(['%d' % int(fix_freqs[k]) for k in att_keys]),
    # print '%s,' % ','.join(['%d' % int(fix_ds[k]) for k in att_keys]),
    # print '%s,' % '::'.join(viewed_pids)

    for k in att_keys:

        cl = v_levels[k]
        ct = cts_types[k]
        fl = fix_levels[k]

        # cm -> crit
        # if k in value_keys:
        #     woes['cm_crit'][cl][ct] += 1
        woes['cm_crit'][cl][ct] += 1

        # fix -> crit
        woes['fix_crit'][fl][ct] += 1
        woes['crit_cm'][ct][cl] += 1

        # fix -> cm
        # if k in value_keys:
        #     woes['fix_cm'][fl][cl] += 1
        #     # fix, cm -> crit
        #     woes['fix_cm_crit'][fl][cl][ct] += 1

        woes['fix_cm'][fl][cl] += 1
        woes['fix_cm_crit'][fl][cl][ct] += 1

        if k in value_keys:
            crit_counts[ct]['num'] += 1
        else:
            crit_counts[ct]['cate'] += 1


    return True

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

    id = 0
    hit = False

    woes = {}

    # cm -> critique
    cm_crit_woe = {}
    for cl in [1, 2, 3, 4]:
        cm_crit_woe[cl] = {}
        for ct in ['=', '+', '-']:
            cm_crit_woe[cl][ct] = 0

    woes['cm_crit'] = cm_crit_woe

    # fix -> critique
    fix_crit_woe = {}
    for fl in [1, 2, 3]:
        fix_crit_woe[fl] = {}
        for ct in ['=', '+', '-']:
            fix_crit_woe[fl][ct] = 0

    woes['fix_crit'] = fix_crit_woe

    # critique -> cm
    crit_cm_woe = {}
    for ct in ['=', '+', '-']:
        crit_cm_woe[ct] = {}
        for cl in [1, 2, 3, 4]:
            crit_cm_woe[ct][cl] = 0
    woes['crit_cm'] = crit_cm_woe

    # fix -> cm
    fix_cm_woe = {}
    for fl in [1, 2, 3]:
        fix_cm_woe[fl] = {}
        for cl in [1, 2, 3, 4]:
            fix_cm_woe[fl][cl] = 0

    woes['fix_cm'] = fix_cm_woe


    fix_cm_ct_woe = {}
    for fl in [1, 2, 3]:
        fix_cm_ct_woe[fl] = {}
        for cl in [1, 2, 3, 4]:
            fix_cm_ct_woe[fl][cl] = {}
            for ct in ['=', '+', '-']:
                fix_cm_ct_woe[fl][cl][ct] = 0
    woes['fix_cm_crit'] = fix_cm_ct_woe

    crit_counts = {}

    for ct in ['=', '+', '-']:
        crit_counts[ct] = {}
        crit_counts[ct]['num'] = 0
        crit_counts[ct]['cate'] = 0

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

                id += 1
                if not parse_session(session, pdb, sid, sname, woes, crit_counts):
                    id -= 1



            if hit:
                session = [items] # append the first record for the next sesssion
                sname = items[0]
            else:
                session = []

        if hit:
            if not items[0].startswith("Session"):
                session.append(items)


    print 'WOE'
    cm_labels = ['better than all', 'better than some', 'worse than all', 'category']
    fix_labels = ['high', 'low', 'zero']

    # num_count = 0.0
    # for ct in ['=', '+', '-']:
    #     num_count += crit_counts[ct]['num']
    num_count = 380.0

    for ct in ['=', '+', '-']:

        woe = woes['cm_crit']
        for cl in [1, 2, 3, 4]:
            print 'woe(%s | %s) = ' % (ct, cm_labels[cl-1]),
            ph = (crit_counts[ct]['num'] + crit_counts[ct]['cate'])/num_count

            count = woe[cl]['='] + woe[cl]['+'] + woe[cl]['-'] + 0.0

            phe = woe[cl][ct]/count

            ohe = phe/(1.0 - phe)
            oh = ph/(1.0 - ph)
            w = math.log(ohe/oh)
            print '%.3f, %.3f' % (phe, w)

        print

        woe = woes['fix_crit']
        for fl in [1, 2, 3]:
            print 'woe(%s | %s) = ' % (ct, fix_labels[fl-1]),
            ph = (crit_counts[ct]['num'] + crit_counts[ct]['cate'])/380.0

            count = woe[fl]['='] + woe[fl]['+'] + woe[fl]['-'] + 0.0

            phe = woe[fl][ct]/count

            ohe = phe/(1.0 - phe)
            oh = ph/(1.0 - ph)
            w = math.log(ohe/oh)
            print '%.3f, %.3f' % (phe, w)
        print

    woe = woes['crit_cm']
    for cl in [1, 2, 3, 4]:
        cl_count = sum([woe[ct][cl] for ct in ['=', '+', '-']]) + 0.0
        ph = cl_count/(38.0 * 7)
        for ct in ['=', '+', '-']:
            print 'woe(%s | %s) = ' % (cm_labels[cl-1], ct),

            count = woe[ct][1] + woe[ct][2] + woe[ct][3] + woe[ct][4] + 0.0
            phe = woe[ct][cl] / count

            ohe = phe / (1.0 - phe)
            oh = ph / (1.0 - ph)
            w = math.log(ohe/oh)
            print '%.3f, %.3f' % (phe, w)

    woe = woes['fix_cm']
    for cl in [1, 2, 3, 4]:
        cl_count = sum([woe[fl][cl] for fl in [1, 2, 3]]) + 0.0
        ph = cl_count/(38.0 * 7)
        for fl in [1, 2, 3]:
            print 'woe(%s | %s) = ' % (cm_labels[cl-1], fix_labels[fl-1]),

            count = woe[fl][1] + woe[fl][2] +  woe[fl][3] + woe[fl][4] + 0.0
            phe = woe[fl][cl]/count

            ohe = phe/(1.0 - phe)
            oh = ph/(1.0 - ph)
            w = math.log(ohe/oh)
            print '%.3f, %.3f' % (phe, w)
        print

    woe = woes['fix_cm_crit']
    for fl in [1, 2, 3]:
        for cl in [1, 2, 3, 4]:
            count = woe[fl][cl]['='] + woe[fl][cl]['+'] + woe[fl][cl]['-'] + 0.0
            for ct in ['=', '+', '-']:
                print 'woe(%s | %s & %s) = ' % (ct, cm_labels[cl-1], fix_labels[fl-1]),
                ph = (crit_counts[ct]['num'] + crit_counts[ct]['cate'])/num_count

                # print '%.3f, ' % ph,

                phe = woe[fl][cl][ct]/count
                if phe <= 0.0001:
                    print '#Nan'
                    continue
                # print '%.3f, ' % phe,

                ohe = phe/(1.0 - phe)
                oh = ph/(1.0 - ph)
                w = math.log(ohe/oh)
                print '%.3f, %.3f' % (phe, w)
            print
        print
    print


if __name__ == '__main__':
    main()
