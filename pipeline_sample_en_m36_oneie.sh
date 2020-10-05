#!/usr/bin/env bash

######################################################
# Arguments
######################################################
data_root=$1
parent_child_tab_path=$2
sorted=$3
lang=$4
source=$5
use_nominal_corefer=1

# ltf source folder path
ltf_source=${data_root}/ltf
# rsd source folder path
rsd_source=${data_root}/rsd
# file list of ltf files (only file names)
ltf_file_list=${data_root}/ltf_lst

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
udp_dir=${data_root}/udp
chunk_file=${data_root}/edl/chunk.txt

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

EDL
entity extraction
echo "** Extracting coarse-grained entities, relations, and events **"
docker run --rm -i -v ${data_root}:${data_root} -w /oneie --gpus '"device=1"' limteng/oneie_aida_m36 \
    /opt/conda/bin/python \
    /oneie/predict.py -i ${ltf_source} -o ${data_root} -l ${lang} --output_hidden
## fine-grained typing by model
echo "fine-grained typing started"
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i --network="host" limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /entity/aida_edl/typing.py \
    ${lang} ${edl_tab_nam_bio} ${entity_fine_model}
echo "fine-grained typing finished"

# linking
echo "** Linking entities to KB **"
docker run -v ${PWD}/system/aida_edl/edl_data:/data \
    -v ${data_root}:/testdata_${lang}${source} \
    --link db:mongo panx27/edl \
    python ./projs/docker_aida19/aida19.py \
    ${lang} \
    /testdata_${lang}${source}/merge/mention/${edl_tab_nam_filename} \
    /testdata_${lang}${source}/merge/mention/${edl_tab_nom_filename} \
    /testdata_${lang}${source}/merge/mention/${edl_tab_pro_filename} \
    /testdata_${lang}${source}/edl \
    m36
## nominal coreference
docker run --rm -v ${data_root}:${data_root} --gpus '"device=1"' laituan245/spanbert_entity_coref \
    -edl_official ${edl_tab_link} -edl_freebase ${edl_tab_link_fb} -l ${ltf_source} -o ${edl_tab_final}
## tab2cs
docker run --rm -v ${data_root}:${data_root} -w `pwd`  -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /entity/aida_edl/tab2cs.py \
    ${edl_tab_final} ${edl_cs_coarse} 'EDL'
docker run --rm -v ${data_root}:${data_root} -v ${data_root}:${data_root} -w `pwd`  -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/rewrite_entity_id.py \
    ${edl_cs_oneie} ${relation_cs_oneie} ${event_coarse_oneie} ${edl_cs_coarse} \
    ${relation_cs_coarse} ${event_coarse_without_time}

# # Filler Extraction & new relation
docker run --rm -v ${data_root}:${data_root} -w /scr -i dylandilu/filler \
    python extract_filler_relation.py \
    --corenlp_dir ${core_nlp_output_path} \
    --ltf_dir ${ltf_source} \
    --edl_path ${edl_cs_coarse} \
    --text_dir ${rsd_source} \
    --path_relation ${new_relation_coarse} \
    --path_filler ${filler_coarse} \
    --lang ${lang}

## Fine-grained Entity
echo "** Fine-grained entity typing **"
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /entity/aida_edl/fine_grained_entity.py \
    ${lang} ${edl_json_fine} ${edl_tab_freebase} ${entity_fine_model} \
    ${geonames_features} ${edl_cs_coarse} ${edl_cs_fine} ${filler_fine} \
    --filler_coarse ${filler_coarse} \
    --ground_truth_tab_dir ${ground_truth_tab_dir} \
    --ltf_dir ${ltf_source} --rsd_dir ${rsd_source} \
    --eval m36
docker run -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /relation/FineRelationExtraction/utils/color_fillers.py \
    --en_color_fill_tab_fname ${edl_tab_color} \
    --en_fill_cs_fname ${filler_coarse} \
    --en_combo_outfname ${filler_coarse_color} \
    --en_color_outfname ${edl_cs_color}

# Relation Extraction (fine)
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i --gpus '"device=1"' limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    -u /relation/FineRelationExtraction/EVALfine_grained_relations.py \
    --lang_id ${lang} \
    --ltf_dir ${ltf_source} \
    --rsd_dir ${rsd_source} \
    --cs_fnames ${edl_cs_coarse} ${filler_coarse_color} ${relation_cs_coarse} ${new_relation_coarse} ${event_coarse_without_time} \
    --fine_ent_type_tab ${edl_tab_freebase} \
    --fine_ent_type_json ${edl_json_fine} \
    --outdir ${relation_result_dir} \
    --fine_grained \
    --use_gpu
##   --reuse_cache \
docker run -i --rm -v ${data_root}:${data_root} \
    -v ${parent_child_tab_path}:${parent_child_tab_path} \
    -w /EventTimeArg --gpus '"device=1"' wenhycs/uiuc_event_time \
    python aida_event_time_pipeline.py \
    --relation_cold_start_filename ${relation_cs_fine} --relation \
    --parent_children_filename ${parent_child_tab_path} \
    --output_filename ${relation_4tuple}

## Postprocessing, adding informative justification
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/pipeline_merge_m18.py \
    --cs_fnames ${edl_cs_fine} ${filler_fine} \
    --output_file ${edl_cs_fine_all}
echo "add protester"
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /entity/aida_edl/add_protester.py \
    ${event_coarse_without_time} ${edl_cs_fine_all} ${edl_cs_fine_protester}
echo "** Informative Justification **"
docker run --rm -v ${data_root}:${data_root} -i panx27/aida20_mention \
    python ./extend.py ${lang} ${ltf_source} ${edl_cs_fine_protester} ${edl_cs_info}_tmp
docker run --rm -v ${data_root}:${data_root} panx27/aida20_mention \
    python ./revise.py ${edl_cs_info}_tmp ${edl_cs_info}
## update mention confidence
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/rewrite_mention_confidence.py \
    ${lang}${source} ${edl_tab_nam} ${edl_tab_nom} ${edl_tab_pro} \
    ${edl_tab_link} ${entity_lorelei_multiple} ${ltf_source} \
    ${edl_cs_info} ${edl_cs_info_conf} ${conf_all}
# Event (Fine-grained)
echo "** Event fine-grained typing **"
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /event/aida_event/fine_grained/fine_grained_events.py \
    ${lang} ${ltf_source} ${edl_json_fine} ${edl_tab_freebase} \
    ${edl_cs_coarse} ${event_coarse_without_time} ${event_fine} \
    --filler_coarse ${filler_coarse} \
    --entity_finegrain_aida ${edl_cs_fine_all}
## Event Rule-based
echo "** Event rule-based **"
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /event/aida_event/framenet/new_event_framenet.py \
    ${framenet_path} ${ltf_source} ${rsd_source} \
    ${edl_cs_coarse} ${filler_coarse} ${event_fine} ${event_frame}
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /event/aida_event/framenet/new_event_dependency.py \
    ${rsd_source} ${core_nlp_output_path} \
    ${edl_cs_coarse} ${filler_coarse} ${event_fine} ${event_frame} ${event_depen}
## Combine fine-grained typing and rule-based
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/pipeline_merge_m18.py \
    --cs_fnames ${event_fine} ${event_frame} ${event_depen} \
    --output_file ${event_fine_all}
## rewrite-args
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /event/aida_event/fine_grained/rewrite_args.py \
    ${event_fine_all} ${ltf_source} ${event_fine_all_clean}_tmp ${lang}
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /event/aida_event/fine_grained/rewrite_args.py \
    ${event_fine_all_clean}_tmp ${ltf_source} ${event_fine_all_clean} ${lang}
# echo "** Event coreference **"
docker run --rm -v ${data_root}:${data_root} --gpus '"device=1"' laituan245/spanbert_coref \
    -i ${event_fine_all_clean} -c ${event_corefer} -t ${event_corefer_confidence} -l ${ltf_source}
# generate 4tuple
docker run -i --rm -v ${data_root}:${data_root} \
    -v ${parent_child_tab_path}:${parent_child_tab_path} \
    -w /EventTimeArg --gpus '"device=1"' wenhycs/uiuc_event_time \
    python aida_event_time_pipeline.py \
    --time_cold_start_filename ${filler_coarse} \
    --event_cold_start_filename ${event_corefer} \
    --read_cs_event \
    --parent_children_filename ${parent_child_tab_path} \
    --ltf_path ${ltf_source} \
    --output_filename ${event_corefer_time} \
    --use_dct_as_default \
    --lang ${lang}
### updating informative mention
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /event/aida_event/postprocessing_event_informative_mentions.py \
    ${ltf_source} ${event_corefer_time} ${event_final} --eval m36
echo "Update event informative mention"

# Final Merge
echo "** Merging all items **"
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /postprocessing/pipeline_merge.py \
    --cs_fnames ${edl_cs_info_conf} ${edl_cs_color} ${relation_4tuple} ${event_final} \
    --output_file ${merged_cs} --eval m36
# multiple lorelei links
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/postprocessing_link_confidence.py \
    ${entity_lorelei_multiple} ${merged_cs} ${merged_cs_link} ${lorelei_link_private_data} --eval m36


######################################################
# Format converter
######################################################
# AIF converter
docker run --rm -v ${data_root}:${data_root} -v ${parent_child_tab_path}:${parent_child_tab_path} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/aida_entity/bin/python \
    /postprocessing/aif_converter_combine.py \
    --input_cs ${merged_cs_link} --ltf_dir ${ltf_source} \
    --output_ttl_dir ${ttl_initial} --lang ${lang}${source} --eval m36 \
    --evt_coref_score_tab ${event_corefer_confidence} \
    --source_tab ${parent_child_tab_path} \
    --ent_vec_dir ${data_root}/merge/mention \
    --ent_vec_files ${edl_vec_file} \
    --evt_vec_dir ${data_root}/merge/mention \
    --evt_vec_files ${evt_vec_file} \
    --event_embedding_from_file \
    --freebase_tab ${edl_tab_freebase} \
    --fine_grained_entity_type_path ${edl_json_fine} \
    --lorelei_link_mapping ${lorelei_link_private_data} \
    --parent_child_tab_path ${parent_child_tab_path}
docker run --rm -v ${data_root}:${data_root} -v ${parent_child_tab_path}:${parent_child_tab_path} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /postprocessing/postprocessing_rename_turtle.py \
    --language_id ${lang}${source} \
    --input_private_folder ${ttl_initial} \
    --output_folder ${ttl_final} \
    --parent_child_tab_path ${parent_child_tab_path} \
    --parent_child_mapping_sorted ${sorted}
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    chmod -R 777 ${ttl_final} ${ttl_initial}

echo "Final result in Cold Start Format is in "${merged_cs_link}
echo "Final result in RDF Format is in "${ttl_final}
