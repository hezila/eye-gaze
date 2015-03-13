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

import datetime
import math
from itertools import *

def get_date(timestamp):
    """
    Get the date from the timestamp
    :param timestamp: the timestamp
    :returns: the string represention of the date
    """
    value = datetime.datetime.fromtimestamp(timestamp)
    return value.strftime('%Y-%m-%d %H:%M:%S')

def order(x):
    """
    returns the order of each element in x as a list.
    """
    L = len(x)
    rangeL = range(L)
    z = izip(x, rangeL)
    z = izip(z, rangeL)  # avoid problems with duplicates.
    D = sorted(z)
    return [d[1] for d in D]


def order_dict(d):
    """
    returns the order of each item in d as a dict
    """
    k_list = []
    v_list = []
    for k, v in d.items():
        k_list.append(k)
        v_list.append(v)

    orders = order(v_list)
    return [k_list[o] for o in orders]


def rank(x):
    """
    Returns the rankings of elements in x as a list.
    """
    L = len(x)
    ordering = order(x)
    ranks = [0] * len(x)
    for i in range(L):
        ranks[ordering[i]] = i
    return ranks


def group_2levels(x, n=2):
    ls = {}
    for k in x.keys():
        ls[k] = 3

    values = [x[k] for k in x.keys() if x[k] > 0]
    keys = [k for k in x.keys() if x[k] > 0]

    if len(values) == 0:
        return ls

    ovalues = {}
    for k in keys:
        ovalues[k] = x[k]

    orders = order_dict(ovalues)[::-1]

    if len(keys) <= 2:
        o1 = orders[0]
        ls[o1] = 1
        o2 = orders[-1]
        if len(keys) == 2:
            if ovalues[o1] - ovalues[o2] > 1:
                ls[o2] = 2
            else:
                ls[o2] = 1
    else:
        mx = orders[0]
        mi = orders[-1]

        cks = {}
        cks[1] = [mx]
        cks[2] = [mi]

        centers = {}
        centers[1] = ovalues[mx]
        centers[2] = ovalues[mi]

        changes = 1
        while changes >= 1:
            new_cks = {}
            new_cks[1] = [mx]
            new_cks[2] = [mi]

            changes = 0
            for o in orders[1:-1]:
                best_value = centers[1] - centers[2]

                b = -1
                if o in cks[1]:
                    b = 1
                elif o in cks[2]:
                    b = 2

                d = 1
                for c in range(1, 3):
                    dis = abs(ovalues[o] - centers[c])
                    if dis < best_value:
                        d = c
                        best_value = dis
                if b != d:
                    changes += 1

                new_cks[d].append(o)

            # update centers
            for c in range(1, 3):
                centers[c] = sum(ovalues[k] for k in new_cks[c])/(len(new_cks[c]) + 0.0)
            cks = new_cks

        for c in cks.keys():
            for o in cks[c]:
                ls[o] = c
    return ls



def group_levels(x, n=3):
    ls = {}
    for k in x.keys():
        ls[k] = 4

    values = [x[k] for k in x.keys() if x[k] > 0]
    keys = [k for k in x.keys() if x[k] > 0]
    if len(values) == 0:
        # print ls
        return ls

    ovalues = {}
    for k in keys:
        ovalues[k] = x[k]

    orders = order_dict(ovalues)[::-1]

    if len(keys) <= 3:

        o1 = orders[0]
        ls[o1] = 1
        o3 = orders[-1]
        if len(keys) == 3:
            o2 = orders[1]
            if ovalues[o2] - ovalues[o1] > 1:
                ls[o2] = 2
            else:
                ls[o2] = 1

            if ovalues[o3] - ovalues[o2] > 1:
                ls[o3] = 3
            else:
                ls[o3] = 1
        elif len(keys) == 2:
            if ovalues[o3] - ovalues[o1] > 1:
                ls[o3] = 3
            else:
                ls[o3] = 1
        else:
            ls[orders[0]] = 1

    else:
        mx = orders[0]
        mi = orders[-1]

        # mid = orders[len(orders)/2]

        cks = {}
        cks[1] = [mx]
        cks[3] = [mi]
        cks[2] = orders[1:-1]

        centers = {}
        centers[1] = ovalues[mx]
        centers[3] = ovalues[mi]
        centers[2] = sum([ovalues[k] for k in cks[2]])/(len(cks[2]) + 0.0)

        changes = 1
        while changes >= 1:
            # updater cluster
            new_cks = {}
            new_cks[1] = [mx]
            new_cks[2] = []
            new_cks[3] = [mi]

            changes = 0

            for o in cks[1][1:]:
                best_value = centers[1] - centers[3]
                b = 1
                for c in range(1, 4):
                    dis = abs(ovalues[o] - centers[c])
                    if dis < best_value:
                        b = c
                        best_value = dis
                if b != 1:
                    changes += 1

                new_cks[b].append(o)

            for o in cks[2]:
                best_value = centers[1] - centers[3]
                b = 2
                for c in range(1, 4):
                    dis = abs(ovalues[o] - centers[c])
                    if dis < best_value:
                        b = c
                        best_value = dis
                if b != 2:
                    changes += 1
                new_cks[b].append(o)

            for o in cks[3][1:]:
                best_value = centers[1] - centers[3]
                b = 3
                for c in range(1, 4):
                    dis = abs(ovalues[o] - centers[c])
                    if dis < best_value:
                        b = c
                        best_value = dis
                if b != 3:
                    changes += 1
                new_cks[b].append(o)

            cks = new_cks

            # update centers
            for c in range(1, 4):
                if len(new_cks[c]) == 0:
                    s = new_cks[3][-1]
                    new_cks[3] = new_cks[3][:-1]

                    new_cks[c].append(s)

                if len(new_cks[c]) > 0:
                    centers[c] = sum([ovalues[k] for k in new_cks[c]])/(len(new_cks[c]) + 0.0)

        for c in cks.keys():
            for o in cks[c]:
                ls[o] = c

    return ls



def standard_levels(x, n=3):
    # print x

    ls = {}
    for k in x.keys():
        ls[k] = 4

    values = [x[k] for k in x.keys() if x[k] > 0]
    keys = [k for k in x.keys() if x[k] > 0]
    if len(values) == 0:
        # print ls
        return ls

    mean = reduce(lambda z, y: z+y, values)/(len(values)+0.0)
    sum_variance = 0.0
    for v in values:
        sum_variance += (v - mean) ** 2
    sum_variance = math.sqrt(sum_variance/(len(values) + 0.0))

    if sum_variance > 1:
        ovalues = {}
        for k in keys:
            ovalues[k] = x[k]

        orders = order_dict(ovalues)[::-1]
        factors = [0.33, 0.66]
        p = [i/(len(orders) - 1.0) for i in range(len(orders))]

        l = 0
        for i, o in enumerate(orders):
            if l == len(factors):
                ls[o] = l + 1
                continue

            if p[i] < factors[l]:
                ls[o] = l + 1
            elif p[i] >= factors[l]:
                l += 1
                if abs(x[o] == x[orders[i - 1]]) < sum_variance:
                    ls[o] = ls[orders[i - 1]]
                else:
                    ls[o] = l+1


        # print ls
        return ls

    else:
        for k in keys:
            ls[k] = 1
        # print ls
        return ls

def levels(x, n=3):
    keys = x.keys()
    zeros = []
    for k in x.keys():
        if x[k] == 0:
            zeros.append(k)
            del x[k]


    orders = order_dict(x)[::-1]

    if len(orders) == 0:
        ls = {}
        for o in keys:
            ls[o] = n+1
        return ls
    elif len(orders) == 1:
        ls = {}
        for o in keys:
            ls[o] = n+1
        ls[orders[0]] = 1
        return ls
    elif len(orders) == 2:
        ls = {}
        for o in keys:
            ls[o] = n+1
        ls[orders[0]] = 1
        ls[orders[1]] = 3
        return ls
    elif len(orders) == n:
        ls = {}
        for o in keys:
            ls[o] = n+1
        ls[orders[0]] = 1
        ls[orders[1]] = 2
        ls[orders[2]] = 3
        return ls

    values = [x[o] for o in orders]
    values = []
    for o in orders:
        if len(values) == 0:
            values.append(x[o])
        elif x[o] != values[-1]:
            values.append(x[o])

    p = [i/(len(values)-1.0) for i in range(len(values))]

    if n == 3:
        factors = [0.33, 0.66]
    else:
        factors = [0.2, 0.4, 0.6, 0.8]
    # print p

    q = []
    l = 0
    for i, v in enumerate(p):

        if v > factors[l]:
            q.append((1.0 - factors[l]) * values[i-1] + factors[l] * values[i])
            l += 1
        elif v == factors[l]:
            q.append(values[i])
            l += 1

        if l == len(factors):
            break
    # print p
    print q

    l = 0
    ls = {}
    for i, o in enumerate(orders):
        if l == len(q):
            ls[o] = l + 1
            continue

        if x[o] >= q[l]:
            ls[o] = l + 1
        else:
            l += 1
            ls[o] = l + 1


    for zk in zeros:
        ls[zk] = n + 1

    return ls
