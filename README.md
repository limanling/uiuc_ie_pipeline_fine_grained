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
* Make sure you have RSD (Raw Source Data, ending with `*.rsd.txt`) and LTF (Logical Text Format, ending with `*.ltf.xml`) files. 
	* If you have RSD files, please use the `aida_utilities/rsd2ltf.py` to generate the LTF files. 
	* If you have LTF files, please use the AIDA ltf2rsd tool (`LDC2018E62_AIDA_Month_9_Pilot_Eval_Corpus_V1.0/tools/ltf2txt/ltf2rsd.perl`) to generate the RSD files. 
* Edit the `pipeline_sample.sh` for your run, including `data_root` containing a subfolder `ltf` with your input LTF files and a subfolder `rsd` with your input RSD files. Then run the shell file, 
```bash
sh pipeline_sample.sh ${data_root} ${output_dir} ${parent_child_tab} ${en_asr_path} ${en_ocr_path} ${ru_ocr_path}
```
For example, 
```bash
sh pipeline_sample.sh ${PWD}/data/testdata_all ${PWD}/data/output ${PWD}/data/testdata_all/parent_children.sorted.tab ${PWD}/data/asr.english ${PWD}/data/video.ocr/en.cleaned.csv ${PWD}/data/video.ocr/ru.cleaned.csv
```

For OneIE version, please use the script `pipeline_sample_oneie.sh` 
```bash
sh pipeline_sample_oneie.sh ${data_root} ${output_dir} ${parent_child_tab} ${en_asr_path} ${en_ocr_path} ${ru_ocr_path}
```
For example, 
```bash
sh pipeline_sample_oneie.sh ${PWD}/data/testdata_all ${PWD}/data/testdata_all/parent_children.sorted.tab ${PWD}/data/asr.english ${PWD}/data/video.ocr/en.cleaned.csv ${PWD}/data/video.ocr/ru.cleaned.csv
```
Note that the file paths are absolute paths.

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
