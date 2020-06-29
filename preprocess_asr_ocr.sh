#!/usr/bin/env bash

data_root=$1
en_asr_aln=$2
en_ocr_csv_file=$3
ru_ocr_csv_file=$4


######################################################
# Arguments
######################################################

#en_asr_aln=${data_root}/rawdata/asr.english.ldc2019e42
en_asr_rsd=${data_root}/source/en_asr_rsd
en_asr_rsd_file_list=${data_root}/source/en_asr_truecase_list
en_asr_ltf=${data_root}/source/en_asr
en_asr_mapping_file_path=${data_root}/source/en_asr_mapping

#en_ocr_csv_file=${data_root}/rawdata/ocr.keyframes.ldc2019e42/en.cleaned.csv
en_ocr_rsd=${data_root}/source/en_ocr_img_rsd
en_ocr_ltf=${data_root}/source/en_ocr_img

#ru_ocr_csv_file=${data_root}/rawdata/ocr.keyframes.ldc2019e42/ru.cleaned.csv
ru_ocr_rsd=${data_root}/source/ru_ocr_img_rsd
ru_ocr_ltf=${data_root}/source/ru_ocr_img

#en_ocr_csv_file_video=${data_root}/rawdata/ocr.videos.ldc2019e42/en.cleaned.csv
#en_ocr_rsd_video=${data_root}/source/en_ocr_video_rsd
#en_ocr_ltf_video=${data_root}/source/en_ocr_video
#
#ru_ocr_csv_file_video=${data_root}/rawdata/ocr.videos.ldc2019e42/ru.cleaned.csv
#ru_ocr_rsd_video=${data_root}/source/ru_ocr_video_rsd
#ru_ocr_ltf_video=${data_root}/source/ru_ocr_video


######################################################
# Running scripts
######################################################

# for asr
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /preprocessing/preprocess_asr.py ${en_asr_aln} ${en_asr_rsd} ${en_asr_rsd_file_list}
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    mkdir -p ${en_asr_ltf}
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    ./system/aida_utilities/rsd2ltf.py ${en_asr_rsd} ${en_asr_ltf} \
    --seg_option nltk+linebreak --tok_option space --extension .rsd.txt
# asr sentence mapping
python asr_sentence_mapping.py ${en_asr_ltf} ${en_asr_aln} ${en_asr_mapping_file_path}

# for english ocr
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /preprocessing/preprocess_ocr.py ${en_ocr_csv_file} ${en_ocr_rsd}
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    mkdir -p ${en_ocr_ltf}
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    ./system/aida_utilities/rsd2ltf.py ${en_ocr_rsd} ${en_ocr_ltf} \
    --seg_option nltk+linebreak --tok_option unitok --extension .rsd.txt
# for russian ocr
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    /preprocessing/preprocess_ocr.py ${ru_ocr_csv_file} ${ru_ocr_rsd}
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    mkdir -p ${ru_ocr_ltf}
docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 \
    /opt/conda/envs/py36/bin/python \
    ./system/aida_utilities/rsd2ltf.py ${ru_ocr_rsd} ${ru_ocr_ltf} \
    --seg_option nltk+linebreak --tok_option unitok --extension .rsd.txt

