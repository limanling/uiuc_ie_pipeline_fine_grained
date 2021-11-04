#!/usr/bin/env bash

######################################################
# Arguments
######################################################
data_root=$1
lang=$2
gpu_device=0
export CUDA_VISIBLE_DEVICES=${gpu_device}

source=""
# ltf source folder path
ltf_source=${data_root}/ltf
# rsd source folder path
rsd_source=${data_root}/rsd
# file list of ltf files (only file names)
ltf_file_list=${data_root}/ltf_lst
rsd_file_list=${data_root}/rsd_lst
# edl output
edl_output_dir=${data_root}/edl
edl_cs_oneie=${data_root}/merge/cs/entity.cs
edl_bio=${edl_output_dir}/${lang}.bio
edl_tab_nam_bio=${data_root}/merge/mention/${lang}.nam.bio
edl_tab_nam_filename=${lang}.nam.tab
edl_tab_nom_filename=${lang}.nom.tab
edl_tab_pro_filename=${lang}.pro.tab
edl_vec_file=${lang}.mention.hidden.txt
evt_vec_file=${lang}.trigger.hidden.txt
edl_tab_nam=${data_root}/merge/mention/${edl_tab_nam_filename}
edl_tab_nom=${data_root}/merge/mention/${edl_tab_nom_filename}
edl_tab_pro=${data_root}/merge/mention/${edl_tab_pro_filename}
edl_tab_link=${edl_output_dir}/${lang}.linking.tab
edl_tab_link_fb=${edl_output_dir}/${lang}.linking.freebase.tab
edl_tab_coref_ru=${edl_output_dir}/${lang}.coreference.tab
geonames_features=${edl_output_dir}/${lang}.linking.geo.json
edl_tab_final=${edl_output_dir}/${lang}.linking.freebase.tab  #${edl_output_dir}/merged_final.tab
edl_cs_coarse=${edl_output_dir}/merged.cs
entity_fine_model=${edl_output_dir}/merged_fine.tsv
edl_cs_fine=${edl_output_dir}/merged_fine.cs
edl_json_fine=${edl_output_dir}/${lang}.linking.freebase.fine.json
edl_tab_freebase=${edl_output_dir}/${lang}.linking.freebase.tab
freebase_private_data=${edl_output_dir}/freebase_private_data.json
lorelei_link_private_data=${edl_output_dir}/lorelei_private_data.json
entity_lorelei_multiple=${edl_output_dir}/${lang}.linking.tab.candidates.json
edl_cs_fine_all=${edl_output_dir}/merged_all_fine.cs
edl_cs_fine_protester=${edl_output_dir}/merged_all_fine_protester.cs
edl_cs_info=${edl_output_dir}/merged_all_fine_info.cs
edl_cs_info_conf=${edl_output_dir}/merged_all_fine_info_conf.cs
edl_tab_color=${edl_output_dir}/${lang}.linking.col.tab
edl_cs_color=${edl_output_dir}/${lang}.color.cs
conf_all=${edl_output_dir}/all_conf.txt
ground_truth_tab_dir=${edl_output_dir}/ldc_anno_matched
# filler output
core_nlp_output_path=${data_root}/corenlp
filler_coarse=${edl_output_dir}/filler_${lang}.cs
filler_coarse_color=${edl_output_dir}/filler_${lang}_all.cs
filler_fine=${edl_output_dir}/filler_fine.cs
# chunk_file=${data_root}/edl/chunk.txt
# relation output
relation_cs_oneie=${data_root}/merge/cs/relation.cs # final cs output for relation
relation_result_dir=${data_root}/relation   # final cs output file path
relation_cs_coarse=${relation_result_dir}/${lang}.rel.cs # final cs output for relation
relation_cs_fine=${relation_result_dir}/${lang}/${lang}.fine_rel.cs # final cs output for relation
relation_4tuple=${relation_result_dir}/${lang}/${lang}_rel_4tuple.cs
new_relation_coarse=${relation_result_dir}/new_relation_${lang}.cs
# event output
event_result_dir=${data_root}/event
event_coarse_oneie=${data_root}/merge/cs/event.cs
event_coarse_without_time=${event_result_dir}/event_rewrite.cs
event_coarse_with_time=${event_result_dir}/events_tme.cs
event_fine=${event_result_dir}/events_fine.cs
event_frame=${event_result_dir}/events_fine_framenet.cs
event_depen=${event_result_dir}/events_fine_depen.cs
event_fine_all=${event_result_dir}/events_fine_all.cs
event_fine_all_clean=${event_result_dir}/events_fine_all_clean.cs
event_corefer=${event_result_dir}/events_corefer.cs
event_corefer_confidence=${event_result_dir}/events_corefer_confidence.tab
event_corefer_time=${event_result_dir}/events_4tuple.cs
event_final=${event_result_dir}/events_info.cs
ltf_txt_path=${event_result_dir}/'ltf_txt'
framenet_path=${data_root}/event/'framenet_res'
# final output
merged_cs=${data_root}/${lang}${source}_full.cs
merged_cs_link=${data_root}/${lang}${source}_full_link.cs
ttl_initial=${data_root}/initial
ttl_initial_private=${data_root}/initial_private_data
ttl_final=${data_root}/final
######################################################
# Running scripts
######################################################
# oneie
docker run --rm -i -v ${data_root}:${data_root} -w /oneie --gpus device=${gpu_device} limteng/oneie_aida_m36 \
    /opt/conda/bin/python \
    /oneie/predict.py -i ${ltf_source} -o ${data_root} -l ${lang} #--output_hidden
docker run --rm -v ${data_root}:${data_root} -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/ltf2bio.py ${ltf_source} ${edl_bio}
docker run --rm -v ${data_root}:${data_root} -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/dir_ls.py ${ltf_source} ${ltf_file_list}
echo "finish stanford dependency parser for "${rsd_source}
# fine-grained typing by model
echo "fine-grained typing started"
docker run -d -i --rm --name uiuc_ie_m36 -w /entity_api -p 5500:5500 --name aida_entity limanling/uiuc_ie_m36 \
    /opt/conda/envs/aida_entity/bin/python \
    /entity_api/entity_api/app.py --eval m36
docker run --rm -v ${data_root}:${data_root} -i --network="host" --gpus device=${gpu_device} limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /entity/aida_edl/typing.py \
    ${lang} ${edl_tab_nam_bio} ${entity_fine_model}
echo "fine-grained typing finished"
echo "** Linking entities to KB **"
# docker run -d --rm -v /shared/nas/data/m1/manling2/aida_docker_test/ta2-pipeline-local/edl_blenders/blender08/edl_data/db:/data/db --name db mongo:4.2
docker run -v /shared/nas/data/m1/manling2/aida_docker_test/ta2-pipeline-local/edl_blenders/blender08/edl_data:/data \
    -v ${data_root}:/testdata_${lang} \
    --link db:mongo panx27/edl \
    python ./projs/docker_aida19/aida19.py \
    ${lang} \
    /testdata_${lang}/merge/mention/${edl_tab_nam_filename} \
    /testdata_${lang}/merge/mention/${edl_tab_nom_filename} \
    /testdata_${lang}/merge/mention/${edl_tab_pro_filename} \
    /testdata_${lang}/edl \
    m36
## nominal coreference
docker run --rm -v ${data_root}:${data_root} --gpus device=$3 laituan245/spanbert_entity_coref \
    -edl_official ${edl_tab_link} -edl_freebase ${edl_tab_link_fb} -l ${ltf_source} -o ${edl_tab_final}
## tab2cs
docker run --rm -v ${data_root}:${data_root} -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /entity/aida_edl_rufes/tab2cs.py \
    ${edl_tab_final} ${edl_cs_coarse} 'EDL'
docker run --rm -v ${data_root}:${data_root} -v ${data_root}:${data_root} -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/rewrite_entity_id.py \
    ${edl_cs_oneie} ${relation_cs_oneie} ${event_coarse_oneie} ${edl_cs_coarse} \
    ${relation_cs_coarse} ${event_coarse_without_time}
# echo "** Event coreference **"
docker run --rm -v ${data_root}:${data_root} --gpus device=${gpu_device} laituan245/spanbert_coref \
    -i ${event_coarse_without_time} -c ${event_corefer} -t ${event_corefer_confidence} -l ${ltf_source}


#######################################################
## Format converter
#######################################################
echo "Final result in Cold Start Format is in "${edl_cs_coarse}, ${relation_cs_coarse}, ${event_corefer}
#echo "Final result in RDF Format is in "${ttl_final}