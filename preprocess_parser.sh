#!/usr/bin/env bash

# ================ input arguments =========================
data_root=$1
lang=$2
parent_child_tab=$3
sorted=$4
thread_id=$5
# ================ default arguments =======================
# ltf source folder path
ltf_source_thread=${data_root}/ltf_minibatch/${thread_id}
# rsd source folder path
rsd_source_thread=${data_root}/rsd_minibatch/${thread_id}
# file list of ltf files (only file names)
ltf_file_list_thread=${data_root}/ltf_minibatch/${thread_id}_ltf_lst
# file list of rsd files (absolute paths, this is a temporary file)
rsd_file_list_thread=${data_root}/rsd_minibatch/${thread_id}_rsd_lst
# bio
edl_output_dir_thread=${data_root}/edl_minibatch
edl_bio_thread=${edl_output_dir_thread}/${lang}_${thread_id}.bio
# corenlp
core_nlp_output_path=${data_root}/corenlp
timetable_tab=${data_root}/time_table.tab


# ================ script =========================
# generate files for each thread
# generate *.bio
docker run --rm -v ${data_root}:/uiuc/${data_root} -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/ltf2bio.py /uiuc/${ltf_source_thread} /uiuc/${edl_bio_thread}
# generate file list
docker run --rm -v ${data_root}:/uiuc/${data_root} -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/dir_readlink.py /uiuc/${rsd_source_thread} /uiuc/${rsd_file_list_thread}

# apply stanford corenlp
docker run --rm -v ${data_root}:/uiuc/${data_root} \
    -v ${parent_child_tab}:/uiuc/${parent_child_tab} \
    -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/parent_child_util.py \
    /uiuc/${parent_child_tab} ${sorted} /uiuc/${timetable_tab}
docker run --rm -v ${data_root}:/uiuc/${data_root} -w /stanford-corenlp-aida_0 -i limanling/aida-tools \
    java -mx50g -cp '/stanford-corenlp-aida_0/*' edu.stanford.nlp.pipeline.StanfordCoreNLP \
    $* -annotators 'tokenize,cleanxml,ssplit,pos,lemma,ner,depparse,entitymentions,parse' \
    -outputFormat json \
    -filelist /uiuc/${rsd_file_list_thread} \
    -ner.docdate.useMappingFile /uiuc/${timetable_tab} \
    -properties StanfordCoreNLP_${lang}.properties \
    -outputDirectory /uiuc/${core_nlp_output_path}
docker run --rm -v ${data_root}:/uiuc/${data_root} -w /scr -i dylandilu/chuck_coreference \
    echo "finish stanford dependency parser for "${rsd_source_thread}


