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


def main():
    usage = "usage prog [options] arg"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--input", dest="input_file",
        help="the input file")
    parser.add_option("-p", "--prds", dest="prds_file",
        help="the product file")
    
    # parser.add_option('-f', "--fixation", dest="fixation",
    #     help="the fixation folder")
    # parser.add_option("-o", "--output", dest="output",
    #               help="write out to DIR")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose")
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose")

    (options, remainder) = parser.parse_args()


    pres = 0.0
    recalls = 0.0

    count = 0.0

    k = 9

    lines = open(options.input_file, 'r')
    for i, line in enumerate(lines):
        if i == 0:
            continue
        items = line.strip().split(',')
        # print items[:10]
        scores = [int(x) for x in items[:10]]
        
        atts = []
        # print items[10:]
        for j, item in enumerate(items[10:]):
            if item != '' and item != '?':
                atts.append(j)

        # print atts
        order_list = order(scores)
        hits = 0.0
        for x in order_list[:k]:
            if x in atts:
                hits += 1.0

        count += 1.0

        pres += hits/k
        recalls += hits/len(atts)

    print 'Top: %d' % int(count)
    print 'precision: %.3f' % (pres/count)
    print 'recall: %.3f' % (recalls/count)


if __name__=="__main__":
    main()
        