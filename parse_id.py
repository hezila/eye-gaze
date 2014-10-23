#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys, os

from optparse import OptionParser

import xml.etree.ElementTree as ET


def _prd_container(container_path):
    prd_container = {}
    tree = ET.parse(container_path)
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
                prd['price'] = item.text
            elif tag == 'brand':
                prd['name'] = item.text
        prd_key = "%s::%s" % (prd['name'], prd['price'])
        prd_id = prd['id']

        prd_container[prd_key] = prd_id
    print 'prd num: %d' % len(prd_container)

    return prd_container

def _user_container(user_container_path):
    user_container = {}
    with open(user_container_path, 'r') as r:
        for line in r:
            uname, uid = line.strip().split(',')
            user_container[uname] = uid
    return user_container

def _fixation_container(fixation_container_path):
    fixation_container = {}
    for dirname, dirnames, filenames in os.walk(fixation_container_path):
        for filename in filenames:
            file_path = os.path.join(dirname, filename)
            uid = filename[:-4]
            fixation_container[uid] = {}
            with open(file_path, 'r') as input:
                for line in input:
                    items = line.strip().split('\t')
                    fid = items[0]
                    duration = items[-3]
                    fixation_container[uid][fid] = duration
    return fixation_container


def get_prd_id(container, prd_key):
    return container[prd_key]

def get_user_id(container, user_name):
    return container[user_name]

def get_fixation_duration(container, uid, fixid):
    return container[uid][fixid]


def process_session(session):
    prd_freqs ={}
    prd_ds = {}

    for r in session:
        pid = r[2] # pid
        d = r[17] # duration
        if pid not in prd_freqs:
            prd_freqs[pid] = 1
            prd_ds[pid] = d
        else:
            prd_freqs[pid] += 1
            prd_ds[pid] += d

        critique_pid = r[31] # critiqued product

        if len(critique_pid) > 0: # the last line
            l = ['%s:%d' % (k, prd_freqs[k]) for k in prd_freqs]
            print '[%s] -> %s' (', '.join(l), critique_pid)


        best_select_pid = r[29] # best or selected product

        final_pid = r[-5]
        target_pid = r[-4]

def main():
    usage = "usage prog [options] arg"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--input", dest="input",
        help="the input file")
    parser.add_option("-p", "--prd", dest="prd",
        help="the product file")
    parser.add_option("-u", "--user", dest="user",
        help="the user file")
    parser.add_option('-f', "--fixation", dest="fixation",
        help="the fixation folder")
    parser.add_option("-o", "--output", dest="output",
                  help="write out to DIR")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose")
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose")

    (options, remainder) = parser.parse_args()

    prd_container = _prd_container(options.prd)
    user_container = _user_container(options.user)
    fixation_container = _fixation_container(options.fixation)

    input = open(options.input, 'r')
    output = open(options.output, 'w')
    index = 0
    for line in input:
        if index == 0:
            index += 1
            output.write(line)
            continue


        items = line.strip().split(',') # comma csv
        if sum([len(x) for x in items]) == 0: # empty line (containing commas)
            continue
        # pid (2)
        pk = items[1]

        pid = get_prd_id(prd_container, pk)
        items[2] = pid

        final_pk = items[-5].strip()
        if len(final_pk) > 0:
            # final_pid = get_prd_id(prd_container, final_pk)
            # items[-5] = final_pid
            final_pid = final_pk.split('::')[-1]
            items[-5] = final_pid

        target_pk = items[-4].strip()
        if len(target_pk) > 0:
            # target_pid = get_prd_id(prd_container, target_pk)
            # items[-4] = target_pid
            target_pid = target_pk.split('::')[-1]
            items[-4] = target_pid

        # user name (-3)
        uname = items[-3]
        if len(uname) > 0:
            uid = get_user_id(user_container, uname)
            items[-3] = uid
            fid = items[16]
            duration = get_fixation_duration(fixation_container, uid, fid)
            items[17] = duration
        output.write('%s\n' % ','.join(items))
    input.close()
    output.close()


if __name__ == "__main__":
    main()
