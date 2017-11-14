#!/usr/bin/env python

from sys import argv, exit
from re import sub, search
from os import system 
from math import floor 

catalog_path = argv[1]
pattern = argv[2]
outdir = argv[3]
fcatalog = open(catalog_path)

files = {}
for line in fcatalog.readlines():
    l = line.strip()
    pd = sub(r'_Output.*', '', l.split('/')[-1])
    if pd not in files:
        files[pd] = []
    files[pd].append(l)

#print {pd:len(f) for pd,f in files.iteritems()}
n_jobs = min(map(len, files.values()))

job_cfg = [[] for _ in xrange(n_jobs+1)]

for inputs in files.values():
    n = len(inputs)
    n_per = int(floor(float(n) / n_jobs))
    for i_job in xrange(n_jobs+1):
        first = min(n, n_per * i_job )
        last = n if (i_job == n_jobs) else min(n, n_per * (i_job + 1))
        job_cfg[i_job] += inputs[first:last]

cfgdir = 'txt/cfg_'+pattern 

system('rm -rf '+cfgdir)
system('mkdir -p '+cfgdir)

fargs = open('%s/args.txt'%cfgdir, 'w')

for idx,cfg in zip(xrange(len(job_cfg)), job_cfg):
    fargs.write('%s/%i.cfg %s %s\n'%(cfgdir, idx, pattern, outdir))
    with open(cfgdir+'/%i.cfg'%idx, 'w') as fcfg:
        for f in cfg:
            fcfg.write(f+'\n')
