#!/usr/bin/env bash

data_root=$1
lang=$2
# ltf source folder path
ltf_source=${data_root}/ltf
# event output
event_result_dir=${data_root}/event
ltf_txt_path=${event_result_dir}/'ltf_txt'
framenet_path=${event_result_dir}/'framenet_res'
thread_num=3

## preprocess for English
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /event/aida_event/framenet/generate_framenet.py \
    ${lang} ${ltf_source} ${ltf_txt_path} ${framenet_path}
docker run --rm -v `pwd`/data:/data -w `pwd` -i limanling/aida-tools \
    /bin/bash /semafor/bin/runSemafor_dir.sh  \
    /${ltf_txt_path} /${framenet_path} ${thread_num}