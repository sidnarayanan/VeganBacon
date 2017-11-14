#!/bin/bash

export SUBMIT_CONVERT_BASEDIR="/data/t3serv014/snarayan/baconarrays/" 
#export SUBMIT_REPRO_BASEDIR="/mnt/hadoop/scratch/snarayan/baconarrays/" 
export SUBMIT_REPRO_BASEDIR="${SUBMIT_CONVERT_BASEDIR}" 
export SUBMIT_CONVERT_VERSION="v13"
mkdir -p ${SUBMIT_CONVERT_BASEDIR}/${SUBMIT_CONVERT_VERSION}/aggregate/

chmod 777 ${SUBMIT_CONVERT_BASEDIR}/${SUBMIT_CONVERT_VERSION}
mkdir -p ${SUBMIT_REPRO_BASEDIR}/${SUBMIT_CONVERT_VERSION}_repro/
chmod 777 ${SUBMIT_REPRO_BASEDIR}/${SUBMIT_CONVERT_VERSION}_repro/
for sub in train test validate; do
    mkdir -p ${SUBMIT_REPRO_BASEDIR}/${SUBMIT_CONVERT_VERSION}_repro/$sub/
    chmod 777 ${SUBMIT_REPRO_BASEDIR}/${SUBMIT_CONVERT_VERSION}_repro/$sub/
done


export PATH=${PATH}:${CMSSW_BASE}/src/PandaCore/bin/
