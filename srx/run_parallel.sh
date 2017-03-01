#!/bin/bash

x='XXXX'
idir=$PWD
run_script='start_calc_srx_src_img_01.py'
for i in $(seq 10000 1000 17000); do
    echo "Radius: $i m"
    calc_dir="r=$i/"
    if [ ! -d "$calc_dir" ]; then
        cp -r $x $calc_dir
        cd $calc_dir
        sed 's/--op_HFM_r=XXXX/--op_HFM_r='"$i"'/g' -i $run_script
        nohup python $run_script > run.log 2>&1 &
        cd $idir
    fi
done