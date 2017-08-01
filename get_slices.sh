#!/bin/bash

START=1401
END=1900
#END=7404
BASEURL=ftp://bigbrain.loris.ca/BigBrainRelease.2015/2D_Final_Sections/Coronal/Png/Full_Resolution/
LOCAL=./bigbrain/
CURR=${PWD}

mkdir -p ${LOCAL}
cd ${LOCAL}
for i in $(seq ${START} ${END})
do
	echo Getting slice: pm`printf "%04d" ${i}`o.png 
	ftp ${BASEURL}pm`printf "%04d" ${i}`o.png 1> /dev/null
done
cd ${CURR}
