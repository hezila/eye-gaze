#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys, os
import math

from optparse import OptionParser

from utils import *

att_keys = ['price', 'manufacture', 'operating_system',
            'battery_life', 'display_size', 'hard_drive',
            'memory', 'processor_class', 'processor_speed',
            'weight']

def process_session(session):
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

            print '\t'.join(critiques)
            print '%s' % ('\t'.join([str(att_freqs[x]) for x in att_keys]))
            print '%s' % ('\t'.join(['%.2f' % att_ds[x] for x in att_keys]))
            print '%s' % ('\t'.join(['%.2f' % (att_ds[x]/(att_freqs[x] + 0.001)) for x in att_keys]))
            print






            # fixation freq
            orders = order_dict(prd_freqs)[::-1]
            # l = ['%s:%d' % (k, prd_freqs[k]) for k in orders]
            # m['freq'] = 1.0 / (orders.index(critique_pid) + 1.0)

            print orders
            print '<>>>>>>>>>'

            # fixatuion duration
            orders = order_dict(prd_ds)[::-1]
            l = ['%s' % (k) for k in orders]
            m['duration'] = 1.0 / (orders.index(critique_pid) + 1.0)

            return None


        best_select_pid = r[29] # best or selected product

        final_pid = r[-5]
        target_pid = r[-4]
    return None

def main():
    usage = "usage prog [options] arg"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--input", dest="input",
        help="the input file")
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


    for line in input:
        if index == 0: # header
            index += 1
            continue

        items = line.strip().split(',')
        if items[0].startswith("Session"): # session begin

            if len(session) > 0:
                result = process_session(session)

                print 'session'

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

if __name__ == '__main__':
    main()
