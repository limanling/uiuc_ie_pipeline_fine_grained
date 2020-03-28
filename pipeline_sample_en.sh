#!/usr/bin/env bash

######################################################
# Arguments
######################################################
lang="en"
# input root path
#data_root=data/testdata/${lang}_small
data_root=$1
parent_child_tab_path=$2
raw_id_column=$3
rename_id_column=$4
use_nominal_corefer=1

# ltf source folder path
ltf_source=${data_root}/ltf
# rsd source folder path
rsd_source=${data_root}/rsd
# file list of ltf files (only file names)
ltf_file_list=${data_root}/ltf_lst
ls ${ltf_source} > ${ltf_file_list}
# file list of rsd files (absolute paths, this is a temporary file)
rsd_file_list=${data_root}/rsd_lst
readlink -f ${rsd_source}/* > ${rsd_file_list}

# edl output
edl_output_dir=${data_root}/edl
edl_bio=${edl_output_dir}/${lang}.bio
edl_tab_nam=${edl_output_dir}/${lang}.nam.tagged.tab
edl_tab_nom=${edl_output_dir}/${lang}.nom.tagged.tab
edl_tab_pro=${edl_output_dir}/${lang}.pro.tagged.tab
edl_tab_link=${edl_output_dir}/${lang}.linking.tab
edl_tab_link_fb=${edl_output_dir}/${lang}.linking.freebase.tab
edl_tab_final=${edl_output_dir}/merged_final.tab
edl_cs_coarse=${edl_output_dir}/merged.cs
entity_fine_model=${edl_output_dir}/merged_fine.tsv
edl_cs_fine=${edl_output_dir}/merged_fine.cs
edl_json_fine=${edl_output_dir}/${lang}.linking.freebase.fine.json
edl_tab_freebase=${edl_output_dir}/${lang}.linking.freebase.tab
edl_cs_fine_all=${edl_output_dir}/merged_all_fine.cs
edl_cs_color=${edl_output_dir}/${lang}.linking.col.tab

# filler output
core_nlp_output_path=${data_root}/corenlp
filler_coarse=${edl_output_dir}/filler_en.cs
filler_fine=${edl_output_dir}/filler_fine.cs

# relation output
relation_result_dir=${data_root}/relation   # final cs output file path
relation_cs_coarse=${relation_result_dir}/en.rel.cs # final cs output for relation
relation_cs_fine=${relation_result_dir}/en.rel.cs # final cs output for relation
new_relation_coarse=${relation_result_dir}/new_relation_en.cs

# event output
event_result_dir=${data_root}/event
event_coarse_with_time=${event_result_dir}/events_tme.cs
event_fine=${event_result_dir}/events_fine.cs
event_corefer=${event_result_dir}/events_corefer.cs

# final output
final_output_file=${data_root}/${lang}_full.cs

######################################################
# Running scripts
######################################################

# EDL
echo "** Extracting entities **"
docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t --network="host" limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    ./system/aida_edl/edl.py \
    ${ltf_source} ${rsd_source} ${lang} ${edl_output_dir} \
    ${edl_bio} ${edl_tab_nam} ${edl_tab_nom} ${edl_tab_pro} \
    ${entity_fine_model}
# linking
echo "** Linking entities to KB **"
link_dir=system/aida_edl/edl_data/test
docker run -v `pwd`:`pwd` -w `pwd` -i -t limanling/uiuc_ie_m18 \
    mkdir -p ${link_dir}/input
docker run -v `pwd`:`pwd` -w `pwd` -i -t limanling/uiuc_ie_m18 \
    cp -r ${edl_output_dir}/* ${link_dir}/input/
docker run -v `pwd`:`pwd` -w `pwd` -i -t limanling/uiuc_ie_m18 \
    ls ${link_dir}/input
docker run -v ${PWD}/system/aida_edl/edl_data:/data --link db:mongo panx27/edl \
    python ./projs/docker_aida19/aida19.py \
    ${lang} /data/test/input /data/test/output
docker run -v `pwd`:`pwd` -w `pwd` -i -t limanling/uiuc_ie_m18 \
    cp ${link_dir}/output/* ${edl_output_dir}/
docker run -v `pwd`:`pwd` -w `pwd` -i -t limanling/uiuc_ie_m18 \
    rm -rf ${link_dir}
# nominal coreference
echo "** Starting nominal coreference **"
docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t --network="host" limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    ./system/aida_edl/nominal_corefer_en.py \
    --dev ${edl_bio} \
    --dev_e ${edl_tab_link} \
    --dev_f ${edl_tab_link_fb} \
    --out_e ${edl_tab_final} \
    --use_nominal_corefer ${use_nominal_corefer}
# tab2cs
docker run --rm -v `pwd`:`pwd` -w `pwd`  -i -t limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    ./system/aida_edl/tab2cs.py \
    ${edl_tab_final} ${edl_cs_coarse} 'EDL'

# Relation Extraction (coarse)
echo "** Extraction relations **"
docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t limanling/uiuc_ie_m18 \
    /opt/conda/envs/aida_relation_coarse/bin/python \
    -u /relation/CoarseRelationExtraction/exec_relation_extraction.py \
    -i ${lang} \
    -l ${ltf_file_list} \
    -f ${ltf_source} \
    -e ${edl_cs_coarse} \
    -t ${edl_tab_final} \
    -o ${relation_cs_coarse}


# Filler Extraction & new relation
echo "** Extraction fillers **"
docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t --network="host" limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    ./system/aida_filler/nlp_utils.py \
    --rsd_list ${rsd_file_list} --corenlp_dir ${core_nlp_output_path}
docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t --network="host" limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    ./system/aida_filler/filler_generate.py \
    --corenlp_dir ${core_nlp_output_path} \
    --edl_path ${edl_cs_coarse} \
    --text_dir ${rsd_source} \
    --filler_path ${filler_coarse}  \
    --relation_path ${new_relation_coarse} \
    --units_path ./system/aida_filler/units_clean.txt

# Fine-grained Entity
echo "** Fine-grained entity typing **"
docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t --network="host" limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    ./system/aida_edl/fine_grained_entity.py \
    ${lang} ${edl_json_fine} ${edl_tab_freebase} ${entity_fine_model} \
    ${edl_cs_coarse} ${edl_cs_fine} ${filler_fine} \
    --filler_coarse ${filler_coarse}
docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    ./system/aida_utilities/pipeline_merge_m18.py \
    -e ${edl_cs_fine} -f ${filler_fine} -o ${edl_cs_fine_all}

# Event (Coarse)
echo "** Extracting events **"
docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t --network="host" limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    ./system/aida_event/gail_event_test.py \
    -l ${ltf_file_list} \
    -f ${ltf_source} \
    -e ${edl_cs_coarse} \
    -t ${edl_tab_final} \
    -i ${filler_coarse} \
    -o ${event_coarse_with_time}

# Relation Extraction (fine)
docker run -v `pwd`:`pwd` -w `pwd` -i -t limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    -u /relation/FineRelationExtraction/EVALfine_grained_relations.py \
    --lang_id ${lang} \
    --ltf_dir ${ltf_source} \
    --rsd_dir ${rsd_source} \
    --cs_fnames ${edl_cs_coarse} ${filler_coarse} ${relation_cs_coarse} ${new_relation_coarse} \
    --fine_ent_type_tab ${edl_tab_freebase} \
    --fine_ent_type_json ${edl_json_fine} \
    --outdir ${relation_result_dir} \
    --fine_grained
##   --reuse_cache \
##   --use_gpu \


# Event (Fine-grained)
echo "** Event fine-grained typing **"
docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t --network="host" limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    ./system/aida_event/fine_grained/fine_grained_events.py \
    ${lang} ${ltf_source} ${edl_json_fine} ${edl_tab_freebase} \
    ${edl_cs_coarse} ${event_coarse_with_time} ${event_fine} \
    --filler_coarse ${filler_coarse} \
    --entity_finegrain_aida ${edl_cs_fine_all}


# Event coreference
docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t --network="host" limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    ./system/aida_event_coreference/gail_event_coreference_test_en.py \
    -i ${event_fine} -o ${event_corefer} -r ${rsd_source}

# Final Merge
echo "Merging all items"
docker run -it --rm -v `pwd`:`pwd` -w `pwd` limanling/uiuc_ie_m18 \
    python ./system/aida_utilities/pipeline_merge_m18.py \
    -e ${edl_cs_fine} -f ${filler_fine} \
    -r ${relation_cs_fine} \
    -v ${event_corefer} \
    -o ${final_output_file}

echo "Final result in Cold Start Format is in "${final_output_file}

