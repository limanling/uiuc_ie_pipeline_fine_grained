#!/usr/bin/env bash

data_root_result="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E11_ann/en"
parent_child_tab_path="/shared/nas/data/m1/common/aida/LDC2020E11_AIDA_Phase_2_Practice_Topic_Source_Data_V1.0/docs/parent_children.tab"
masterShotTable_path="/shared/nas/data/m1/common/aida/LDC2020E11_AIDA_Phase_2_Practice_Topic_Source_Data_V1.0/docs/video_data.msb"
preprocessed_source_dir_from_uiuc="/shared/nas/data/m1/common/aida/LDC2020E11_AIDA_Phase_2_Practice_Topic_Source_Data_V1.0/data/ltf"
# ocr_path_from_OCR=""
all_merged_ttl="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E11_ann/en/final"
final_ttl="/shared/nas/data/m1/manling2/aida_docker_test/uiuc_ie_pipeline_fine_grained/output/output_dryrun_E11_ann/en/final_clean"
# # merge sentiment
# docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t limanling/uiuc_ie_m18 \
#     /opt/conda/envs/py36/bin/python \
#     /postprocessing/postprocessing_add_relation.py \
#     --relation_cs_files ${language_id} \
#     --input_ttl_folder ${cu_merged_ttl} \
#     --output_ttl_folder ${all_merged_ttl} \
#     --parent_child_tab_path ${parent_child_tab_path} \
#     --child_column_idx ${child_column_idx} \
#     --parent_column_idx ${root_column_idx}

# run docker
docker run --rm -v ${data_root}:/aida-tools-master/sample_params/m18-eval/${data_root} -w /aida-tools-master -i -t limanling/aida-tools \
    /aida-tools-master/aida-eval-tools/target/appassembler/bin/cleanKB  \
    sample_params/m18-eval/${data_root_result}/uiuc_clean_normal_params

