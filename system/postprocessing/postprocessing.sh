#!/usr/bin/env bash

######################################################
# Arguments
######################################################
final_output_cs=data/test_post/en_full_link_conf.cs
data_root_lang=data/test_post
lang='en'
datasource=''
parent_child_tab_path=data/test_post/parent_children.tab
child_column_idx=3
root_column_idx=2

#data_root=$1
#parentChildMap=$2
#masterShotTable=$2
#lang=$2
#datasource=$3

language_id=${lang}${datasource}
fine_grained_entity_type_path=${data_root_lang}/edl/${lang}.linking.freebase.fine.json
freebase_link_mapping=${data_root_lang}/edl/freebase_private_data.json
lorelei_link_mapping=${data_root_lang}/edl/lorelei_private_data.json


# final output
#data_root_result=${data_root}/result
#data_root_lang=${data_root_result}/${lang}${datasource}
#final_output_cs=${data_root_lang}/${lang}${datasource}_full_link_conf.cs
initial_ttl=${data_root_lang}/initial
private_ttl=${data_root_lang}/initial_private_data
final_ttl=${data_root_lang}/final

#####################################################################
# postprocessing
#####################################################################

# ColdStart Format to AIF Format
echo "Generating AIF format"
## Generating parameter file
echo "inputKBFile: /aida-tools-master/sample_params/m18-eval/"${final_output_cs} > ${data_root_lang}/uiuc_converter_params_${lang}${datasource}
echo "outputAIFDirectory: /aida-tools-master/sample_params/m18-eval/"${initial_ttl} >> ${data_root_lang}/uiuc_converter_params_${lang}${datasource}
echo "baseURI: http://www.isi.edu/gaia" >> ${data_root_lang}/uiuc_converter_params_${lang}${datasource}
echo "systemURI: http://www.uiuc.edu" >> ${data_root_lang}/uiuc_converter_params_${lang}${datasource}
echo "mode: SHATTER" >> ${data_root_lang}/uiuc_converter_params_${lang}${datasource}
echo "includeDebugPrefLabels: true" >> ${data_root_lang}/uiuc_converter_params_${lang}${datasource}
echo "entityOntology: /AIDA-Interchange-Format-master/java/src/main/resources/com/ncc/aif/ontologies/LDCOntology" >> ${data_root_lang}/uiuc_converter_params_${lang}${datasource}
echo "relationOntology: /AIDA-Interchange-Format-master/java/src/main/resources/com/ncc/aif/ontologies/LDCOntology" >> ${data_root_lang}/uiuc_converter_params_${lang}${datasource}
echo "eventOntology: /AIDA-Interchange-Format-master/java/src/main/resources/com/ncc/aif/ontologies/LDCOntology" >> ${data_root_lang}/uiuc_converter_params_${lang}${datasource}
## Running converter
docker run --rm -v ${PWD}:/aida-tools-master/sample_params/m18-eval -w /aida-tools-master -i -t limanling/aida-tools \
    /aida-tools-master/aida-eval-tools/target/appassembler/bin/coldstart2AidaInterchange  \
    sample_params/m18-eval/${data_root_lang}/uiuc_converter_params_${lang}${datasource}

# Append private information
docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /postprocessing/postprocessing_append_private_data.py \
    --language_id ${language_id} \
    --initial_folder ${initial_ttl} \
    --output_folder ${private_ttl} \
    --fine_grained_entity_type_path ${fine_grained_entity_type_path} \
    --freebase_link_mapping ${freebase_link_mapping} \
    --lorelei_link_mapping ${lorelei_link_mapping}
#    --translation_path \

# Change the ttl names
docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /postprocessing/postprocessing_rename_turtle.py \
    --language_id ${language_id} \
    --input_private_folder ${private_ttl} \
    --output_folder ${final_ttl} \
    --parent_child_tab_path ${parent_child_tab_path} \
    --child_column_idx ${child_column_idx} \
    --parent_column_idx ${root_column_idx}

