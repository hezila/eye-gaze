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
