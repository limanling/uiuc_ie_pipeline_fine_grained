#!/usr/bin/env bash

data_root=$1
lang=$2
parent_child_tab=$3
sorted=$4
# ltf source folder path
ltf_source=${data_root}/ltf
# rsd source folder path
rsd_source=${data_root}/rsd
# file list of ltf files (only file names)
ltf_file_list=${data_root}/ltf_lst
# file list of rsd files (absolute paths, this is a temporary file)
rsd_file_list=${data_root}/rsd_lst
# bio
edl_output_dir=${data_root}/edl
edl_bio=${edl_output_dir}/${lang}.bio
# corenlp
core_nlp_output_path=${data_root}/corenlp
timetable_tab=${data_root}/time_table.tab
# udp
udp_dir=${data_root}/udp
chunk_file=${edl_output_dir}/chunk.txt
# event output
event_result_dir=${data_root}/event
ltf_txt_path=${event_result_dir}/'ltf_txt'
framenet_path=${event_result_dir}/'framenet_res'
thread_num=3

# generate *.bio
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/ltf2bio.py ${ltf_source} ${edl_bio}
# generate file list
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/dir_readlink.py ${rsd_source} ${rsd_file_list}
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/dir_ls.py ${ltf_source} ${ltf_file_list}

# apply stanford corenlp
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/parent_child_util.py \
    ${parent_child_tab} ${sorted} ${timetable_tab}
docker run --rm -v `pwd`/data:/stanford-corenlp-aida_0/data -w /stanford-corenlp-aida_0 -i limanling/aida-tools \
    java -mx50g -cp '/stanford-corenlp-aida_0/*' edu.stanford.nlp.pipeline.StanfordCoreNLP \
    $* -annotators 'tokenize,cleanxml,ssplit,pos,lemma,ner,depparse,entitymentions,parse' \
    -outputFormat json \
    -filelist ${rsd_file_list} \
    -ner.docdate.useMappingFile ${timetable_tab} \
    -properties StanfordCoreNLP_${lang}.properties \
    -outputDirectory ${core_nlp_output_path}
#docker run --rm -v `pwd`/data:/CoreNLP/data -i graham3333/corenlp-complete \
#    java -mx50g -cp '*' edu.stanford.nlp.pipeline.StanfordCoreNLP \
#    $* -annotators 'tokenize,cleanxml,ssplit,pos,lemma,ner,depparse,entitymentions,parse' \
#    -outputFormat json \
#    -filelist ${rsd_file_list} \
#    -ner.docdate.useMappingFile ${timetable_tab} \
#    -properties StanfordCoreNLP_${lang}.properties \
#    -outputDirectory ${core_nlp_output_path}
#docker run --rm -v `pwd`:`pwd` -w `pwd` -i --network="host" limanling/uiuc_ie_m18 \
#    /opt/conda/envs/py36/bin/python \
#    ./system/aida_filler/nlp_utils.py \
#    --rsd_list ${rsd_file_list} \
#    --corenlp_dir ${core_nlp_output_path}
docker run --rm -v `pwd`/data:/scr/data -w /scr -i dylandilu/chuck_coreference \
    echo "finish stanford dependency parser for "${data_root}
# apply universal dependency parser
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    mkdir -p ${udp_dir}
docker run --rm -v `pwd`/data:/scr/data -w /scr -i dylandilu/chuck_coreference \
    python bio2udp.py \
    --corenlp_dir ${core_nlp_output_path} \
    --lang ${lang} \
    --path_bio ${edl_bio} \
    --udp_dir ${udp_dir}
docker run --rm -v `pwd`/data:/scr/data -w /scr -i dylandilu/chuck_coreference \
    echo "finish universal dependency parser for "${data_root}
# chunk extraction
docker run --rm -v `pwd`/data:/scr/data -w /scr -i dylandilu/chuck_coreference \
    python chunk_mine.py \
    --udp_dir ${udp_dir} \
    --text_dir ${rsd_source} \
    --path_out_chunk ${chunk_file}
docker run --rm -v `pwd`/data:/scr/data -w /scr -i dylandilu/chuck_coreference \
    echo "finish chunking for "${data_root}

