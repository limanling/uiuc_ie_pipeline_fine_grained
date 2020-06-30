#!/usr/bin/env bash

#./pipeline_sample.sh data/testdata_all data/testdata_all/parent_children.sorted.tab data/asr.english data/video.ocr/en.cleaned.csv data/video.ocr/ru.cleaned.csv

######################################################
# Arguments
######################################################
# input root path
data_root=$1
parent_child_tab_path=$2
asr_en_path=$3
ocr_en_path=$4
ocr_ru_path=$5
sorted=1

# data folder that specified with language
data_root_ltf=${data_root}/ltf
data_root_rsd=${data_root}/rsd
data_root_result=${data_root}/result
output_folder=${data_root_result}/kb/ttl
log_dir=${data_root}/log

#####################################################################
# set up services, please reserve the the following ports and ensure that no other programs/services are occupying these ports:
# `27017`, `2468`, `5500`, `5000`, `5234`, `9000`, `6001`, `6101` and `6201`.
#####################################################################
sh set_up.sh > ${log_dir}/log_set_up.txt

#####################################################################
# preprocessing, including language detection, ASR/OCR preprcessing
#####################################################################
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /preprocessing/preprocess_detect_languages.py ${data_root_rsd} ${data_root_ltf} ${data_root_result}
sh preprocess_asr_ocr.sh ${data_root_result} ${asr_en_path} ${ocr_en_path} ${ocr_ru_path}


#####################################################################
# extraction, including entity, relation, event
#####################################################################
for lang in 'en' 'ru' 'uk'
do
    for datasource in '' #'_asr' '_ocr'
    do
        (
            data_root_lang=${data_root_result}/${lang}${datasource}
            if [ -d "${data_root_lang}/ltf" ]
            then
                sh preprocess.sh ${data_root_lang} ${lang} ${parent_child_tab_path} ${sorted} > ${log_dir}/log_preprocess_${lang}${source}.txt

                wait

                sh pipeline_sample_${lang}.sh ${data_root_lang} ${parent_child_tab_path} ${lang} ${datasource}
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
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /postprocessing/postprocessing_combine_turtle_from_all_sources.py \
    --root_folder ${data_root_result} \
    --final_dir_name 'final' \
    --output_folder ${output_folder}
echo "Final output of English, Russian, Ukrainian in "${output_folder}


#####################################################################
# docker stop
#####################################################################
#docker stop $(docker ps -q --filter ancestor=<image-name> )
#docker stop $(docker container ls -q --filter name=db*)
docker stop db
docker stop nominal_coreference
docker stop aida_entity
docker stop event_coreference_en
docker stop event_coreference_ru
docker stop event_coreference_uk


exit 0