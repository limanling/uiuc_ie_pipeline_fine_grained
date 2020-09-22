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

### Running on raw text data
* Prepare a data directory `data` containing sub-directories `rsd` and `ltf`. The `rsd` sub-directory contains RSD (Raw Source Data, ending with `*.rsd.txt`), and `ltf` sub-directory has LTF (Logical Text Format, ending with `*.ltf.xml`) files. 
	* If you have RSD files, please use the [`aida_utilities/rsd2ltf.py`](https://github.com/limanling/uiuc_ie_pipeline_finegrained_source_code/blob/master/aida_utilities/rsd2ltf.py) to generate the LTF files. 
	* If you have LTF files, please use the AIDA ltf2rsd tool (`LDC2018E62_AIDA_Month_9_Pilot_Eval_Corpus_V1.0/tools/ltf2txt/ltf2rsd.perl`) to generate the RSD files. 
* Run the scripts. Note that the file paths are absolute paths.   
```bash
sh pipeline_full_en.sh ${data_root}
```
For example, 
```bash
sh pipeline_full_en.sh ${PWD}/data/testdata_dryrun
```


<!-- ### AIDA M18: Running LDC corpus, such as `LDC2019E42_AIDA_Phase_1_Evaluation_Source_Data_V1.0`.
```bash
sh pipeline_sample.sh ${data_root_ldc} ${output_dir} ${parent_child_tab} ${en_asr_path} ${en_ocr_path} ${ru_ocr_path} ${thread_num}
```
where `parent_child_tab` is the file meta data in `docs` of LDC corpus. For example, 
```bash
sh pipeline_sample.sh ${PWD}/data/testdata_ldc ${PWD}/output/output ${PWD}/data/testdata_ldc/docs/parent_children.tab ${PWD}/data/asr.english ${PWD}/data/video.ocr/en.cleaned.csv ${PWD}/data/video.ocr/ru.cleaned.csv 10
```
If there is no ASR and OCR files, please use `None` as input, e.g.,
```bash
sh pipeline_sample.sh ${PWD}/data/testdata_ldc ${PWD}/output/output ${PWD}/data/testdata_ldc/docs/parent_children.tab None None None 10
```

To run OneIE version (RUN2), please run script
```bash
sh pipeline_sample_oneie.sh ${data_root_ldc} ${output_dir} ${parent_child_tab} ${en_asr_path} ${en_ocr_path} ${ru_ocr_path} 10
```
For example,
```bash
sh pipeline_sample_oneie.sh ${PWD}/data/testdata_ldc ${PWD}/output/output_oneie ${PWD}/data/testdata_ldc/docs/parent_children.tab None None None 10
``` -->

### AIDA M36: Running LDC corpus and link entities to LDC released KB 
```bash
sh pipeline_sample_m36.sh ${data_root_ldc} ${kb_data_dir} ${output_dir} ${parent_child_tab} ${en_asr_path} ${en_ocr_path} ${ru_ocr_path} ${thread_num}
```
where `parent_child_tab` is the file meta data in `docs` of LDC corpus. `kb_data_dir` is the `data` directory of a LDC released KB, such as `${PWD}/data/LDC2020E27_AIDA_Phase_2_Practice_Topics_Reference_Knowledge_Base_V1.1/data`. For example, 
```bash
sh pipeline_sample_m36.sh ${PWD}/data/LDC2020E29 ${PWD}/data/LDC2020E27_AIDA_Phase_2_Practice_Topics_Reference_Knowledge_Base_V1.1/data ${PWD}/output/output_dryrun_E29_test ${PWD}/data/LDC2020E11_AIDA_Phase_2_Practice_Topic_Source_Data_V1.0/docs/parent_children.tab ${PWD}/output/output_dryrun_E11_asr_aln ${PWD}/data/video.ocr/en.cleaned.csv ${PWD}/data/video.ocr/ru.cleaned.csv 20
```
If there is no ASR and OCR files, please use `None` as input, e.g.,
```bash
sh pipeline_sample_m36.sh ${PWD}/data/LDC2020E29 ${PWD}/data/LDC2020E27_AIDA_Phase_2_Practice_Topics_Reference_Knowledge_Base_V1.1/data ${PWD}/output/output_dryrun_E29_test ${PWD}/data/LDC2020E11_AIDA_Phase_2_Practice_Topic_Source_Data_V1.0/docs/parent_children.tab None None None 20
```



## Run on reduced version
Reduced Version disables the functions that will take long runningtime, including the functions of entity filler extraction (time, value, title, etc), part of fine-grained event extraction, etc.
```bash
sh pipeline_reduced.sh ${data_root_ltf} ${data_root_rsd} ${output_dir}
```
For example,
```bash
sh pipeline_reduced.sh ${PWD}/data/testdata_dryrun/ltf ${PWD}/data/testdata_dryrun/rsd ${PWD}/output/output_reduced_dryrun
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

