#!/usr/bin/env bash

######################################################
# Arguments
######################################################
# input root path
data_root=$1
parent_child_tab_path=$2
sorted=1

# data folder that specified with language
data_root_ltf=${data_root}/ltf
data_root_rsd=${data_root}/rsd
data_root_result=${data_root}/result

#####################################################################
# preprocessing, including language detection, ASR/OCR preprcessing
#####################################################################
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /preprocessing/preprocess_detect_languages.py ${data_root_rsd} ${data_root_ltf} ${data_root_result}

for lang in 'en' #'ru' 'uk'
do
    for datasource in '' #'_asr' '_ocr'
    do
        (
            data_root_lang=${data_root_result}/${lang}${datasource}
            if [ -d "${data_root_lang}/ltf" ]
            then
                sh preprocess.sh ${data_root_lang} ${lang} ${parent_child_tab_path} ${sorted}
                sh pipeline_sample_${lang}_oneie.sh ${data_root_lang} ${lang} ${datasource}
            else
                echo "No" ${lang}${datasource} " documents in the corpus. Please double check. "
            fi
        )&
    done
done

