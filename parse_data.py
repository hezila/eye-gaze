#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys, os
import math

from optparse import OptionParser

from utils import *

def process_session(session):
    prd_freqs ={}
    prd_ds = {}

    prd_in ={}
    prd_out = {}

    m = {}
    m['freq'] = 0.0
    m['duration'] = 0.0
    m['indegree'] = 0.0
    m['outdegree'] = 0.0
    m['degree'] = 0.0

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

        d = r[17] # duration
        if pid not in prd_freqs:
            prd_freqs[pid] = 1
            prd_ds[pid] = d
        else:
            prd_freqs[pid] += 1
            prd_ds[pid] += d

        critique_pid = r[31] # critiqued product

        if len(critique_pid) > 0: # the last line
            if critique_pid not in pids:
                m['freq'] = 0.0
                m['duration'] = 0.0
                m['indegree'] = 0.0
                m['outdegree'] = 0.0
                m['degree'] = 0.0
                return m


            # fixation freq
            orders = order_dict(prd_freqs)[::-1]
            l = ['%s:%d' % (k, prd_freqs[k]) for k in orders]
            m['freq'] = 1.0 / (orders.index(critique_pid) + 1.0)



            # fixatuion duration
            orders = order_dict(prd_ds)[::-1]
            l = ['%s' % (k) for k in orders]
            m['duration'] = 1.0 / (orders.index(critique_pid) + 1.0)


            # indgree
            orders = order_dict(prd_in)[::-1]
            l = ['%s:%d' % (k, prd_in[k]) for k in orders]
            m['indegree'] = 1.0 / (orders.index(critique_pid) + 1.0)


            # outdegree
            orders = order_dict(prd_out)[::-1]
            l = ['%s:%d' % (k, prd_out[k]) for k in orders]
            m['outdegree'] = 1.0 / (orders.index(critique_pid) + 1.0)

            prd_inout = {}
            for p in pids:
                if p not in prd_in:
                    s = 0.0
                else:
                    s = prd_in[p]
                if p not in prd_out:
                    o = 0.0
                else:
                    o = prd_out[p]
                prd_inout[p] = (math.log(s+2.0) + .0)/(math.log(o+2.0) + .0)

            orders = order_dict(prd_inout)[::-1]
            m['degree'] = 1.0/ (orders.index(critique_pid) + 1.0)


            # print '[%s] -> %s' % (', '.join(l), critique_pid)


            #m = 1.0 / (orders.index(critique_pid) + 1.0)
            return m



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
    m_scores['indegree'] = 0.0
    m_scores['outdegree'] = 0.0
    m_scores['degree'] = 0.0
    m_count = 0
    for line in input:
        if index == 0: # header
            index += 1
            continue

        items = line.strip().split(',')
        if items[0].startswith("Session"): # session begin

            if len(session) > 0:
                m = process_session(session)
                if m is not None:
                    for mk in m:
                        m_scores[mk] += m[mk]

                    m_count += 1
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
    print "#############################"
    print 'Critique count: %d' % m_count
    print "MAP: %.3f\t%.3f\t%.3f\t%.3f\t%.3f" % (m_scores['freq']/m_count,
                            m_scores['duration']/m_count,
                            m_scores['indegree']/m_count,
                            m_scores['outdegree']/m_count,
                            m_scores['degree']/m_count)

if __name__ == '__main__':
    main()
