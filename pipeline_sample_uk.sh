#!/usr/bin/env bash

######################################################
# Arguments
######################################################
data_root=$1
lang=$2
source=$3
use_nominal_corefer=1

# ltf source folder path
ltf_source=${data_root}/ltf
# rsd source folder path
rsd_source=${data_root}/rsd
# file list of ltf files (only file names)
ltf_file_list=${data_root}/ltf_lst
#ls ${ltf_source} > ${ltf_file_list}
# file list of rsd files (absolute paths, this is a temporary file)
rsd_file_list=${data_root}/rsd_lst
#readlink -f ${rsd_source}/* > ${rsd_file_list}

# edl output
edl_output_dir=${data_root}/edl
edl_bio=${edl_output_dir}/${lang}.bio
edl_tab_nam_filename=${lang}.nam.tagged.tab
edl_tab_nom_filename=${lang}.nom.tagged.tab
edl_tab_pro_filename=${lang}.pro.tagged.tab
edl_tab_nam=${edl_output_dir}/${edl_tab_nam_filename}
edl_tab_nom=${edl_output_dir}/${edl_tab_nom_filename}
edl_tab_pro=${edl_output_dir}/${edl_tab_pro_filename}
edl_tab_link=${edl_output_dir}/${lang}.linking.tab
edl_tab_link_fb=${edl_output_dir}/${lang}.linking.freebase.tab
edl_tab_coref_ru=${edl_output_dir}/${lang}.coreference.tab
geonames_features=${edl_output_dir}/${lang}.linking.geo.json
edl_tab_final=${edl_output_dir}/merged_final.tab
edl_cs_coarse=${edl_output_dir}/merged.cs
entity_fine_model=${edl_output_dir}/merged_fine.tsv
edl_cs_fine=${edl_output_dir}/merged_fine.cs
edl_json_fine=${edl_output_dir}/${lang}.linking.freebase.fine.json
edl_tab_freebase=${edl_output_dir}/${lang}.linking.freebase.tab
freebase_private_data=${edl_output_dir}/freebase_private_data.json
lorelei_link_private_data=${edl_output_dir}/lorelei_private_data.json
entity_lorelei_multiple=${edl_output_dir}/${lang}.linking.tab.candidates.json
edl_cs_fine_all=${edl_output_dir}/merged_all_fine.cs
edl_cs_info=${edl_output_dir}/merged_all_fine_info.cs
edl_cs_info_conf=${edl_output_dir}/merged_all_fine_info_conf.cs
edl_cs_color=${edl_output_dir}/${lang}.linking.col.tab
conf_all=${edl_output_dir}/all_conf.txt

# filler output
core_nlp_output_path=${data_root}/corenlp
filler_coarse=${edl_output_dir}/filler_${lang}.cs
filler_fine=${edl_output_dir}/filler_fine.cs
udp_dir=${data_root}/udp
chunk_file=${edl_output_dir}/chunk.txt

# relation output
relation_result_dir=${data_root}/relation   # final cs output file path
relation_cs_coarse=${relation_result_dir}/${lang}.rel.cs # final cs output for relation
relation_cs_fine=${relation_result_dir}/${lang}.rel.cs # final cs output for relation
new_relation_coarse=${relation_result_dir}/new_relation_${lang}.cs

# event output
event_result_dir=${data_root}/event
event_coarse_without_time=${event_result_dir}/events.cs
event_coarse_with_time=${event_result_dir}/events_tme.cs
event_fine=${event_result_dir}/events_fine.cs
event_frame=${event_result_dir}/events_fine_framenet.cs
event_depen=${event_result_dir}/events_fine_depen.cs
event_fine_all=${event_result_dir}/events_fine_all.cs
event_corefer=${event_result_dir}/events_corefer.cs
event_final=${event_result_dir}/events_info.cs
ltf_txt_path=${event_result_dir}/'ltf_txt'
framenet_path=${event_result_dir}/'framenet_res'

# final output
merged_cs=${data_root}/${lang}${source}_full.cs
merged_cs_link=${data_root}/${lang}${source}_full_link.cs


######################################################
# Running scripts
######################################################

# EDL
## entity extraction
echo "** Extracting entities **"
docker run --rm -v `pwd`:`pwd` -w `pwd` -i --network="host" limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    ./system/aida_edl/edl.py \
    ${ltf_source} ${rsd_source} ${lang} ${edl_output_dir} \
    ${edl_bio} ${edl_tab_nam} ${edl_tab_nom} ${edl_tab_pro} \
    ${entity_fine_model}
## linking
echo "** Linking entities to KB **"
link_dir=system/aida_edl/edl_data/test
docker run -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    mkdir -p ${link_dir}/input
docker run -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    cp -r ${edl_output_dir}/* ${link_dir}/input/
docker run -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    ls ${link_dir}/input
docker run -v ${PWD}/system/aida_edl/edl_data:/data --link db:mongo panx27/edl \
    python ./projs/docker_aida19/aida19.py \
    ${lang} /data/test/input/ /data/test/output
docker run -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    cp ${link_dir}/output/* ${edl_output_dir}/
docker run -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    rm -rf ${link_dir}
## nominal coreference for ru and uk
docker run --rm -v `pwd`/data:/scr/data -w /scr -i dylandilu/chuck_coreference \
    python appos_extract.py \
    --udp_dir ${udp_dir} \
    --edl_tab_path ${edl_tab_link} \
    --path_out_coref ${edl_tab_final}
## tab2cs
docker run --rm -v `pwd`:`pwd` -w `pwd`  -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    ./system/aida_edl/tab2cs.py \
    ${edl_tab_final} ${edl_cs_coarse} 'EDL'

# Relation Extraction (coarse-grained)
echo "** Extraction relations **"
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/aida_relation_coarse/bin/python \
    -u /relation/CoarseRelationExtraction/exec_relation_extraction.py \
    -i ${lang} \
    -l ${ltf_file_list} \
    -f ${ltf_source} \
    -e ${edl_cs_coarse} \
    -t ${edl_tab_final} \
    -o ${relation_cs_coarse}