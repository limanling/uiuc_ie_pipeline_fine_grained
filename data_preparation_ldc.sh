####################################################################
# prepare ltf and rsd, and parent_child_tab
####################################################################
ldc_data=$1  #/shared/nas/data/m1/AIDA_Data/LDC_raw_data/LDC2019E42_AIDA_Phase_1_Evaluation_Source_Data_V1.0
ltf_dir=$2 #${ldc_data}/data/ltf/ltf
rsd_dir=$3 #${ldc_data}/data/rsd
eval=$4

# unzip ltf
docker run --rm -v ${ldc_data}:${ldc_data} -v ${ltf_dir}:${ltf_dir} -i limanling/uiuc_ie_${eval} \
    mkdir -p ${ltf_dir}
docker run --rm -v ${ldc_data}:${ldc_data} -v ${ltf_dir}:${ltf_dir} -i limanling/uiuc_ie_${eval} \
    unzip -o ${ldc_data}/data/ltf/\*.zip -d ${ltf_dir}
# generate rsd
docker run --rm -v ${ldc_data}:${ldc_data} -v ${ltf_dir}:${ltf_dir} -v ${rsd_dir}:${rsd_dir} -w `pwd` -i limanling/uiuc_ie_${eval} \
    perl ${ldc_data}/tools/ltf2txt/ltf2rsd.perl -o ${rsd_dir} ${ltf_dir}

echo "ltf file directory is "${ltf_dir}
echo "rsd file directory is "${rsd_dir}