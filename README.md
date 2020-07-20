# UIUC Information Extraction Pipeline
One single script to run text information extraction, including fine-grained entity extraction, relation extraction and event extraction.

Table of Contents
=================
  * [Overview](#overview)
  * [Requirements](#requirements)
  * [Quickstart](#quickstart)
  * [Sourcecode](#sourcecode)
  * [References](#references)
  
## Overview
<p align="center">
  <img src="overview_text.png" alt="Photo" style="width="100%;"/>
</p>

## Requirements
Docker (Please do not set up UIUC IE Pipeline in a NAS, as the EDL needs MongoDB, which may lead to permission issues in a NAS.)


## Quick Start

### Running LDC corpus, such as `LDC2019E42_AIDA_Phase_1_Evaluation_Source_Data_V1.0`.
```bash
sh pipeline_sample.sh ${data_root_ldc} ${output_dir} ${parent_child_tab} ${en_asr_path} ${en_ocr_path} ${ru_ocr_path}
```
where `parent_child_tab` is the file meta data in `docs` of LDC corpus. For example, 
```bash
sh pipeline_sample.sh ${PWD}/data/testdata_ldc ${PWD}/data/testdata_ldc/output ${PWD}/data/testdata_ldc/docs/parent_children.tab ${PWD}/data/asr.english ${PWD}/data/video.ocr/en.cleaned.csv ${PWD}/data/video.ocr/ru.cleaned.csv
```
If there is no ASR and OCR files, please use `None` as input, e.g.,
```bash
sh pipeline_sample.sh ${PWD}/data/testdata_ldc ${PWD}/data/testdata_ldc/output ${PWD}/data/testdata_ldc/docs/parent_children.tab None None None
```

To run OneIE version (RUN2), please run script
```bash
sh pipeline_sample_oneie.sh ${data_root_ldc} ${output_dir} ${parent_child_tab} ${en_asr_path} ${en_ocr_path} ${ru_ocr_path}
```


### Running on raw text data
* Make sure you have RSD (Raw Source Data, ending with `*.rsd.txt`) and LTF (Logical Text Format, ending with `*.ltf.xml`) files. 
	* If you have RSD files, please use the `aida_utilities/rsd2ltf.py` to generate the LTF files. 
	* If you have LTF files, please use the AIDA ltf2rsd tool (`LDC2018E62_AIDA_Month_9_Pilot_Eval_Corpus_V1.0/tools/ltf2txt/ltf2rsd.perl`) to generate the RSD files. 
* Optional files including the meta data and ASR/OCR results. If you do not have these files, please use `None`. 
    * `parent_child_tab` is a meta data file containing columns `child_uid` and `parent_uid` as file name, `content_date` as publication date, and example file is `testdata_dryrun/parent_children.sorted.tab`. It is used to normalize the time expression to 'YYYY-MM-DD'.
    * `en_asr_path`, `en_ocr_path` and `ru_ocr_path` are generated from ASR and OCR system using docker `gaiaaida/asr` from DockerHub. Example files are in `asr.english` and `data/video.ocr`. 
* Run the scripts. Note that the file paths are absolute paths.   
```bash
sh pipeline_sample_full.sh ${data_root_ltf} ${data_root_rsd} ${output_dir} ${parent_child_tab} ${en_asr_path} ${en_ocr_path} ${ru_ocr_path}
```
For example, 
```bash
sh pipeline_sample_full.sh ${PWD}/data/testdata_dryrun/ltf ${PWD}/data/testdata_dryrun/rsd ${PWD}/data/output ${PWD}/data/testdata_dryrun/parent_children.sorted.tab ${PWD}/data/asr.english ${PWD}/data/video.ocr/en.cleaned.csv ${PWD}/data/video.ocr/ru.cleaned.csv
```
If you do not have `parent_child_tab`, `en_asr_path`, `en_ocr_path` and `ru_ocr_path`, please use `None`.


For OneIE version, please use the script `pipeline_sample_oneie.sh` 
```bash
sh pipeline_sample_oneie.sh ${data_root_ltf} ${data_root_rsd} ${output_dir} ${parent_child_tab} ${en_asr_path} ${en_ocr_path} ${ru_ocr_path}
```
For example, 
```bash
sh pipeline_sample_oneie.sh ${PWD}/data/testdata_dryrun/ltf ${PWD}/data/testdata_dryrun/rsd ${PWD}/data/output_oneie ${PWD}/data/testdata_dryrun/parent_children.sorted.tab ${PWD}/data/asr.english ${PWD}/data/video.ocr/en.cleaned.csv ${PWD}/data/video.ocr/ru.cleaned.csv
```
Note that the file paths are absolute paths.

## Run on reduced version
Reduced Version disables the functions that will take long runningtime, including the functions of entity filler extraction (time, value, title, etc), part of fine-grained event extraction, etc.
```bash
sh pipeline_reduced.sh ${data_root_ltf} ${data_root_rsd} ${output_dir}
```

## Source Code

Please find source code in https://github.com/limanling/uiuc_ie_pipeline_finegrained_source_code.

## References
```
@inproceedings{li2020gaia,
  title={GAIA: A Fine-grained Multimedia Knowledge Extraction System},
  author={Li, Manling and Zareian, Alireza and Lin, Ying and Pan, Xiaoman and Whitehead, Spencer and Chen, Brian and Wu, Bo and Ji, Heng and Chang, Shih-Fu and Voss, Clare and others},
  booktitle={Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics: System Demonstrations},
  pages={77--86},
  year={2020}
}
```

