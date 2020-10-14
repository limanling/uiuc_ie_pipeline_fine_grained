#!/usr/bin/env bash

data_root="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E11_new"
# data_root="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E29_oneie_entcoref"
parent_child_tab_path="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/bak_output_dryrun_E29_ann/parent_children.tab"
output_ttl=${data_root}"/kb/ttl" 
cu_merged_ttl=${data_root}"/merged_ttl_cu"
# all_merged_ttl=${output_ttl}
variant=1
final_ttl=${data_root}"/final_clean"
# asr_mapping_file=${data_root}"/final_clean"

sentiment_dir="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E11_new/cu_sentiment"
relation_cs_file_en="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E11_new/cu_sentiment/en.multi_sent.sponsor_assignblame.cs"
relation_cs_file_ru="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E11_new/cu_sentiment/ru.multi_sent.sponsor_assignblame.cs"
relation_cs_file_es="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E11_new/cu_sentiment/es.multi_sent.sponsor_assignblame.cs"

evt_source_tab_en="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E11_new/cu_sentiment/en.event_sources.cs"
evt_source_tab_ru="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E11_new/cu_sentiment/ru.event_sources.cs"
evt_source_tab_es="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E11_new/cu_sentiment/es.event_sources.cs"


# docker run --rm -v ${data_root}:${data_root} -i limanling/uiuc_ie_m36 \
#     /opt/conda/envs/py36/bin/python \
#     /postprocessing/postprocessing_combine_turtle_from_all_sources.py \
#     --root_folder ${data_root} \
#     --final_dir_name 'final' \
#     --output_folder ${output_ttl}
# echo "Final output of English, Russian, Spanish in "${output_ttl}

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
        # --asr_mapping ${asr_mapping_file} 
docker run --rm -v ${data_root}:${data_root} \
    -v ${parent_child_tab_path}:${parent_child_tab_path} \
    -w /aida-tools-java11 -i -t limanling/aida-tools \
    /aida-tools-java11/aida-eval-tools/target/appassembler/bin/cleanKB  \
    ${data_root}/cleankb.param


