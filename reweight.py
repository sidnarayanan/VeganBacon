#!/usr/bin/env python

from sys import argv, exit, stdout 
from NH1 import NH1
from glob import glob 
import numpy as np 

outfile = argv[2]
infiles = glob(argv[1])
print '|-',argv[1]
print '|--->',outfile

pt_weight = NH1(np.arange(400.,2000.,40.))
n_files = len(infiles)
for ifile,fpath in enumerate(infiles):
    if ifile%100==0:
        print '%i/%i\r'%(ifile,n_files),
        stdout.flush()
    pt_weight.add_from_file(fpath)
print '                                              \r',
n_entries = pt_weight.integral()
print 'Loaded %i entries'%n_entries
pt_weight.invert()
pt_weight.save(outfile)
pt_weight.scale(np.float64(n_entries) / (pt_weight.bins.shape[0]*1000))
pt_weight.save(outfile.replace('ptweight','ptweight_scaled'))
