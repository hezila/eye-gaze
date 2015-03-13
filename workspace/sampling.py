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

from pulp import *
import pprint

def u(w, values):
    s = 0.0
    for i, v in enumerate(values):
        s += w[i] * v
    return s

def skyline(prd, cm_prds, atts):
    for p in cm_prds:
        c = 0
        for k in value_keys:
            if k in ['price', 'weight']:
                if prd[k] < p[k]: c += 1
            else:
                if prd[k] > p[k]: c += 1
        if c == len(value_keys): return True
    return False

def check(w, prd, cm_prds, atts):
    cs = prd_scores(prd, atts)
    pu = u(w, cs)
    for p in cm_prds:
        vs = prd_scores(p, atts)
        vu = u(w, vs)
        if pu < vu:
            return False
    return True
def lp(prd, cm_prds, atts):
    cs = prd_scores(prd, atts)

    prob = LpProblem('top_rank', LpMaximize)

    w = [LpVariable('w%d' % i, lowBound = 0.0) for i in range(7)]
    #
    # w1 = LpVariable('w1', lowBound = 0)
    # w2 = LpVariable('w2', lowBound = 0)
    # z = LpVariable('z', lowBound = 0)

    # prob += w[0] + w[1] + w[2] + w[3] + w[4] + w[5] + w[6] <= 1.0
    # prob += w[0] + w[1] + w[2] + w[3] + w[4] + w[5] + w[6] >= 1.0
    prob += w[0] + w[1] + w[2] + w[3] + w[4] + w[5] + w[6] == 1.0


    difs = [0]*7
    for vprd in cm_prds:

        vs = prd_scores(vprd, atts)

        dfs = [cs[i]-vs[i] for i in range(7)]
        for i in range(7):
            difs[i] += dfs[i]

        prob += w[0] * dfs[0] + w[1]*dfs[1] + w[2]*dfs[2] + w[3]*dfs[3] + w[4]*dfs[4] + w[5]*dfs[5] + w[6] * dfs[6]  >= 0.0001

    prob += w[0]*difs[0] + w[1]*difs[1] + w[2]*difs[2] + w[3]*difs[3] + w[4]*difs[4] + w[5]*difs[5] + w[6]*difs[6]
    prob += w[0] * cs[0] + w[1]*cs[1] + w[2]*cs[2] + w[3]*cs[3] + w[4]*cs[4] + w[5]*cs[5] + w[6]*cs[6]
    # prob.writeLP("problem.lp")
    # print prob
    # print

    GLPK().solve(prob)
    # status = prob.solve(GLPK(msg = 0))
    w = []
    for v in prob.variables():
        print v.name, '=', v.varValue
        w.append(v.varValue)
    return w

def main():
    usage = "usage prog [options] arg"
    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--session", dest="session_file",
        help="the input file")
    parser.add_option("-p", "--prds", dest="prds_file",
        help="the product file")
    parser.add_option("-a", "--att", dest="atts_file",
        help="the att file")
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

    for line in open(options.session_file, 'r'):
        items = line.split(',')
        crit_pid = items[2]
        viewed_pids = items[23].split('::')
        prd = prds[crit_pid]
        cm_prds = [prds[pid.strip()] for pid in viewed_pids]
        print 'SKYLINE: ' + str(skyline(prd, cm_prds, atts))
        w = lp(prd, cm_prds, atts)
        a = np.array(w)
        if sum(a) == 0:
            continue
        ws = []
        count = 0
        while len(ws) <= 10000 and count < 1000000:
            w = np.random.dirichlet(a)
            if check(w, prd, cm_prds, atts):
                ws.append(w)
                print '.',
            count += 1


        print 'len: %d' % len(ws)

if __name__ == '__main__':
    main()
