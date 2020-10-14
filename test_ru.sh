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
ltf_source=${data_root_ru}/ltf
# rsd source folder path
rsd_source=${data_root_ru}/rsd
# file list of ltf files (only file names)
ltf_file_list=${data_root_ru}/ltf_lst

# edl output
edl_output_dir=${data_root_ru}/edl
edl_cs_oneie=${data_root_ru}/merge/cs/entity.cs
edl_bio=${edl_output_dir_ru}/${lang_ru}.bio
edl_tab_nam_bio=${data_root_ru}/merge/mention/${lang_ru}.nam.bio
edl_tab_nam_filename=${lang_ru}.nam.tab
edl_tab_nom_filename=${lang_ru}.nom.tab
edl_tab_pro_filename=${lang_ru}.pro.tab
edl_vec_file=${lang_ru}.mention.hidden.txt
evt_vec_file=${lang_ru}.trigger.hidden.txt
edl_tab_nam=${data_root_ru}/merge/mention/${lang_ru}.nam.tab
edl_tab_nom=${data_root_ru}/merge/mention/${lang_ru}.nom.tab
edl_tab_pro=${data_root_ru}/merge/mention/${lang_ru}.pro.tab
edl_tab_link=${edl_output_dir_ru}/${lang_ru}.linking.tab
edl_tab_link_fb=${edl_output_dir_ru}/${lang_ru}.linking.freebase.tab
edl_tab_coref_ru=${edl_output_dir_ru}/${lang_ru}.coreference.tab
geonames_features=${edl_output_dir_ru}/${lang_ru}.linking.geo.json
edl_tab_final=${edl_output_dir_ru}/merged_final.tab
edl_cs_coarse=${edl_output_dir_ru}/merged.cs
entity_fine_model=${edl_output_dir_ru}/merged_fine.tsv
edl_cs_fine=${edl_output_dir_ru}/merged_fine.cs
edl_json_fine=${edl_output_dir_ru}/${lang_ru}.linking.freebase.fine.json
edl_tab_freebase=${edl_output_dir_ru}/${lang_ru}.linking.freebase.tab
freebase_private_data=${edl_output_dir_ru}/freebase_private_data.json
lorelei_link_private_data=${edl_output_dir_ru}/lorelei_private_data.json
entity_lorelei_multiple=${edl_output_dir_ru}/${lang_ru}.linking.tab.candidates.json
edl_cs_fine_all=${edl_output_dir_ru}/merged_all_fine.cs
edl_cs_fine_protester=${edl_output_dir_ru}/merged_all_fine_protester.cs
edl_cs_info=${edl_output_dir_ru}/merged_all_fine_info.cs
edl_cs_info_conf=${edl_output_dir_ru}/merged_all_fine_info_conf.cs
edl_tab_color=${edl_output_dir_ru}/${lang_ru}.linking.col.tab
edl_cs_color=${edl_output_dir_ru}/${lang_ru}.color.cs
conf_all=${edl_output_dir_ru}/all_conf.txt
ground_truth_tab_dir=${edl_output_dir_ru}/ldc_anno_matched

# filler output
core_nlp_output_path=${data_root_ru}/corenlp
filler_coarse=${edl_output_dir_ru}/filler_${lang_ru}.cs
filler_coarse_color=${edl_output_dir_ru}/filler_${lang_ru}_all.cs
filler_fine=${edl_output_dir_ru}/filler_fine.cs
udp_dir=${data_root_ru}/udp
chunk_file=${data_root_ru}/edl/chunk.txt

# relation output
relation_cs_oneie=${data_root_ru}/merge/cs/relation.cs # final cs output for relation
relation_result_dir=${relation_result_dir_ru}   # final cs output file path
relation_cs_coarse=${relation_result_dir_ru}/${lang_ru}.rel.cs # final cs output for relation
relation_cs_fine=${relation_result_dir_ru}/${lang_ru}/${lang_ru}.fine_rel.cs # final cs output for relation
relation_4tuple=${relation_result_dir_ru}/${lang_ru}/${lang_ru}_rel_4tuple.cs
new_relation_coarse=${relation_result_dir_ru}/new_relation_${lang_ru}.cs

# event output
event_result_dir=${event_result_dir_ru}
event_coarse_oneie=${data_root_ru}/merge/cs/event.cs
event_coarse_without_time=${event_result_dir_ru}/event_rewrite.cs
event_coarse_with_time=${event_result_dir_ru}/events_tme.cs
event_fine=${event_result_dir_ru}/events_fine.cs
event_frame=${event_result_dir_ru}/events_fine_framenet.cs
event_depen=${event_result_dir_ru}/events_fine_depen.cs
event_fine_all=${event_result_dir_ru}/events_fine_all.cs
event_fine_all_clean=${event_result_dir_ru}/events_fine_all_clean.cs
event_corefer=${event_result_dir_ru}/events_corefer.cs
event_corefer_confidence=${event_result_dir_ru}/events_corefer_confidence.tab
event_corefer_time=${event_result_dir_ru}/events_4tuple.cs 
event_final=${event_result_dir_ru}/events_info.cs
ltf_txt_path=${event_result_dir_ru}/'ltf_txt'
framenet_path=${event_result_dir_ru}/'framenet_res'

# final output
merged_cs=${data_root_ru}/${lang_ru}${source_ru}_full.cs
merged_cs_link=${data_root_ru}/${lang_ru}${source_ru}_full_link.cs
ttl_initial=${data_root_ru}/initial
ttl_initial_private=${data_root_ru}/initial_private_data
ttl_final=${data_root_ru}/final

######################################################
# Running scripts
######################################################

# # EDL
# # entity extraction
# echo "** Extracting coarse-grained entities, relations, and events **"
docker run --rm -i -v ${data_root_ru}:${data_root_ru} -w /oneie --gpus '"device=1"' limteng/oneie_aida_m36 /opt/conda/bin/python /oneie/predict.py -i ${ltf_source_ru} -o ${data_root_ru} -l ${lang_ru} --output_hidden
# fine-grained typing by model
echo "fine-grained typing started"
docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd` -i --network="host" limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /entity_api/entity_api/typing_m36.py ${lang_ru} ${data_root_ru}/merge/mention/${lang_ru}.nam.bio ${edl_output_dir_ru}/merged_fine.tsv
echo "fine-grained typing finished"

# # linking
# echo "** Linking entities to KB **"
docker run -v ${PWD_ru}/system/aida_edl/edl_data:/data -v ${data_root_ru}:/testdata_${lang_ru}${source_ru} --link db:mongo panx27/edl python ./projs/docker_aida19/aida19.py ${lang_ru} /testdata_${lang_ru}${source_ru}/merge/mention/${lang_ru}.nam.tab /testdata_${lang_ru}${source_ru}/merge/mention/${lang_ru}.nom.tab /testdata_${lang_ru}${source_ru}/merge/mention/${lang_ru}.pro.tab /testdata_${lang_ru}${source_ru}/edl m36
# ## nominal coreference
docker run --rm -v ${data_root_ru}:${data_root_ru} -w /scr -i dylandilu/chuck_coreference python appos_extract.py --udp_dir ${data_root_ru}/udp --edl_tab_path ${edl_output_dir_ru}/${lang_ru}.linking.tab --path_out_coref ${edl_output_dir_ru}/merged_final.tab
# ## tab2cs
docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd`  -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /entity/aida_edl/tab2cs.py ${edl_output_dir_ru}/merged_final.tab ${edl_output_dir_ru}/merged.cs 'EDL'
docker run --rm -v ${data_root_ru}:${data_root_ru} -v ${data_root_ru}:${data_root_ru} -w `pwd`  -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /aida_utilities/rewrite_entity_id.py ${data_root_ru}/merge/cs/entity.cs ${data_root_ru}/merge/cs/relation.cs ${data_root_ru}/merge/cs/event.cs ${edl_output_dir_ru}/merged.cs ${relation_result_dir_ru}/${lang_ru}.rel.cs ${event_result_dir_ru}/event_rewrite.cs

# # # Filler Extraction & new relation
# docker run --rm -v ${data_root_ru}:${data_root_ru} -w /scr -i dylandilu/filler python extract_filler_relation.py --corenlp_dir ${data_root_ru}/corenlp --ltf_dir ${ltf_source_ru} --edl_path ${edl_output_dir_ru}/merged.cs --text_dir ${rsd_source_ru} --path_relation ${relation_result_dir_ru}/new_relation_${lang_ru}.cs --path_filler ${edl_output_dir_ru}/filler_${lang_ru}.cs --lang ${lang_ru}

# ## Fine-grained Entity
# echo "** Fine-grained entity typing **"
# docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd` -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /entity/aida_edl/fine_grained_entity.py ${lang_ru} ${edl_output_dir_ru}/${lang_ru}.linking.freebase.fine.json ${edl_output_dir_ru}/${lang_ru}.linking.freebase.tab ${edl_output_dir_ru}/merged_fine.tsv ${edl_output_dir_ru}/${lang_ru}.linking.geo.json ${edl_output_dir_ru}/merged.cs ${edl_output_dir_ru}/merged_fine.cs ${edl_output_dir_ru}/filler_fine.cs --filler_coarse ${edl_output_dir_ru}/filler_${lang_ru}.cs --ground_truth_tab_dir ${edl_output_dir_ru}/ldc_anno_matched --ltf_dir ${ltf_source_ru} --rsd_dir ${rsd_source_ru} --eval m36
# docker run -v ${data_root_ru}:${data_root_ru} -w `pwd` -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /relation/FineRelationExtraction/utils/color_fillers.py --en_color_fill_tab_fname ${edl_output_dir_ru}/${lang_ru}.linking.col.tab --en_fill_cs_fname ${edl_output_dir_ru}/filler_${lang_ru}.cs --en_combo_outfname ${edl_output_dir_ru}/filler_${lang_ru}_all.cs --en_color_outfname ${edl_output_dir_ru}/${lang_ru}.color.cs
docker run -v ${data_root_ru}:${data_root_ru} -w `pwd` -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /event/aida_event/postprocessing_add_time_expression.py ${ltf_source_ru} ${edl_output_dir_ru}/filler_${lang_ru}.cs ${event_result_dir_ru}/event_rewrite.cs ${event_result_dir_ru}/events_tme.cs

# Relation Extraction (fine)
# docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd` -i --gpus '"device=1"' limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python -u /relation/FineRelationExtraction/EVALfine_grained_relations.py --lang_id ${lang_ru} --ltf_dir ${ltf_source_ru} --rsd_dir ${rsd_source_ru} --cs_fnames ${edl_output_dir_ru}/merged.cs ${edl_output_dir_ru}/filler_${lang_ru}_all.cs ${relation_result_dir_ru}/${lang_ru}.rel.cs ${relation_result_dir_ru}/new_relation_${lang_ru}.cs ${event_result_dir_ru}/event_rewrite.cs --fine_ent_type_tab ${edl_output_dir_ru}/${lang_ru}.linking.freebase.tab --fine_ent_type_json ${edl_output_dir_ru}/${lang_ru}.linking.freebase.fine.json --outdir ${relation_result_dir_ru} --fine_grained --use_gpu
##   --reuse_cache \
# docker run -i --rm -v ${data_root_ru}:${data_root_ru} -v ${parent_child_tab_path_ru}:${parent_child_tab_path_ru} -w /EventTimeArg --gpus '"device=1"' wenhycs/uiuc_event_time python aida_event_time_pipeline.py --relation_cold_start_filename ${relation_result_dir_ru}/${lang_ru}/${lang_ru}.fine_rel.cs --relation --parent_children_filename ${parent_child_tab_path_ru} --output_filename ${relation_result_dir_ru}/${lang_ru}/${lang_ru}_rel_4tuple.cs

## Postprocessing, adding informative justification
# docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd` -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /aida_utilities/pipeline_merge_m18.py --cs_fnames ${edl_output_dir_ru}/merged_fine.cs ${edl_output_dir_ru}/filler_fine.cs --output_file ${edl_output_dir_ru}/merged_all_fine.cs
echo "add protester"
# docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd` -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /entity/aida_edl/add_protester.py ${event_result_dir_ru}/event_rewrite.cs ${edl_output_dir_ru}/merged_all_fine.cs ${edl_output_dir_ru}/merged_all_fine_protester.cs
echo "** Informative Justification **"
docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd` -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /entity/aida_edl/entity_informative.py ${edl_output_dir_ru}/chunk.txt ${edl_output_dir_ru}/merged_all_fine_protester.cs ${edl_output_dir_ru}/merged_all_fine_info.cs
## update mention confidence
# docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd` -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /aida_utilities/rewrite_mention_confidence.py ${lang_ru}${source_ru} ${data_root_ru}/merge/mention/${lang_ru}.nam.tab ${data_root_ru}/merge/mention/${lang_ru}.nom.tab ${data_root_ru}/merge/mention/${lang_ru}.pro.tab ${edl_output_dir_ru}/${lang_ru}.linking.tab ${edl_output_dir_ru}/${lang_ru}.linking.tab.candidates.json ${ltf_source_ru} ${edl_output_dir_ru}/merged_all_fine_info.cs ${edl_output_dir_ru}/merged_all_fine_info_conf.cs ${edl_output_dir_ru}/all_conf.txt
# Event (Fine-grained)
echo "** Event fine-grained typing **"
# docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd` -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /event/aida_event/fine_grained/fine_grained_events.py ${lang_ru} ${ltf_source_ru} ${edl_output_dir_ru}/${lang_ru}.linking.freebase.fine.json ${edl_output_dir_ru}/${lang_ru}.linking.freebase.tab ${edl_output_dir_ru}/merged.cs ${event_result_dir_ru}/event_rewrite.cs ${event_result_dir_ru}/events_fine.cs --filler_coarse ${edl_output_dir_ru}/filler_${lang_ru}.cs --entity_finegrain_aida ${edl_output_dir_ru}/merged_all_fine.cs
## rewrite-args
# docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd` -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /event/aida_event/fine_grained/rewrite_args.py ${event_result_dir_ru}/events_fine.cs ${ltf_source_ru} ${event_result_dir_ru}/events_fine_all_clean.cs_tmp ${lang_ru}
# docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd` -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /event/aida_event/fine_grained/rewrite_args.py ${event_result_dir_ru}/events_fine_all_clean.cs_tmp ${ltf_source_ru} ${event_result_dir_ru}/events_fine_all_clean.cs ${lang_ru}
# echo "** Event coreference **"
# docker run --rm -v ${data_root_ru}:${data_root_ru} --gpus '"device=1"' laituan245/spanbert_coref -i ${event_result_dir_ru}/events_fine_all_clean.cs -c ${event_result_dir_ru}/events_corefer.cs -t ${event_result_dir_ru}/events_corefer_confidence.tab -l ${ltf_source_ru}
docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd` -i --network="host" limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /event/aida_event_coreference/gail_event_coreference_test.py -i ${event_result_dir_ru}/events_fine_all_clean.cs -o ${event_result_dir_ru}/events_corefer.cs -c ${event_result_dir_ru}/events_corefer_confidence.tab -r ${rsd_source_ru} -l ${lang_ru}
# generate 4tuple
docker run -i --rm -v ${data_root_ru}:${data_root_ru} -v ${parent_child_tab_path_ru}:${parent_child_tab_path_ru} -w /EventTimeArg --gpus '"device=1"' wenhycs/uiuc_event_time python aida_event_time_pipeline.py --time_cold_start_filename ${edl_output_dir_ru}/filler_${lang_ru}.cs --event_cold_start_filename ${event_result_dir_ru}/events_corefer.cs --parent_children_filename ${parent_child_tab_path_ru} --output_filename ${event_result_dir_ru}/events_4tuple.cs --lang ${lang_ru}
### updating informative mention
# docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd` -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /event/aida_event/postprocessing_event_informative_mentions.py ${ltf_source_ru} ${event_result_dir_ru}/events_4tuple.cs ${event_result_dir_ru}/events_info.cs --eval m36
echo "Update event informative mention"

# Final Merge
echo "** Merging all items **"
docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd` -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /postprocessing/pipeline_merge.py --cs_fnames ${edl_output_dir_ru}/merged_all_fine_info_conf.cs ${edl_output_dir_ru}/${lang_ru}.color.cs ${relation_result_dir_ru}/${lang_ru}/${lang_ru}_rel_4tuple.cs ${event_result_dir_ru}/events_info.cs --output_file ${data_root_ru}/${lang_ru}${source_ru}_full.cs --eval m36
# multiple lorelei links
docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd` -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /aida_utilities/postprocessing_link_confidence.py ${edl_output_dir_ru}/${lang_ru}.linking.tab.candidates.json ${data_root_ru}/${lang_ru}${source_ru}_full.cs ${data_root_ru}/${lang_ru}${source_ru}_full_link.cs ${edl_output_dir_ru}/lorelei_private_data.json --eval m36


######################################################
# Format converter
######################################################
# AIF converter
docker run --rm -v ${data_root_ru}:${data_root_ru} -v ${parent_child_tab_path_ru}:${parent_child_tab_path_ru} -w `pwd` -i limanling/uiuc_ie_m36 /opt/conda/envs/aida_entity/bin/python /postprocessing/aif_converter_combine.py --input_cs ${data_root_ru}/${lang_ru}${source_ru}_full_link.cs --ltf_dir ${ltf_source_ru} --output_ttl_dir ${data_root_ru}/initial --lang ${lang_ru}${source_ru} --eval m36 --evt_coref_score_tab ${event_result_dir_ru}/events_corefer_confidence.tab --source_tab ${parent_child_tab_path_ru} --ent_vec_dir ${data_root_ru}/merge/mention --ent_vec_files ${lang_ru}.mention.hidden.txt --evt_vec_dir ${data_root_ru}/merge/mention --evt_vec_files ${lang_ru}.trigger.hidden.txt --event_embedding_from_file --freebase_tab ${edl_output_dir_ru}/${lang_ru}.linking.freebase.tab --fine_grained_entity_type_path ${edl_output_dir_ru}/${lang_ru}.linking.freebase.fine.json --lorelei_link_mapping ${edl_output_dir_ru}/lorelei_private_data.json --parent_child_tab_path ${parent_child_tab_path_ru}
docker run --rm -v ${data_root_ru}:${data_root_ru} -v ${parent_child_tab_path_ru}:${parent_child_tab_path_ru} -w `pwd` -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /postprocessing/postprocessing_rename_turtle.py --language_id ${lang_ru}${source_ru} --input_private_folder ${data_root_ru}/initial --output_folder ${data_root_ru}/final --parent_child_tab_path ${parent_child_tab_path_ru} --parent_child_mapping_sorted ${sorted_ru}
docker run --rm -v ${data_root_ru}:${data_root_ru} -w `pwd` -i limanling/uiuc_ie_m36 chmod -R 777 ${data_root_ru}/final ${data_root_ru}/initial

echo "Final result in Cold Start Format is in "${data_root_ru}/${lang_ru}${source_ru}_full_link.cs
echo "Final result in RDF Format is in "${data_root_ru}/final
