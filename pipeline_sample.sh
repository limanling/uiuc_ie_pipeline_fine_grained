#!/usr/bin/env bash

######################################################
# Arguments
######################################################
# input root path
data_root=$1
parent_child_tab_path=$2
raw_id_column=$3
rename_id_column=$4

# data folder that specified with language
data_root_ltf=${data_root}/ltf
data_root_rsd=${data_root}/rsd
data_root_result=${data_root}/result
data_root_en=${data_root_result}/en

######################################################
# Knowledge Extraction for each language
######################################################
docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /preprocessing/preprocess_detect_languages.py ${data_root_rsd} ${data_root_ltf} ${data_root_result}

if [ -d "${data_root_en}/ltf" ]
then
    sh pipeline_sample_en.sh ${data_root_en}
else
    echo "No English documents in the corpus. Please double check. "
fi