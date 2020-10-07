#!/usr/bin/env bash

# input
parent_child_tab_path="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/bak_output_dryrun_E29_ann/parent_children.tab"
data_root="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E11_new/vis/WORKING/columbia_vision_shared/cu_graph_merging_ttl/dryrun" 
output_ttl=${data_root}"/merged_ttl"
variant=1
# output
final_ttl=${data_root}"/final_clean"


docker run --rm -v ${output_ttl}:${output_ttl} -v ${final_ttl}:${final_ttl} -v ${parent_child_tab_path}:${parent_child_tab_path} -i limanling/uiuc_ie_m36 \
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


