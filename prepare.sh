#!/bin/bash

BASEDIR=$SUBMIT_CONVERT_BASEDIR/$SUBMIT_CONVERT_VERSION/
OUTDIR=${SUBMIT_REPRO_BASEDIR}/${SUBMIT_CONVERT_VERSION}_repro/

echo "Checking sanity"
python sanity.py "${BASEDIR}/*singletons.npy" 

echo "Reweighting"
mkdir -p $BASEDIR/aggregate/
#python reweight.py "${BASEDIR}/ZprimeToWW*_2_ptweight.npy" ${BASEDIR}/aggregate/ZprimeToWW_2_ptweight.npy
#python reweight.py "${BASEDIR}/ZprimeToTTJet_*_4_ptweight.npy" ${BASEDIR}/aggregate/ZprimeToTTJet_4_ptweight.npy
#python reweight.py "${BASEDIR}/ZprimeToTTJet_*_2_ptweight.npy" ${BASEDIR}/aggregate/ZprimeToTTJet_2_ptweight.npy
#python reweight.py "${BASEDIR}/QCD_*_0_ptweight.npy" ${BASEDIR}/aggregate/QCD_0_ptweight.npy

#python reweight.py "${BASEDIR}/ZprimeToWW_*_2_ptweight.npy" ${BASEDIR}/aggregate/ZprimeToWW_2_ptweight.npy
#python reweight.py "${BASEDIR}/ZprimeToWW_*_1_ptweight.npy" ${BASEDIR}/aggregate/ZprimeToWW_1_ptweight.npy
#
python reweight.py "${BASEDIR}/ZprimeToTTJet_*_3_ptweight.npy" ${BASEDIR}/aggregate/ZprimeToTTJet_3_ptweight.npy
#python reweight.py "${BASEDIR}/ZprimeToTTJet_*_2_ptweight.npy" ${BASEDIR}/aggregate/ZprimeToTTJet_2_ptweight.npy
python reweight.py "${BASEDIR}/ZprimeToA0hToA0chichihbb_*_2_ptweight.npy" ${BASEDIR}/aggregate/ZprimeToA0hToA0chichihbb_2_ptweight.npy
#
#python reweight.py "${BASEDIR}/QCD_*_3_ptweight.npy" ${BASEDIR}/aggregate/QCD_3_ptweight.npy
#python reweight.py "${BASEDIR}/QCD_*_2_ptweight.npy" ${BASEDIR}/aggregate/QCD_2_ptweight.npy
python reweight.py "${BASEDIR}/QCD_*_1_ptweight.npy" ${BASEDIR}/aggregate/QCD_1_ptweight.npy

echo "Normalizing"
python normalize.py "${BASEDIR}/ZprimeToTTJet_*_3_XXXX.npy" ${BASEDIR}/aggregate/QCD_1
#python normalize.py "${BASEDIR}/QCD_*_0_XXXX.npy" ${BASEDIR}/aggregate/QCD_0
#python normalize.py "${BASEDIR}/QCD_*_1_XXXX.npy" ${BASEDIR}/aggregate/QCD_1

echo "Cataloging"

#ls ${BASEDIR}/ZprimeToWW*_2_singletons.npy > txt/catalog_npy/ZprimeToWW_2.txt
#ls ${BASEDIR}/ZprimeToTTJet_*_4_singletons.npy > txt/catalog_npy/ZprimeToTTJet_4.txt
#ls ${BASEDIR}/ZprimeToTTJet_*_2_singletons.npy > txt/catalog_npy/ZprimeToTTJet_2.txt
#ls ${BASEDIR}/QCD_*_0_singletons.npy > txt/catalog_npy/QCD_0.txt
#ls ${BASEDIR}/ZprimeToWW_*_2_singletons.npy > txt/catalog_npy/ZprimeToWW_2.txt
#ls ${BASEDIR}/ZprimeToWW_*_1_singletons.npy > txt/catalog_npy/ZprimeToWW_1.txt
ls ${BASEDIR}/ZprimeToTTJet_*_3_singletons.npy > txt/catalog_npy/ZprimeToTTJet_3.txt
#ls ${BASEDIR}/ZprimeToTTJet_*_2_singletons.npy > txt/catalog_npy/ZprimeToTTJet_2.txt
ls ${BASEDIR}/ZprimeToA0hToA0chichihbb_*_2_singletons.npy > txt/catalog_npy/ZprimeToA0hToA0chichihbb_2.txt
#ls ${BASEDIR}/QCD_*_3_singletons.npy > txt/catalog_npy/QCD_3.txt
#ls ${BASEDIR}/QCD_*_2_singletons.npy > txt/catalog_npy/QCD_2.txt
ls ${BASEDIR}/QCD_*_1_singletons.npy > txt/catalog_npy/QCD_1.txt


echo "Submitting"
#for cat in ZprimeToTTJet_4 ZprimeToTTJet_2 ZprimeToWW_2 QCD_0 ; 
#for cat in ZprimeToTTJet_3 ZprimeToTTJet_2 ZprimeToWW_2 ZprimeToWW_1 QCD_1 QCD_2 QCD_3 ; 
for cat in ZprimeToTTJet_3 ZprimeToA0hToA0chichihbb_2 QCD_1 ; 
do
  python partition.py txt/catalog_npy/${cat}.txt ${cat} $OUTDIR 
  submit --exec reprocess.py --arglist txt/cfg_${cat}/args.txt --cache $(readlink -f cache/${cat}/)
done
