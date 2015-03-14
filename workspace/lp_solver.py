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
        int i = 0

        for j, pid in enumerate(ranked_pids[1:]):
            pi = ranked_pids[i]
            i = j
            cs = prd_scores(prds[pi], atts)

            pid = pid.strip()
            vprd = prds[pid]
            vs = prd_scores(vprd, atts)

            dfs = [cs[i]-vs[i] for i in range(7)]
            for i in range(7):
                difs[i] += dfs[i]

            # prob += w[0] * dfs[0] + w[1]*dfs[1] + w[2]*dfs[2] + w[3]*dfs[3] + w[4]*dfs[4] + w[5]*dfs[5] + w[6] * dfs[6]  >= 0.0001

        prob += w[0]*difs[0] + w[1]*difs[1] + w[2]*difs[2] + w[3]*difs[3] + w[4]*difs[4] + w[5]*difs[5] + w[6]*difs[6]



        GLPK().solve(prob)
        # status = prob.solve(GLPK(msg = 0))

        for v in prob.variables():
            print v.name, '=', v.varValue

if __name__ == '__main__':
    main()
