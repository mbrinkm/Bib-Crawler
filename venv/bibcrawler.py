#!/Library/Frameworks/Python.framework/Versions/3.8/bin/python3
######################

import requests as url
from pyquery import PyQuery as pq
import sys
import re
import io
import multiprocessing as mp
import os
import time

# get citation keys from .tex file
def findcitations(path):
    regex = r'(?<=\\cite{)(.*?)(?=})'       # RegEx matches '\cite{...}' interior

    with open(path, 'r') as tex:            # Find citation interiors, still in sequences and with line breaks
        read = tex.read()
        RawCites = re.findall(regex, read, re.S)

    cites = []
    for seq in RawCites:                    #clean up so only one citation per list item
        if seq.startswith('}'):
            continue
        seq2 = seq.split(',')
        for word in seq2:
            key = word.strip(' \n')
            cites.append(key)
    cites = list(dict.fromkeys(cites))   # cast to dict and back to list to remove duplicates
    return list(filter(None, cites))     #remove empty strings


# get inspire-hep ID from citation key
def getRecId(conn, keylist):
    for key in keylist:
        query = {'p': key, 'of': 'recjson', 'ot': 'recid'}
        URL = 'http://inspirehep.net/search?%s&of=recjson&ot=recid'
        with url.get(URL, query) as link:
            recid = link.json()[0]['recid']
            conn.send(recid)
    conn.send('END')


def addBibItem(conn, refpath):
    bf = ''
    while 1:
        recid = conn.recv()         # recieve recid from getRecId
        if recid == 'END':
            break
        page = pq('http://inspirehep.net/record/%s/export/hx' % recid)  # get inspire-hep identifier for key and read html file
        bibitem = page('.pagebodystripemiddle')('pre').html()  # find bib item on page
        bibitem = re.sub(r'(?m)^ *%%.*\n?', '', bibitem)
        bf += bibitem
    with open(refpath, 'w') as bib:
        bib.write(bf)

if __name__ == '__main__':
    start = time.time()
    # find current working directory
    cwd = os.getcwd()

    # read out relative path to .tex file
    if len(sys.argv) > 1:
        relpath = sys.argv[1]
    else:
        relpath = input('Relative path to .tex file:')

    texpath = cwd + '/' + relpath
    refpath = cwd + '/references.bib'

    if os.path.isfile(refpath):
        newpath = cwd + '/referencesOld.bib'
        n = 1
        while os.path.isfile(newpath):
            newpath = cwd + '/referencesOld' + str(n) + '.bib'
            n += 1
        os.rename(refpath, newpath)
        print('renamed old reference file: %s' % newpath)

    # get list of citation keys from .tex file
    cites = findcitations(texpath)

    # open pipe
    (parent_conn, child_conn) = mp.Pipe()

    # create processes
    p1 = mp.Process(target=getRecId, args=(parent_conn, cites))
    p2 = mp.Process(target=addBibItem, args=(child_conn, refpath))

    # run processes
    p1.start()
    p2.start()

    # wait until processes finish
    p1.join()
    p2.join()

    print('imported bib items to %s' % refpath)
    print('runtime: %s' % (time.time()-start))
