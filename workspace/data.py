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

import xml.etree.ElementTree as ET

try:
    import simplejson as json
except Exception, e:
    import json

att_keys = ["price", "manufacturer", "operating_system", "battery_life",
        "display_size", "hard_drive_capacity", "installed_memory", "processor_class",
        "processor_speed", "weight"]
# value_keys = ["price",  "battery_life",
#         "display_size", "hard_drive_capacity", "installed_memory",
#         "processor_speed", "weight"]

value_keys = ["price",  "battery_life",
         "hard_drive_capacity", "installed_memory",
        "processor_speed", "weight"]


class Session:
    def __init__(self, sid=None, cid=None, selected_id=None, pids=[], prefs={}):
        self.sid = sid
        self.cid = cid # critiqued product ID
        self.selected_id = selected_id # selected product ID
        self.pids = pids # the first one is top (selected) product
        self.prefs = prefs
    def __str__(self):
        return 'sid: %s, cid: %s, selected: %s' % (self.sid, self.cid, self.selected_id)

def load_sessions(filepath, atts):
    sessions = []
    index = 0
    with open(filepath, 'r') as fp:
        for line in fp:
            line = line.strip()
            if index > 0 and len(line) > 0: # skip header
                items = line.split(',')

                sid = items[0]
                selected_id = items[1]
                cid = items[2]

                pids = []
                for pid in items[3].split('::'):
                    if pid not in pids:
                        pids.append(pid)

                prefs_items = items[4:14]
                prefs = {}
                for i, pt in enumerate(prefs_items):
                    atk = att_keys[i]
                    #prefs[atk] = {}
                    p, w = pt.split('::')

                    if p.startswith('all'):
                        cond = 'all'
                        v = -1 # WARNING: to do
                    elif p[1] == '=' or p[1] == '>':
                        cond = p[:2]
                        v = p[2:]
                    else:
                        cond = p[0]
                        v = p[1:]
                    pref = {}
                    if atts[atk]['type'] == 'float':
                        v = float(v)

                    pref['value'] = v
                    pref['cond'] = cond
                    pref['weight'] = float(w)
                    prefs[atk] = pref

                session = Session(sid, cid, selected_id, pids, prefs)
                sessions.append(session)

            index += 1
    return sessions


def load_prds(filepath, atts):
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



def load_atts(filepath):
    doc = json.load(open(filepath, 'r'))
    return doc

def load_fixfreq(filepath):
    lines = open(filepath, 'r')
    for i, line in enumerate(lines):
        if i == 0:
            continue
        items = line.strip().split(',')
        scores = map(lambda x: int(x), items[:10])
        atts = []
        for j, item in enumerate(items[10:]):
            if item != '':
                atts.append(j)
        order_list = order(scores)

def prd_scores(prd, atts):
    prd_scores = []

    for atk in value_keys:
        pv = prd[atk]

        at = atts[atk]

        if atk in ['price', 'weight']:
            s = (at['max'] - pv)/at['range']
        else:
            s = (pv - at['min'])/at['range']
        prd_scores.append(s)

    return prd_scores

def prd_6scores(prd, atts):
    prd_scores = []

    for atk in value_keys:
        if atk == 'display_size': continue
        pv = prd[atk]

        at = atts[atk]

        if atk in ['price', 'weight']:
            s = (at['max'] - pv)/at['range']
        else:
            s = (pv - at['min'])/at['range']
        prd_scores.append(s)

    return prd_scores


def score(atk, spec_value, pref, atts):
    v = pref['value']
    cond = pref['cond']

    att = atts[atk]

    type = att['type']

    # print type
    # print pref
    # print spec_value
    # print

    if type == "string":
        if cond == "all" or cond == '<>': # improvement (equal or "any value")
            return 1.0
        elif cond == '!=':
            if spec_value != v:
                return 1.0
            else:
                return 0.0
        elif cond == '=':
            if spec_value == v:
                return 1.0
            else:
                return 0.0
        else:
            print cond
    else:
        if cond == '=':
            if spec_value == v:
                return 1.0
            else:
                return 1.0 - abs(spec_value - v + 0.0)/att['range']
        elif cond == '!=':
            if spec_value != v:
                return 1.0
            else:
                return 0.0
        elif cond == '<':
            if spec_value < v:
                return 1.0 + abs(spec_value - v + 0.0)/att['range']
            else:
                return 1.0 - abs(spec_value - v + 0.0)/att['range']
        elif cond == '<=':
            if spec_value <= v:
                return 1.0 #+ abs(spec_value - v + 0.0)/att['range']
            else:
                return 1.0 - abs(spec_value - v + 0.0)/att['range']
        elif cond == '>':
            if spec_value > v:
                return 1.0 + abs(spec_value - v + 0.0)/att['range']
            else:
                return 1.0 - abs(spec_value - v + 0.0)/att['range']
        elif cond == '>=':
            if spec_value >= v:
                return 1.0 #+ abs(spec_value - v + 0.0)/att['range']
            else:
                return 1.0 - abs(spec_value - v + 0.0)/att['range']
        else:
            print 'Oops'

def values(prd, prefs, atts):
    scores = []

    for atk in att_keys:
        pref = prefs[atk]

        spv = prd[atk]
        # get value function
        v = score(atk, spv, pref, atts)

        scores.append(v)

    return np.array(scores)

def utility(prd, prefs, atts):
    u = 0.0
    for atk in att_keys:
        pref = prefs[atk]

        spv = prd[atk]
        # get value function
        v = score(atk, spv, pref, atts)

        u += pref['weight'] * v
    return u
