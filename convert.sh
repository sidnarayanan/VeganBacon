#!/bin/bash

OUTDIR=${SUBMIT_CONVERT_BASEDIR}/${SUBMIT_CONVERT_VERSION}/

# echo "xrdcp root://eoscms.cern.ch/${1} input.root "
# xrdcp root://eoscms.cern.ch/${1} input.root 
# echo "cp ${1} input.root "
# cp ${1} input.root 
echo "hdfs dfs -fs hdfs://t3serv002.mit.edu:9000 -get $(echo ${1} | sed "s?/mnt/hadoop??") input.root"
hdfs dfs -fs hdfs://t3serv002.mit.edu:9000 -get $(echo ${1} | sed "s?/mnt/hadoop??") input.root
python $CMSSW_BASE/src/conversion/convert.py ${1} $OUTDIR
ret=$?
#du -hs input.root
rm input.root
exit $ret
