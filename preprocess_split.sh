#!/usr/bin/env bash

# ================ input arguments =========================
data_root=$1
thread_num=$2
eval=$3
# ================ default arguments =========================
ltf_source=${data_root}/ltf
rsd_source=${data_root}/rsd
ltf_source_thread_dir=${data_root}/ltf_minibatch
rsd_source_thread_dir=${data_root}/rsd_minibatch

# ================ script =========================
# split files
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_${eval} \
    /opt/conda/envs/py36/bin/python \
    /preprocessing/postprocessing_separate_files.py \
    ${ltf_source} ${rsd_source} ${ltf_source_thread_dir} ${rsd_source_thread_dir} ${thread_num}
