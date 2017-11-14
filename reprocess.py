#!/usr/bin/env python 

from sys import argv, exit 
import json 
import numpy as np 
from NH1 import NH1
from os import getenv, system
from time import sleep
from glob import glob

basedir = getenv('CMSSW_BASE') + '/src/conversion/'
cfgpath = basedir + argv[1]
pd = argv[2]
outdir = argv[3] 

add_cats = ['inclusive']
#add_cats = ['inclusive', 'parton']
NPER = 50 # only merge this many files together
pt_idx = 0 # location of pT in singletons array
fracs = {'train':0.70, 'test':0.15}

idx = int(argv[1].split('/')[-1].split('.')[0])

cfg = [l.strip() for l in open(cfgpath).readlines()]
ncfg = len(cfg)
if ncfg == 0:
    exit(0)

np.random.shuffle(cfg)
f_partitions = [cfg[min(i*NPER,ncfg):min((i+1)*NPER,ncfg)] for i in xrange(ncfg/NPER + 1)]

aggregate = '/'.join(cfg[0].split('/')[:-1]) + '/aggregate/'
pt_weight = NH1(); pt_weight.load(aggregate+'/%s_ptweight.npy'%pd)
scaled_pt_weight = NH1(); scaled_pt_weight.load(aggregate+'/%s_ptweight_scaled.npy'%pd)


for d in ['train','test','validate']:
    system('mkdir -p %s/'%(d))

for fidx, files in enumerate(f_partitions):
    if not files:
        continue
    bad_files = []
    print 'Loading singletons'
    xarr = np.concatenate([np.load(f) for f in files])
    print 'Loading weights'
    warr = pt_weight.eval_array(xarr[:,pt_idx])
    print 'Loading scaled weights'
    swarr = scaled_pt_weight.eval_array(xarr[:,pt_idx])
    N = warr.shape[0]
    indices = range(N); np.random.shuffle(indices)
    n_train = int(fracs['train'] * N)
    n_test = int(fracs['test'] * N)

    assert(xarr.shape[0] == N)
    assert(swarr.shape[0] == N)

    np.save('train/%s_%i_%i_singletons.npy'%(pd, idx, fidx), xarr[indices[:n_train]])
    np.save('test/%s_%i_%i_singletons.npy'%(pd, idx, fidx), xarr[indices[n_train:n_train+n_test]])
    np.save('validate/%s_%i_%i_singletons.npy'%(pd, idx, fidx), xarr[indices[n_train+n_test:]])

    np.save('train/%s_%i_%i_ptweight.npy'%(pd, idx, fidx), warr[indices[:n_train]])
    np.save('test/%s_%i_%i_ptweight.npy'%(pd, idx, fidx), warr[indices[n_train:n_train+n_test]])
    np.save('validate/%s_%i_%i_ptweight.npy'%(pd, idx, fidx), warr[indices[n_train+n_test:]])

    np.save('train/%s_%i_%i_ptweight_scaled.npy'%(pd, idx, fidx), swarr[indices[:n_train]])
    np.save('test/%s_%i_%i_ptweight_scaled.npy'%(pd, idx, fidx), swarr[indices[n_train:n_train+n_test]])
    np.save('validate/%s_%i_%i_ptweight_scaled.npy'%(pd, idx, fidx), swarr[indices[n_train+n_test:]])

    for cat in add_cats:
        print 'Processing category',cat
        payload = json.load(open(aggregate+'/QCD_1_%s.json'%(cat)))
        #payload = json.load(open(aggregate+'/QCD_0_%s.json'%(cat)))
        mu = []; sigma = []
        for p in payload:
            mu.append(p['mean'])
            if p['stdev'] > 0:
                sigma.append(p['stdev'])
            else:
                sigma.append(1)
        mu = np.array(mu); sigma = np.array(sigma)
        tmparrs = []
        for f in files: # do it this way for debugging output
            print f
            tmparr = np.load(f.replace('singletons',cat))
            tmparrs.append(tmparr)
        print 'Concatenating'
        xarr = np.concatenate(tmparrs)
        assert(xarr.shape[0] == N)
        print 'Concatenated'
        if mu.shape[0] != 0:
            xarr -= mu
            xarr /= sigma
        print 'Saving'
        np.save('train/%s_%i_%i_%s.npy'%(pd, idx, fidx, cat), xarr[indices[:n_train]])
        np.save('test/%s_%i_%i_%s.npy'%(pd, idx, fidx, cat), xarr[indices[n_train:n_train+n_test]])
        np.save('validate/%s_%i_%i_%s.npy'%(pd, idx, fidx, cat), xarr[indices[n_train+n_test:]])

    # do stageout at the end, so if anything fails along the way, it crashes instead of partial stageout
    for d in ['train','test','validate']:
        print 'Staging out successful output!'
        # sleep(np.random.randint(30)) # stagger the stageouts
        for ftmp in glob('%s/*npy'%d):
            # cmd = ('hdfs dfs -fs hdfs://t3serv002.mit.edu:9000 -put -f %s %s/%s' % 
            #        (ftmp, outdir.replace('/mnt/hadoop',''), d))
            cmd = ('gfal-copy file://$PWD/%s srm://t3serv006.mit.edu:8443/srm/v2/server?SFN=%s/%s' % 
                   (ftmp, outdir, ftmp))
            print cmd 
            system(cmd)
            cmd = 'rm %s'%ftmp 
            print cmd 
            system(cmd)
        # system('cp %s/*npy %s/%s/'%(d, outdir, d))
for d in ['train','test','validate']:
    system('rm -r %s'%d)
