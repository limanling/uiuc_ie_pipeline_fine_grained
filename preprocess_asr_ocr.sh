#!/usr/bin/env bash

data_root=$1
en_asr_aln=$2
en_ocr_csv_file=$3
ru_ocr_csv_file=$4
eval=$5

######################################################
# Arguments
######################################################

#en_asr_aln=${data_root}/rawdata/asr.english.ldc2019e42
en_asr_rsd=${data_root}/en_asr/rsd
en_asr_rsd_file_list=${data_root}/en_asr/en_asr_truecase_list
en_asr_ltf=${data_root}/en_asr/ltf
en_asr_mapping_file_path=${data_root}/en_asr/en_asr_mapping

#en_ocr_csv_file=${data_root}/rawdata/ocr.keyframes.ldc2019e42/en.cleaned.csv
#en_ocr_csv_file_video=${data_root}/rawdata/ocr.videos.ldc2019e42/en.cleaned.csv
en_ocr_rsd=${data_root}/en_ocr/rsd
en_ocr_ltf=${data_root}/en_ocr/ltf

#ru_ocr_csv_file=${data_root}/rawdata/ocr.keyframes.ldc2019e42/ru.cleaned.csv
#ru_ocr_csv_file_video=${data_root}/rawdata/ocr.videos.ldc2019e42/ru.cleaned.csv
ru_ocr_rsd=${data_root}/ru_ocr/rsd
ru_ocr_ltf=${data_root}/ru_ocr/ltf


######################################################
# Running scripts
######################################################

if [ -d "${en_asr_aln}" ]
then
    # for asr
    docker run --rm -v ${data_root}:${data_root} \
        -v ${en_asr_aln}:${en_asr_aln} \
        -w `pwd` -i limanling/uiuc_ie_${eval} \
        /opt/conda/envs/py36/bin/python \
        /preprocessing/preprocess_asr.py ${en_asr_aln} ${en_asr_rsd} ${en_asr_rsd_file_list}
    docker run --rm -v ${data_root}:${data_root} \
        -w `pwd` -i limanling/uiuc_ie_${eval} \
        mkdir -p ${en_asr_ltf}
    docker run --rm -v ${data_root}:${data_root} \
        -w `pwd` -i limanling/uiuc_ie_${eval} \
        /opt/conda/envs/py36/bin/python \
        /aida_utilities/rsd2ltf.py ${en_asr_rsd} ${en_asr_ltf} \
        --seg_option nltk+linebreak --tok_option space --extension .rsd.txt
    # asr sentence mapping
    docker run --rm -v ${data_root}:${data_root} \
        -v ${en_asr_aln}:${en_asr_aln} \
        -w `pwd` -i limanling/uiuc_ie_${eval} \
        /opt/conda/envs/py36/bin/python \
        /preprocessing/asr_sentence_mapping.py ${en_asr_ltf} ${en_asr_aln} ${en_asr_mapping_file_path}
else
    echo "no ASR files"
fi

if [ -d "${en_ocr_csv_file}" ]
then
    # for english ocr
    docker run --rm -v ${data_root}:${data_root} \
        -v ${en_ocr_csv_file}:${en_ocr_csv_file} \
        -w `pwd` -i limanling/uiuc_ie_${eval} \
        /opt/conda/envs/py36/bin/python \
        /preprocessing/preprocess_ocr.py ${en_ocr_csv_file} ${en_ocr_rsd}
    docker run --rm -v ${data_root}:${data_root} \
        -w `pwd` -i limanling/uiuc_ie_${eval} \
        mkdir -p ${en_ocr_ltf}
    docker run --rm -v ${data_root}:${data_root} \
        -w `pwd` -i limanling/uiuc_ie_${eval} \
        /opt/conda/envs/py36/bin/python \
        /aida_utilities/rsd2ltf.py ${en_ocr_rsd} ${en_ocr_ltf} \
        --seg_option nltk+linebreak --tok_option unitok --extension .rsd.txt
else
    echo "no English OCR files"
fi

if [ -d "${ru_ocr_csv_file}" ]
then
    # for russian ocr
    docker run --rm -v ${data_root}:${data_root} \
        -v ${ru_ocr_csv_file}:${ru_ocr_csv_file} \
        -w `pwd` -i limanling/uiuc_ie_${eval} \
        /opt/conda/envs/py36/bin/python \
        /preprocessing/preprocess_ocr.py ${ru_ocr_csv_file} ${ru_ocr_rsd}
    docker run --rm -v ${data_root}:${data_root} \
        -w `pwd` -i limanling/uiuc_ie_${eval} \
        mkdir -p ${ru_ocr_ltf}
    docker run --rm -v ${data_root}:${data_root} \
        -w `pwd` -i limanling/uiuc_ie_${eval} \
        /opt/conda/envs/py36/bin/python \
        /aida_utilities/rsd2ltf.py ${ru_ocr_rsd} ${ru_ocr_ltf} \
        --seg_option nltk+linebreak --tok_option unitok --extension .rsd.txt
else
    echo "no Russian OCR files"
fi

