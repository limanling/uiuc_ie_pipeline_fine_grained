#!/usr/bin/env bash

data_root="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E11_new"
parent_child_tab_path="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/bak_output_dryrun_E29_ann/parent_children.tab"
output_ttl=${data_root}"/kb/ttl" 
# all_merged_ttl=${output_ttl}
variant=1
final_ttl=${data_root}"/final_clean"


# docker run --rm -v ${data_root}:${data_root} -i limanling/uiuc_ie_m36 \
#     /opt/conda/envs/py36/bin/python \
#     /postprocessing/postprocessing_combine_turtle_from_all_sources.py \
#     --root_folder ${data_root} \
#     --final_dir_name 'final' \
#     --output_folder ${output_ttl}
# echo "Final output of English, Russian, Spanish in "${output_ttl}

# # # merge sentiment
# # docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t limanling/uiuc_ie_m18 \
# #     /opt/conda/envs/py36/bin/python \
# #     /postprocessing/postprocessing_add_relation.py \
# #     --relation_cs_files ${language_id} \
# #     --input_ttl_folder ${cu_merged_ttl} \
# #     --output_ttl_folder ${all_merged_ttl} \
# #     --parent_child_tab_path ${parent_child_tab_path} \
# #     --child_column_idx ${child_column_idx} \
# #     --parent_column_idx ${root_column_idx}

# run docker python /shared/nas/data/m1/manling2/aida_docker/docker_m18/postprocessing/postprocessing_cleankb_params.py \
docker run --rm -v ${data_root}:${data_root} -v ${parent_child_tab_path}:${parent_child_tab_path} -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /postprocessing/postprocessing_cleankb_params.py \
    ${data_root}/cleankb.param ${output_ttl} ${final_ttl} ${variant} \
    --parent_child_tab_path ${parent_child_tab_path} \
    --eval m36
docker run --rm -v ${data_root}:/aida-tools-java11/sample_params/m36-eval/${data_root} \
    -v ${parent_child_tab_path}:/aida-tools-java11/sample_params/m36-eval/${parent_child_tab_path} \
    -w /aida-tools-java11 -i -t limanling/aida-tools \
    /aida-tools-java11/aida-eval-tools/target/appassembler/bin/cleanKB  \
    sample_params/m36-eval/${data_root}/cleankb.param


