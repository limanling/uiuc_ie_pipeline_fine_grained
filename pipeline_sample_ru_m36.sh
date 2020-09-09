#!/usr/bin/env bash


#./pipeline_sample_ru.sh data/testdata_all/result/ru data/testdata_all/parent_children.sorted.tab ru


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
#ls ${ltf_source} > ${ltf_file_list}

# edl output
edl_output_dir=${data_root}/edl
edl_bio=${edl_output_dir}/${lang}.bio
edl_tab_nam_bio=${edl_output_dir}/${lang}.nam.tagged.bio
edl_tab_nam_filename=${lang}.nam.tagged.tab
edl_tab_nom_filename=${lang}.nom.tagged.tab
edl_tab_pro_filename=${lang}.pro.tagged.tab
edl_vec_file1=${lang}_nam_5type.mention.hidden.txt
edl_vec_file2=${lang}_nam_wv.mention.hidden.txt
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
translation_freebase=${edl_output_dir}/${lang}.linking.freebase.translations.json
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
chunk_file=${edl_output_dir}/chunk.txt

# relation output
relation_result_dir=${data_root}/relation   # final cs output file path
relation_cs_coarse=${relation_result_dir}/${lang}.rel.cs # final cs output for relation
relation_cs_fine=${relation_result_dir}/${lang}/${lang}.fine_rel.cs # final cs output for relation
new_relation_coarse=${relation_result_dir}/new_relation_${lang}.cs

# event output
event_result_dir=${data_root}/event
event_coarse_without_time=${event_result_dir}/events.cs
event_coarse_with_time=${event_result_dir}/events_tme.cs
event_fine=${event_result_dir}/events_fine.cs
event_frame=${event_result_dir}/events_fine_framenet.cs
event_depen=${event_result_dir}/events_fine_depen.cs
event_fine_all=${event_result_dir}/events_fine_all.cs
event_fine_all_clean=${event_result_dir}/events_fine_all_clean.cs
event_corefer=${event_result_dir}/events_corefer.cs
event_corefer_confidence=${event_result_dir}/events_corefer_confidence.tab
event_corefer_time=${event_result_dir}/events_4tuple.cs  #events_corefer_timefix.cs
event_final=${event_result_dir}/events_info.cs
ltf_txt_path=${event_result_dir}/'ltf_txt'
framenet_path=${event_result_dir}/'framenet_res'

# final output
merged_cs=${data_root}/${lang}${source}_full.cs
merged_cs_link=${data_root}/${lang}${source}_full_link.cs
ttl_initial=${data_root}/initial
ttl_initial_private=${data_root}/initial_private_data
ttl_final=${data_root}/final

######################################################
# Running scripts
######################################################

# EDL
# entity extraction
echo "** Extracting entities **"
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i --network="host" limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /entity/aida_edl/edl.py \
    ${ltf_source} ${rsd_source} ${lang} \
    ${edl_tab_nam} ${edl_tab_nom} ${edl_tab_pro} \
    ${entity_fine_model} ${edl_output_dir}
## linking
echo "** Linking entities to KB **"
docker run -v ${PWD}/system/aida_edl/edl_data:/data \
    -v ${edl_output_dir}:/testdata_${lang}${source} \
    --link db:mongo panx27/edl \
    python ./projs/docker_aida19/aida19.py \
    ${lang} \
    /testdata_${lang}${source}/${edl_tab_nam_filename} \
    /testdata_${lang}${source}/${edl_tab_nom_filename} \
    /testdata_${lang}${source}/${edl_tab_pro_filename} \
    /testdata_${lang}${source} \
    m36
## nominal coreference for ru and uk
docker run --rm -v ${data_root}:/uiuc/${data_root} -w /scr -i dylandilu/chuck_coreference \
    python appos_extract.py \
    --udp_dir /uiuc/${udp_dir} \
    --edl_tab_path /uiuc/${edl_tab_link} \
    --path_out_coref /uiuc/${edl_tab_final}
## tab2cs
docker run --rm -v ${data_root}:${data_root} -w `pwd`  -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /entity/aida_edl/tab2cs.py \
    ${edl_tab_final} ${edl_cs_coarse} 'EDL'

# Relation Extraction (coarse-grained)
echo "** Extraction relations **"
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/aida_relation_coarse/bin/python \
    -u /relation/CoarseRelationExtraction/exec_relation_extraction.py \
    -i ${lang} \
    -l ${ltf_file_list} \
    -f ${ltf_source} \
    -e ${edl_cs_coarse} \
    -t ${edl_tab_final} \
    -o ${relation_cs_coarse}
## Filler Extraction & new relation
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
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i --network="host" limanling/uiuc_ie_m36 \
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

# Event (Coarse)
echo "** Extracting events for "${lang}" **"
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
   /opt/conda/envs/ru_event/bin/python \
   /ru_event/${lang}_event/${lang}_event_backend.py \
   --ltf_folder_path ${ltf_source} \
   --input_edl_bio_file_path ${edl_tab_nam_bio} \
   --input_rsd_folder_path ${rsd_source} \
   --entity_cs_file_path ${edl_cs_coarse} \
   --output_dir ${event_result_dir} \
   --output_event_cs ${event_coarse_without_time}
## Add time expression
docker run -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /event/aida_event/postprocessing_add_time_expression.py \
    ${ltf_source} ${filler_coarse} ${event_coarse_without_time} ${event_coarse_with_time}
echo ${event_coarse_with_time}

# Relation Extraction (fine)
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    -u /relation/FineRelationExtraction/EVALfine_grained_relations.py \
    --lang_id ${lang} \
    --ltf_dir ${ltf_source} \
    --rsd_dir ${rsd_source} \
    --cs_fnames ${edl_cs_coarse} ${filler_coarse_color} ${relation_cs_coarse} ${new_relation_coarse}  ${event_coarse_without_time} \
    --fine_ent_type_tab ${edl_tab_freebase} \
    --fine_ent_type_json ${edl_json_fine} \
    --outdir ${relation_result_dir} \
    --fine_grained
##   --reuse_cache \
##   --use_gpu \
## Postprocessing, adding informative justification
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/pipeline_merge_m18.py \
    --cs_fnames ${edl_cs_fine} ${filler_fine} \
    --output_file ${edl_cs_fine_all}
echo "add protester"
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i --network="host" limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /entity/aida_edl/add_protester.py \
    ${event_coarse_without_time} ${edl_cs_fine_all} ${edl_cs_fine_protester}
echo "** Informative Justification **"
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /entity/aida_edl/entity_informative.py ${chunk_file} ${edl_cs_fine_protester} ${edl_cs_info}
## update mention confidence
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/rewrite_mention_confidence.py \
    ${lang}${source} ${edl_tab_nam} ${edl_tab_nom} ${edl_tab_pro} \
    ${edl_tab_link} ${entity_lorelei_multiple} ${ltf_source} \
    ${edl_cs_info} ${edl_cs_info_conf} ${conf_all}


## Event (Fine-grained)
echo "** Event fine-grained typing **"
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /event/aida_event/fine_grained/fine_grained_events.py \
    ${lang} ${ltf_source} ${edl_json_fine} ${edl_tab_freebase} \
    ${edl_cs_coarse} ${event_coarse_without_time} ${event_fine} \
    --filler_coarse ${filler_coarse} \
    --entity_finegrain_aida ${edl_cs_fine_all}
## rewrite-args
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /event/aida_event/fine_grained/rewrite_args.py \
    ${event_fine} ${ltf_source} ${event_fine_all_clean}_tmp ${lang}
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /event/aida_event/fine_grained/rewrite_args.py \
    ${event_fine_all_clean}_tmp ${ltf_source} ${event_fine_all_clean} ${lang}
echo "Fix time and format"
# Event coreference
echo "** Event coreference **"
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i --network="host" limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /event/aida_event_coreference/gail_event_coreference_test.py \
    -i ${event_fine_all_clean} -o ${event_corefer} -c ${event_corefer_confidence} -r ${rsd_source} -l ${lang}
# generate 4tuple
docker run -i -t --rm -v ${data_root}:${data_root} \
    -v ${parent_child_tab_path}:${parent_child_tab_path} \
    -w /EventTimeArg wenhycs/uiuc_event_time \
    python aida_event_time_pipeline.py \
    --time_cold_start_filename ${filler_coarse} \
    --event_cold_start_filename ${event_corefer} \
    --parent_children_filename ${parent_child_tab_path} \
    --output_filename ${event_corefer_time} \
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
    --cs_fnames ${edl_cs_info_conf} ${edl_cs_color} ${relation_cs_fine} ${event_final} \
    --output_file ${merged_cs} --eval m36
# multiple freebase links
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/postprocessing_link_freebase.py \
    ${edl_tab_freebase} ${merged_cs} ${freebase_private_data}
# multiple lorelei links
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /aida_utilities/postprocessing_link_confidence.py \
    ${entity_lorelei_multiple} ${merged_cs} ${merged_cs_link} ${lorelei_link_private_data}


######################################################
# Format converter
######################################################

# AIF converter
docker run --rm -v ${data_root}:${data_root} -v ${parent_child_tab_path}:${parent_child_tab_path} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/aida_entity/bin/python \
    /postprocessing/aif_converter.py \
    --input_cs ${merged_cs_link} --ltf_dir ${ltf_source} \
    --output_ttl_dir ${ttl_initial} --lang ${lang}${source} --eval m36 \
    --evt_coref_score_tab ${event_corefer_confidence} \
    --source_tab ${parent_child_tab_path}
# Append private information
docker run --rm -v ${data_root}:${data_root} -v ${parent_child_tab_path}:${parent_child_tab_path} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/aida_entity/bin/python \
    /postprocessing/postprocessing_append_private_data_m36.py \
    --language_id ${lang}${source} \
    --ltf_dir ${ltf_source} \
    --initial_folder ${ttl_initial} \
    --output_folder ${ttl_initial_private} \
    --fine_grained_entity_type_path ${edl_json_fine} \
    --freebase_link_mapping ${freebase_private_data} \
    --lorelei_link_mapping ${lorelei_link_private_data} \
    --parent_child_tab_path ${parent_child_tab_path} \
    --parent_child_mapping_sorted ${sorted} \
    --ent_vec_dir ${edl_output_dir} \
    --ent_vec_files ${edl_vec_file1} ${edl_vec_file2} \
    --edl_tab ${edl_tab_final} \
    --eval m36
    # --translation_path ${translation_freebase}
docker run --rm -v ${data_root}:${data_root} -v ${parent_child_tab_path}:${parent_child_tab_path} -w `pwd` -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /postprocessing/postprocessing_rename_turtle.py \
    --language_id ${lang}${source} \
    --input_private_folder ${ttl_initial_private} \
    --output_folder ${ttl_final} \
    --parent_child_tab_path ${parent_child_tab_path} \
    --parent_child_mapping_sorted ${sorted}
docker run --rm -v ${data_root}:${data_root} -w `pwd` -i limanling/uiuc_ie_m36 \
    chmod -R 777 ${ttl_final} ${ttl_initial_private} ${ttl_initial}

echo "Final result in Cold Start Format is in "${merged_cs_link}
echo "Final result in RDF Format is in "${ttl_final}
