#!/usr/bin/env python 

from sys import argv 
from os import getenv, system 
from glob import glob
if len(argv) == 4:
    infile = argv[1]
    outfile = argv[2] 
else:
    infile = 'input.root'
    outfile = argv[2] + '/'
    x = argv[1].split('/')
    outfile += '_'.join([x[-1].replace('.root',''), '%i_%s.npy'])
args = argv[:]
argv = []

import ROOT as root
import numpy as np 
from PandaCore.Tools.Misc import PInfo, PError, PDebug 
from PandaCore.Tools.root_interface import read_tree
from NH1 import NH1
from time import sleep 

branches = { }
bins = { }
#cats = ['singletons', 'inclusive', 'parton']
cats = ['singletons', 'charged', 'inclusive', 'sv']
pads = {'charged':50, 'inclusive':100, 'sv':10, 'singletons':1, 'parton':10}
for cat in cats:
    fcat = open(getenv('CMSSW_BASE')+'/src/conversion/txt/'+cat+'.txt')
    branches[cat] = []
    bins[cat] = {}
    for x in fcat.readlines():
        xx = x.strip().split(':')
        branches[cat].append('AK8Puppijet_'+xx[0])
        try:
            bins[cat][xx[0]] = [np.float64(xxx) for xxx in xx[1].split(',')]
        except IndexError:
            pass
    fcat.close()


def convert(tree, branchlist, cut=None, dim=2, astype=np.float16, maxlen=50):
    struct_arr = read_tree(tree, branchlist, cut)
    if False and dim > 1: 
        arr = np.stack([
                            pad_sequences(struct_arr[f], 
                                          dtype=np.float32, 
                                          maxlen=maxlen, 
                                          padding='post', 
                                          truncating='post', 
                                          value=0.).astype(astype) 
                            for f in branchlist
                        ], 
                        axis=1)
    else:
        arr = np.stack([
                            struct_arr[f].astype(astype) 
                            for f in branchlist
                        ], 
                        axis=1)
    if dim>1: 
        arr = arr.transpose((0, 2, 1))
    return arr

def run_prong(tree, nprong, out_path_tmpl):
    cut = 'AK8Puppijet_nProngs==%i && AK8Puppijet_pt>400 && AK8Puppijet_msd>40'%nprong 
    arrs = {}
    for cat in cats:
        dim = 1 if cat=='singletons' else 2
        arr = convert(tree, branches[cat], cut=cut, dim=dim, maxlen=pads[cat])
        if arr.shape[0] == 0:
            print 'Input did not create non-empty array in %s'%(out_path_tmpl%(nprong, cat))
            return
        if cat == 'singletons':
            arrs[cat] = arr 
        np.save(out_path_tmpl%(nprong, cat), arr)
        dummy = np.load(out_path_tmpl%(nprong, cat)) # just make sure this doesn't crash
        print 'Successfuly created',out_path_tmpl%(nprong, cat)
    arr = arrs['singletons'][:,branches['singletons'].index('AK8Puppijet_pt')]
    h = NH1(np.arange(400.,2000.,40))
    h.fill_array(arr)
    h.save(out_path_tmpl%(nprong, 'ptweight'))
        

def run_resonance(tree, resonance, out_path_tmpl):
    cut = 'AK8Puppijet_resonanceType==%i && AK8Puppijet_pt>400 && AK8Puppijet_msd>20'%resonance
    arrs = {}
    for cat in cats:
        dim = 1 if cat=='singletons' else 2
        arr = convert(tree, branches[cat], cut=cut, dim=dim, maxlen=pads[cat])
        if arr.shape[0] == 0:
            return
        if cat == 'singletons':
            arrs[cat] = arr 
        np.save(out_path_tmpl%(resonance, cat), arr)
        print arr.shape
        dummy = np.load(out_path_tmpl%(resonance, cat)) # just make sure this doesn't crash
        print 'Successfuly created',out_path_tmpl%(resonance,cat)
    arr = arrs['singletons'][:,branches['singletons'].index('AK8Puppijet_pt')]
    h = NH1(np.arange(400.,2000.,40))
    h.fill_array(arr)
    h.save(out_path_tmpl%(resonance, 'ptweight'))


def run_all(tree, out_path_tmpl):
    for cat in cats:
        dim = 1 if cat=='singletons' else 2
        arr = convert(tree, branches[cat], cut=None, dim=dim, maxlen=pads[cat])
        np.save(out_path_tmpl%cat, arr)


f_in = root.TFile(infile)
t_in = f_in.Get('Events')
system('mkdir -p tmp/')
tmp_outpath = 'tmp/' + outfile.split('/')[-1]
#if 'QCD' in outfile:
#    resonances = [0]
#elif 'BulkGravTohhTohbbhbb' in outfile:
#    resonances = [3]
#elif 'ZprimeToTTJet' in outfile:
#    resonances = [2, 4]
#else:
#    resonances = [1, 2]
#for resonance in resonances:
#    run_resonance(t_in, resonance, tmp_outpath)

if 'QCD' in outfile:
    n_prongs = [1]
elif 'ZprimeToA0hToA0chichihbb' in outfile or 'ZprimeToWW' in outfile:
    n_prongs = [1, 2]
elif 'ZprimeToTTJet' in outfile:
    n_prongs = [1, 2, 3]
for n_prong in n_prongs:
    run_prong(t_in, n_prong, tmp_outpath)
outdir = '/'.join(outfile.split('/')[:-1])
# sleep(np.random.randint(60)) # stagger the stageouts
# system('cp tmp/* %s'%outdir)
for ftmp in glob('tmp/*'):
    cmd = ('yes | gfal-copy file://$PWD/%s srm://t3serv006.mit.edu:8443/srm/v2/server?SFN=%s/%s'%
            (ftmp, outdir, ftmp.split('/')[-1])) # gfal-cp to avoid overloading server
    print cmd 
    system(cmd)
    # system('mv %s %s'%(ftmp, outdir))
    #system('yes | scp %s snarayan@t3desk006.mit.edu:%s'%(ftmp, outdir))
    #system('hdfs dfs -fs hdfs://t3serv002.mit.edu:9000 -put -f %s %s'%(ftmp, outdir.replace('/mnt/hadoop','')))
system('rm -r tmp')
# run_all(t_in, args[2])
