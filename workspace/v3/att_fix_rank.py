#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
Copyright (c) 2014 Feng Wang <wangfelix87@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

import sys, os

import numpy as np

from optparse import OptionParser

from utils import *
from data import *

from constraint import *

def zip(a):
    list = []
    for i, x in enumerate(a):
        for j, y in enumerate(a):
            if i == j: continue
            list.append((x, y))
    return list

def kendall(x, y):
    count = 0.0
    pairs = zip(x.keys())
    match = 0.0
    for f, s in pairs:
        x1 = x[f]
        x2 = x[s]

        y1 = y[f]
        y2 = y[s]

        if x1 != x2:
            if (x1 - x2) * (y1 - y2) > 0:
                match += 1
            count += 1.0
    # if count == 0:
    #     print x
    #     print y
    #     print 'OOOOP'
    #     return 0.0
    return match/count




def filter_skyline(pid, pids, pdb):
    new_pids = []
    prd = pdb[pid]
    for id in pids:
        id = id.strip()
        if len(id) == 0: continue
        cp = pdb[id.strip()]
        for k in value_keys:
            if k in ['price', 'weight']:
                if cp[k] > prd[k]:
                    new_pids.append(id)
                    break
            else:
                if cp[k] < prd[k]:
                    new_pids.append(id)
                    break

    return new_pids

def main():
    usage = "usage prog [options] arg"
    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--session", dest="session_file",
        help="the input file")
    parser.add_option("-p", "--prds", dest="prds_file",
        help="the product file")
    parser.add_option("-a", "--att", dest="atts_file",
        help="the att file")

    parser.add_option('-f', "--fix", dest="fix", help="the fixation data")
    # parser.add_option('-f', "--fixation", dest="fixation",
    #     help="the fixation folder")
    # parser.add_option("-o", "--output", dest="output",
    #               help="write out to DIR")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose")
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose")

    (options, remainder) = parser.parse_args()

    atts = load_atts(options.atts_file)
    print 'att: %d' % len(atts)

    prds = load_prds(options.prds_file, atts)
    print 'prds: %d' % len(prds)

    for k in value_keys:
        at = atts[k]
        at['max'] = 0.0
        at['min'] = 10000

    for pid, prd in prds.items():
        for k in value_keys:
            v = prd[k]
            at = atts[k]
            if v > at['max']:
                at['max'] = v
            if v < at['min']:
                at['min'] = v
    for k in value_keys:
        at = atts[k]
        at['range'] = at['max'] - at['min']

    # pprint.pprint(atts)


    output = open('crit_perform_attfix_%s.txt' % (options.fix), 'w')

    hits = {}
    ground_hits = {}
    pred_hits = {}

    valids = 0

    for line in open(options.session_file, 'r'):
        items = line.strip().split(',')
        crit_pid = items[2]
        viewed_pids = items[23].split('::')
        disp_pids = items[-4].split('::')
        # freq_ranked_pids = items[-3].split('::')
        # ds_ranked_pids = items[-2].split('::')
        # avg_ranked_pids = items[-1].split('::')

        crits = items[24:34]
        fix_freqs = [int(x) for x in items[3:13]]
        fix_ds = [int(x) for x in items[13:23]]

        new_crits = []
        new_fix_freqs = {}
        new_fix_ds = {}
        j = 0
        for i, k in enumerate(att_keys):
            if k in value_keys:
                if k == 'display_size': continue

                new_crits.append(crits[i].strip())
                new_fix_freqs['w%d' % j] = fix_freqs[i]
                new_fix_ds['w%d' % j] = fix_ds[i]
                j += 1

        crits = new_crits
        fix_freqs = new_fix_freqs
        fix_ds = new_fix_ds

        fix = options.fix
        if fix == 'dur':
            fixes = fix_ds
        elif fix == 'avg':
            fixes = {}
            for k in new_fix_freqs.keys():
                freq = new_fix_freqs[k]
                # print '%.3f:%.3f' % (freq, new_fix_ds[k])
                if freq > 0:
                    fixes[k] = new_fix_ds[k] / (freq + 0.0)
                else:
                    fixes[k] = 0.0
        else:
            fixes = fix_freqs

        ats = order_dict(fixes)[::-1]
        print ats
        preds = ['='] * 7
        for i, a in enumerate(ats):
            ai = int(a[-1])
            # ak = value_keys[ai]
            #
            # ow.append(ak)
            if i <= 1:
                preds[ai] = '='
            elif i >= 4:
                preds[ai] = '-'
            else:
                preds[ai] = '+'

        auc = 0
        for i in range(len(crits)):
            gt = crits[i]
            pt = preds[i]
            if crits[i] == preds[i]:
                auc += 1
                if gt not in hits: hits[gt] = 0.0
                hits[gt] += 1.0
            if gt not in ground_hits: ground_hits[gt] = 0.0
            if pt not in pred_hits: pred_hits[pt] = 0.0

            ground_hits[gt] += 1.0
            pred_hits[pt] += 1
            output.write('(%s|%s) ' % (crits[i], preds[i]))
            print '(%s|%s) ' % (crits[i], preds[i]),
        print ' %d' % auc
        output.write(' %d\n' % auc)

    tp = 0.0
    tr = 0.0
    tf = 0.0

    for t in ['=', '+', '-']:
        p = hits[t]/pred_hits[t]
        r = hits[t]/ground_hits[t]
        f = 2 * (p * r) / (p + r)

        tp += p
        tr += r
        tf += f

        print '%s: p: %.3f, r: %.3f, f1: %.3f' % (t, p, r, f)
        output.write('%s: p: %.3f, r: %.3f, f1: %.3f\n' % (t, p, r, f))
    tp = tp / 3.0
    tr = tr / 3.0
    print 'p: %.3f, r: %.3f, f1: %.3f' % (tp, tr, 2 * (tp * tr) / (tp + tr))
    output.write('p: %.3f, r: %.3f, f1: %.3f\n' % (tp, tr, 2 * (tp * tr) / (tp + tr)))
    hit_ratio = sum([hits[t] for t in ['=', '+', '-']]) / (38 * 7 + 0.0)
    print 'hit ratio: %.3f' % hit_ratio
    output.write("hit_ratio: %.3f" % (hit_ratio))
    output.close()

if __name__ == '__main__':
    main()
