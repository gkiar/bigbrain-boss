#!/bin/bash

START=1
END=7404
BASEURL=ftp://bigbrain.loris.ca/BigBrainRelease.2015/2D_Final_Sections/Coronal/Png/Full_Resolution/
LOCAL=./bigbrain/
pm1298o.png

for i in $(seq ${START} ${END})
do
	echo Getting slice: pm`printf "%04d" ${i}`o.png 
	ftp ${BASEURL}pm`printf "%04d" ${i}`o.png ${LOCAL} 1> /dev/null
done
