#!/usr/bin/env bash

data_root="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E32_gpu_1210"
parent_child_tab_path="/shared/nas/data/m1/AIDA_Data/LDC_raw_data/LDC2020E32_AIDA_TAC_SM-KBP_2020_Evaluation_Source_Data/docs/parent_children.tab"
ltf_dir="/shared/nas/data/m1/AIDA_Data/LDC_raw_data/LDC2020E32_AIDA_TAC_SM-KBP_2020_Evaluation_Source_Data/data/ltf/ltf"

output_ttl=${data_root}"/merged_ttl_eval01_coref" 
output_ttl_test=${data_root}"/merged_ttl_eval01_clean_coref"
cu_merged_ttl=${data_root}"/merged_ttl_cu_vision_sent_coref"
variant=1
final_ttl=${data_root}"/merged_all_clean_coref"
final_ttl_str=${data_root}"/merged_all_clean_coref_str"
final_ttl_str_fix=${data_root}"/merged_all_clean_coref"

# output_ttl=${data_root}"/merged_ttl_eval01" 
# output_ttl_test=${data_root}"/merged_ttl_eval01_clean"
# cu_merged_ttl=${data_root}"/merged_ttl_cu_vision_sent"
# variant=1
# final_ttl=${data_root}"/merged_all_clean"
# final_ttl_str=${data_root}"/merged_all_clean_str"
# # final_ttl_str_fix=${data_root}"/merged_all_clean_str_fix"

sentiment_dir="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E32_gpu_1210/cu_sentiment"
relation_cs_file_en="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E32_gpu_1210/cu_sentiment/en.multi_sent.sponsor_assignblame.cs"
relation_cs_file_ru="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E32_gpu_1210/cu_sentiment/ru.multi_sent.sponsor_assignblame.cs"
relation_cs_file_es="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E32_gpu_1210/cu_sentiment/es.multi_sent.sponsor_assignblame.cs"
evt_source_tab_en="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E32_gpu_1210/cu_sentiment/en.event_sources.cs"
evt_source_tab_ru="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E32_gpu_1210/cu_sentiment/ru.event_sources.cs"
evt_source_tab_es="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E32_gpu_1210/cu_sentiment/es.event_sources.cs"

docker run --rm -v ${data_root}:${data_root} -v ${parent_child_tab_path}:${parent_child_tab_path} -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /postprocessing/postprocessing_cleankb_params_caci.py \
    ${data_root}/cleankb.param ${output_ttl} ${output_ttl_test} ${variant} \
    --parent_child_tab_path ${parent_child_tab_path} \
    --eval m36
docker run --rm -v ${data_root}:${data_root} \
    -v ${parent_child_tab_path}:${parent_child_tab_path} \
    -w /aida-tools-java11 -i -t limanling/aida-tools \
    /aida-tools-java11/aida-eval-tools/target/appassembler/bin/cleanKB  \
    ${data_root}/cleankb.param

# merge sentiment
for thread_id in {0..9}
do
    docker run --rm -v ${data_root}:${data_root} -v ${parent_child_tab_path}:${parent_child_tab_path} -v ${sentiment_dir}:${sentiment_dir} -i limanling/uiuc_ie_m36 \
        /opt/conda/envs/aida_entity/bin/python \
        /postprocessing/postprocessing_add_relation.py \
        --relation_cs_files ${relation_cs_file_en} ${relation_cs_file_ru} ${relation_cs_file_es} \
        --event_source_files ${evt_source_tab_en} ${evt_source_tab_ru} ${evt_source_tab_es} \
        --input_ttl_folder ${output_ttl} \
        --output_ttl_folder ${cu_merged_ttl} \
        --parent_child_tab_path ${parent_child_tab_path} \
        --thread 10 --current_thread ${thread_id} &
done
wait

docker run --rm -v ${data_root}:${data_root} -i limanling/uiuc_ie_m36 chmod 777 -R ${cu_merged_ttl}

docker run --rm -v ${data_root}:${data_root} -v ${parent_child_tab_path}:${parent_child_tab_path} -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /postprocessing/postprocessing_cleankb_params_caci.py \
    ${data_root}/cleankb.param ${cu_merged_ttl} ${final_ttl} ${variant} \
    --parent_child_tab_path ${parent_child_tab_path} \
    --eval m36
docker run --rm -v ${data_root}:${data_root} \
    -v ${parent_child_tab_path}:${parent_child_tab_path} \
    -w /aida-tools-java11 -i -t limanling/aida-tools \
    /aida-tools-java11/aida-eval-tools/target/appassembler/bin/cleanKB  \
    ${data_root}/cleankb.param

for thread_id in {0..19}
do
    docker run --rm -v ${final_ttl}:${final_ttl} -v ${final_ttl_str}:${final_ttl_str} -v ${ltf_dir}:${ltf_dir} -i limanling/uiuc_ie_m36 \
        /opt/conda/envs/py36/bin/python \
        /postprocessing/aif_addstr.py \
        --input_ttl_folder ${final_ttl} \
        --output_ttl_dir ${final_ttl_str} \
        --ltf_dir ${ltf_dir} \
        --thread 20 --current_thread ${thread_id} &
done
wait