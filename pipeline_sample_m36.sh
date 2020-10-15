#!/usr/bin/env bash

######################################################
# Arguments
######################################################
# input root path
data_root=$1
kb_dir=$2
output_dir=$3
parent_child_tab_path=$4
asr_en_path=$5
ocr_en_path=$6
ocr_ru_path=$7
thread_num=$8
sorted=0
eval='m36'
variant=1

# data folder that specified with language
data_root_result=${output_dir}
data_root_ltf=${data_root_result}/ltf
data_root_rsd=${data_root_result}/rsd
output_ttl=${data_root_result}/kb/ttl
log_dir=${output_dir}/log


# #####################################################################
# # set up services, please reserve the the following ports and ensure that no other programs/services are occupying these ports:
# # `27017`, `2468`, `5500`, `5000`, `5234`, `9000`, `6001`, `6101` and `6201`.
# #####################################################################
# sh set_up_m36.sh ${kb_dir}

# ####################################################################
# # data prepreparation
# ####################################################################
# sh data_preparation_ldc.sh ${data_root} ${output_dir} ${output_dir} ${eval}


# ####################################################################
# # preprocessing, including language detection, ASR/OCR preprcessing
# ####################################################################
# docker run --rm -v ${data_root_rsd}:${data_root_rsd} -v ${data_root_ltf}:${data_root_ltf} -v ${data_root_result}:${data_root_result} -v ${parent_child_tab_path}:${parent_child_tab_path} -w `pwd` -i limanling/uiuc_ie_m36 \
#     /opt/conda/envs/py36/bin/python \
#     /preprocessing/preprocess_detect_languages.py ${data_root_rsd} ${data_root_ltf} ${data_root_result} \
#     --langs en ru es --parent_child_tab_path ${parent_child_tab_path}
# sh preprocess_asr_ocr.sh ${data_root_result} ${asr_en_path} ${ocr_en_path} ${ocr_ru_path} ${eval}

# wait

#####################################################################
# extraction, including entity, relation, event
#####################################################################
for lang in 'ru' 'en' 'es' 
do
    for datasource in '' '_asr' #'_ocr'
    do
        (
            data_root_lang=${data_root_result}/${lang}${datasource}
            if [ -d "${data_root_lang}/ltf" ]
            then
                sh preprocess.sh ${data_root_lang} ${lang} ${parent_child_tab_path} ${sorted} ${thread_num} ${eval}
            else
                echo "No" ${lang}${datasource} " documents in the corpus. Please double check. "
            fi
        )&
    done
done

wait

for lang in 'ru' 'en' 'es'
do
    for datasource in '' '_asr' #'_ocr'
    do
        (
            data_root_lang=${data_root_result}/${lang}${datasource}
            if [ -d "${data_root_lang}/ltf" ]
            then
                sh pipeline_sample_${lang}_m36_oneie.sh ${data_root_lang} ${parent_child_tab_path} ${sorted} ${lang} ${datasource}
            else
                echo "No" ${lang}${datasource} " documents in the corpus. Please double check. "
            fi
        )&
    done
done

wait

#####################################################################
# merging results
#####################################################################
docker run --rm -v ${data_root_result}:${data_root_result} -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /postprocessing/postprocessing_combine_turtle_from_all_sources.py \
    --root_folder ${data_root_result} \
    --final_dir_name 'final' \
    --output_folder ${output_ttl}
echo "Final output of English, Russian, Ukrainian in "${output_ttl}

docker run --rm -v ${data_root_result}:${data_root_result} -v ${parent_child_tab_path}:${parent_child_tab_path} -i limanling/uiuc_ie_m36 \
    /opt/conda/envs/py36/bin/python \
    /postprocessing/postprocessing_cleankb_params_caci.py \
    ${data_root_result}/cleankb.param ${output_ttl} ${final_ttl} ${variant} \
    --parent_child_tab_path ${parent_child_tab_path} \
    --eval m36
docker run --rm -v ${data_root_result}:${data_root_result} \
    -v ${parent_child_tab_path}:${parent_child_tab_path} \
    -w /aida-tools-java11 -i -t limanling/aida-tools \
    /aida-tools-java11/aida-eval-tools/target/appassembler/bin/cleanKB  \
    ${data_root_result}/cleankb.param


# #####################################################################
# # docker stop
# #####################################################################
# echo "Stop dockers..."
# docker stop db
# docker stop nominal_coreference
# docker stop aida_entity
# docker stop event_coreference_en
# docker stop event_coreference_ru
# docker stop event_coreference_uk
# docker ps

# exit 0