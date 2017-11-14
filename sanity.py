#!/usr/bin/env python

import numpy as np
from glob import glob
from sys import argv, exit, stdout
from re import sub 
from os import system 

#categories = ['singletons', 'ptweight', 'inclusive', 'parton']
categories = ['singletons', 'ptweight', 'inclusive']

corrupted = []
fs = glob(argv[1])
for i,f in enumerate(fs):
    print '%i/%i\r'%(i,len(fs)),
    stdout.flush()
    failed = False
    for c in categories:
        fc = f.replace('singletons', c)
        try:
            arr = np.load(fc)
        except:
            print fc
            failed = True 
            break 
    if failed:
        corrupted.extend([f.replace('singletons', c) for c in categories])


if corrupted:
    print 'Found corrupted files:'
    for f in corrupted:
        print f
    print 'Removing:'
    removable = set([sub('_[a-z]*\.npy$', '*.npy', f) for f in corrupted])
    for f in removable:
        to_remove = f
        print to_remove 
        fname = to_remove.split('/')[-1]
        if fname.replace('*.npy', '') == '':
            print 'ERROR', f 
            continue 
        print ('rm -f '+to_remove)
        system('rm -f '+to_remove)
    exit(1)
else:
    print 'No corrupted files found'
    exit(0)
