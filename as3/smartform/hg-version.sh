#!/bin/sh
#
# Copyright (c) 2009 rPath, Inc.
# All rights reserved
#
# Get the build version for build.xml

hgDir=$1
if [ -z $hgDir ]; then
  hgDir=../../
fi

if [[ -x /usr/bin/hg && -d $hgDir/.hg ]] ; then
    rev=`hg id -i`
elif [[ -x /usr/local/bin/hg && -d $hgDir/.hg ]]; then
    rev=`hg id -i`
elif [ -f $hgDir/.hg_archival.txt ]; then
    rev=`grep node $hgDir/.hg_archival.txt |cut -d' ' -f 2 |head -c 12`;
else
    rev= ;
fi ;
echo "$rev"


