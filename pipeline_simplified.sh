#!/usr/bin/env bash

######################################################
# Arguments
######################################################
data_root=$1
export CUDA_VISIBLE_DEVICES=$2


lang="en"
use_nominal_corefer=1
eval=m36

# ltf source folder path
ltf_source=${data_root}/ltf
# rsd source folder path
rsd_source=${data_root}/rsd

# edl output
edl_output_dir=${data_root}/edl
edl_cs_oneie=${data_root}/merge/cs/entity.cs
edl_tab_nam_filename=${lang}.nam.tab
edl_tab_nom_filename=${lang}.nom.tab
edl_tab_pro_filename=${lang}.pro.tab
edl_tab_nam=${data_root}/merge/mention/${edl_tab_nam_filename}
edl_tab_nom=${data_root}/merge/mention/${edl_tab_nom_filename}
edl_tab_pro=${data_root}/merge/mention/${edl_tab_pro_filename}
edl_tab_link=${edl_output_dir}/${lang}.linking.tab
edl_tab_link_fb=${edl_output_dir}/${lang}.linking.freebase.tab
edl_tab_final=${edl_output_dir}/merged_final.tab
edl_cs_coarse=${edl_output_dir}/merged.cs
edl_cs_fine=${edl_output_dir}/merged_fine.cs
edl_json_fine=${edl_output_dir}/${lang}.linking.freebase.fine.json
edl_tab_freebase=${edl_output_dir}/${lang}.linking.freebase.tab

# relation output
relation_cs_oneie=${data_root}/merge/cs/relation.cs # final cs output for relation
relation_result_dir=${data_root}/relation   # final cs output file path
relation_cs_coarse=${relation_result_dir}/${lang}.rel.cs # final cs output for relation

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

# final output
merged_cs_link=${data_root}/${lang}_full_link.cs
ttl_initial=${data_root}/initial


######################################################
# Setup
######################################################

# Download KB
if [ -d "${PWD}/system/aida_edl" ]
then
    echo "KB for linking is already in "${PWD}"/system/aida_edl"
else
    docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m36 rm -rf ${PWD}/system/aida_edl
    docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m36 mkdir -p ${PWD}/system/aida_edl
    docker run -v ${PWD}/system/aida_edl:/data panx27/data-processor wget http://159.89.180.81/demo/resources/edl_data.tar.gz -P /data
    docker run -v ${PWD}/system/aida_edl:/data panx27/data-processor tar zxvf /data/edl_data.tar.gz -C /data
fi
# Start Mongo DB
docker run -d --rm -v ${PWD}/system/aida_edl/edl_data/db:/data/db --name db mongo


######################################################
# Running scripts
######################################################

# echo "** Extracting coarse-grained entities, relations, and events **"
docker run --rm -i -v ${data_root}:${data_root} -w /oneie --gpus device=$2 limteng/oneie_aida_m36 \
    /opt/conda/bin/python \
    /oneie/predict.py -i ${ltf_source} -o ${data_root} -l ${lang}

## linking
echo "** Linking entities to KB **"
docker run -v ${PWD}/system/aida_edl/edl_data:/data \
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
docker run --rm -v ${data_root}:${data_root} --gpus device=$2 laituan245/spanbert_entity_coref \
    -edl_official ${edl_tab_link} -edl_freebase ${edl_tab_link_fb} -l ${ltf_source} -o ${edl_tab_final}
## tab2cs
docker run --rm -v ${data_root}:${data_root} -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /entity/aida_edl/tab2cs.py \
    ${edl_tab_final} ${edl_cs_coarse} 'EDL'
docker run --rm -v ${data_root}:${data_root} -v ${data_root}:${data_root} -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/rewrite_entity_id.py \
    ${edl_cs_oneie} ${relation_cs_oneie} ${event_coarse_oneie} ${edl_cs_coarse} \
    ${relation_cs_coarse} ${event_coarse_without_time}
# relation format change
docker run --rm -v ${data_root}:${data_root} -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    -u /relation_spa/FineRelationExtraction/EVALfine_grained_relations.py \
    --lang_id ${lang} \
    --ltf_dir ${ltf_source} \
    --rsd_dir ${rsd_source} \
    --cs_fnames ${edl_cs_coarse} ${relation_cs_coarse} ${event_coarse_without_time} \
    --fine_ent_type_tab ${edl_tab_freebase} \
    --fine_ent_type_json ${edl_json_fine} \
    --outdir ${relation_result_dir} \
    --fine_grained
# echo "** Event coreference **"
docker run --rm -v ${data_root}:${data_root} --gpus device=$2 laituan245/spanbert_coref \
    -i ${event_coarse_without_time} -c ${event_corefer} -t ${event_corefer_confidence} -l ${ltf_source}

# Final Merge
echo "** Merging all items **"
docker run --rm -v ${data_root}:${data_root} -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /postprocessing/pipeline_merge_simple.py \
    --cs_fnames ${edl_cs_coarse} ${relation_cs_fine} ${event_corefer} \
    --output_file ${merged_cs_link} --eval m36

# AIF converter
docker run --rm -v ${data_root}:${data_root} -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/aida_entity/bin/python \
    /postprocessing/aif_converter.py \
    --input_cs ${merged_cs_link} --ltf_dir ${ltf_source} \
    --output_ttl_dir ${ttl_initial} --lang ${lang} --eval m36
docker run --rm -v ${data_root}:${data_root} -i limanling/uiuc_ie_m36 \
    chmod -R 777 ${ttl_initial} ${ttl_initial}

echo "Final result in Cold Start Format is in "${merged_cs_link}
echo "Final result in RDF Format is in "${ttl_initial}