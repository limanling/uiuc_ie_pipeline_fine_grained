#!/usr/bin/env bash

# merge sentiment
docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /postprocessing/postprocessing_add_relation.py \
    --relation_cs_files ${language_id} \
    --input_ttl_folder ${cu_merged_ttl} \
    --output_ttl_folder ${all_merged_ttl} \
    --parent_child_tab_path ${parent_child_tab_path} \
    --child_column_idx ${child_column_idx} \
    --parent_column_idx ${root_column_idx}

# clean KB
echo "parentChildMapFilenames: /aida-tools-master/sample_params/m18-eval/"${parent_child_tab_path} > ${data_root_result}/uiuc_clean_normal_params
echo "masterShotTable: /aida-tools-master/sample_params/m18-eval/"${masterShotTable_path} >> ${data_root_result}/uiuc_clean_normal_params
echo "sourceDir: /aida-tools-master/sample_params/m18-eval/"${preprocessed_source_dir_from_uiuc} >> ${data_root_result}/uiuc_clean_normal_params
echo "sampledOcrDir: /aida-tools-master/sample_params/m18-eval/"${ocr_path_from_OCR} >> ${data_root_result}/uiuc_clean_normal_params
echo "INCLUDE m18_cleaning.common.params" >> ${data_root_result}/uiuc_clean_normal_params
echo "kbsToRead: /aida-tools-master/sample_params/m18-eval/"${all_merged_ttl} >> ${data_root_result}/uiuc_clean_normal_params
echo "baseOutputDir: /aida-tools-master/sample_params/m18-eval/"${final_ttl} >> ${data_root_result}/uiuc_clean_normal_params
echo "variantNum: 1" >> ${data_root_result}/uiuc_clean_normal_params
echo "suppressValidation: true" >> ${data_root_result}/uiuc_clean_normal_params
# run docker
docker run --rm -v ${PWD}:/aida-tools-master/sample_params/m18-eval -w /aida-tools-master -i -t limanling/aida-tools \
    /aida-tools-master/aida-eval-tools/target/appassembler/bin/cleanKB  \
    sample_params/m18-eval/${data_root_result}/uiuc_clean_normal_params

