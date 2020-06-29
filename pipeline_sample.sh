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

#####################################################################
# extraction, including entity, relation, event
#####################################################################
for lang in 'en' 'ru' 'uk'
do
    for datasource in '' '_asr' '_ocr'
    do
        (
            data_root_lang=${data_root_result}/${lang}${datasource}
            if [ -d "${data_root_lang}/ltf" ]
            then
                sh preprocess.sh ${data_root_lang} ${lang} ${parent_child_tab_path} ${sorted}
                sh pipeline_sample_${lang}.sh ${data_root_lang} ${parent_child_tab_path} ${lang} ${datasource}
            else
                echo "No" ${lang}${datasource} " documents in the corpus. Please double check. "
            fi
        )&
    done
done

#####################################################################
# merging results
#####################################################################
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /postprocessing/postprocessing_combine_turtle_from_all_sources.py \
#    parser.add_argument('--root_folder', type=str,
#                        help='root_folder')
#    parser.add_argument('--final_dir_name', type=str,
#                        help='final_dir_name')
#    parser.add_argument('--output_folder', type=str,
#                        help='output directory after merging')
