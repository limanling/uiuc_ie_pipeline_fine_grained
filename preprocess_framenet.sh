#!/usr/bin/env bash

# ================ input arguments =========================
data_root=$1
lang=$2
thread_id=$3
eval=$4
# ================ default arguments =======================
# ltf source folder path
ltf_source=${data_root}/ltf_minibatch/${thread_id}
# event output
event_result_dir=${data_root}/event
ltf_txt_path=${event_result_dir}/ltf_txt/${thread_id}
framenet_path=${event_result_dir}/framenet_res

# # ================ script =========================
# # preprocess for English
# docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_${eval} \
#     /opt/conda/envs/py36/bin/python \
#     /event/aida_event/framenet/generate_framenet.py \
#     ${lang} ${ltf_source} ${ltf_txt_path} ${framenet_path}
# docker run --rm -v ${data_root}:${data_root} -w `pwd` -w `pwd` -i limanling/aida-tools \
#     /bin/bash /semafor/bin/runSemafor_dir.sh  \
#     ${ltf_txt_path} ${framenet_path} 10
