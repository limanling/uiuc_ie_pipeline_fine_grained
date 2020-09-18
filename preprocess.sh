#!/usr/bin/env bash

# ================ input arguments =========================
data_root_lang=$1
lang=$2
parent_child_tab_path=$3
sorted=$4
thread_num=$5
eval=$6

## ================ script =========================
## split dataset into minibatches
sh preprocess_split.sh ${data_root_lang} ${thread_num} ${eval}
## run the scripts
for thread_id in $(seq 1 $thread_num);
do
    (
        # note that preprocess_parser.sh and preprocess_framenet.sh can also be run in parallel
        sh preprocess_parser.sh ${data_root_lang} ${lang} ${parent_child_tab_path} ${sorted} ${thread_id} ${eval}
        sh preprocess_framenet.sh ${data_root_lang} ${lang} ${thread_id} ${eval}
    )&
done
## merge the result
sh preprocess_merge.sh ${data_root_lang} ${lang} ${eval}