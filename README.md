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
Docker


## Quick Start

### Running on raw text data
* Prepare a data directory `data` containing sub-directories `rsd` and `ltf`. The `rsd` sub-directory contains RSD (Raw Source Data, ending with `*.rsd.txt`), and `ltf` sub-directory has LTF (Logical Text Format, ending with `*.ltf.xml`) files. 
	* If you have RSD files, please use the [`aida_utilities/rsd2ltf.py`](https://github.com/limanling/uiuc_ie_pipeline_finegrained_source_code/blob/master/aida_utilities/rsd2ltf.py) to generate the LTF files. 
  ```bash
  docker run --rm -v ${ltf_dir}:${ltf_dir} -v ${rsd_dir}:${rsd_dir} -i limanling/uiuc_ie_m36 /opt/conda/envs/py36/bin/python /aida_utilities/rsd2ltf.py --seg_option nltk+linebreak --tok_option nltk_wordpunct --extension .rsd.txt ${rsd_dir} ${ltf_dir}
  ```
	* If you have LTF files, please use the AIDA ltf2rsd tool (`LDC2018E62_AIDA_Month_9_Pilot_Eval_Corpus_V1.0/tools/ltf2txt/ltf2rsd.perl`) to generate the RSD files. 
* Start services
```bash
sh set_up_m36.sh
```
* Run the scripts. Note that the file paths are absolute paths.   
```bash
sh pipeline_full_en.sh ${data_root} ${GPU_id}
```
For example, 
```bash
sh pipeline_full_en.sh ${PWD}/data/testdata_dryrun 0
```
If there is no gpu, please only set the `data_root` parameter:
```bash
sh pipeline_full_en.sh ${data_root}
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

### Run on reduced version
Reduced Version disables the functions that will take long runningtime, including the functions of entity filler extraction (time, value, title, etc), part of fine-grained event extraction, etc.
```bash
sh pipeline_reduced.sh ${data_root_ltf} ${data_root_rsd} ${output_dir}
```
For example,
```bash
sh pipeline_reduced.sh ${PWD}/data/testdata_dryrun/ltf ${PWD}/data/testdata_dryrun/rsd ${PWD}/output/output_reduced_dryrun
```

### Run on multimedia data

#### Step 1. Data preparation
Please prepare the input data file structure:
```
- CU_toolbox
- data 
  |------rsd
  |------ltf
  |------vision
  |------------data/jpg/jpg
  |------------data/video_shot_boundaries/representative_frames
  |------------docs/video_data.msb
  |------------docs/masterShotBoundary.msb
  |------------docs/parent_children.tab
  |------cu_objdet_results
  |------cu_grounding_results
  |------cu_grounding_matching_features
  |------cu_grounding_dict_files
```
where `docs/video_data.msb` and `docs/masterShotBoundary.msb` are empty files and `data/video_shot_boundaries/representative_frames` is an empty directory. `docs/parent_children.tab` contains meta data of images and text documents in the format of `catalog_id	version	parent_uid	child_uid	url	child_asset_type	topic	lang_id	lang_manual	rel_pos	wrapped_md5	unwrapped_md5	download_date	content_date	status_in_corpus`, separated by `TAB`. If one image (e.g., `image_1.jpg`) and one text document (e.g., `text_1.ltf.xml`) belongs to the same news article (e.g., `doc_1`), then it should be formatted as:
```
gaia v1 doc_1 image_1 0 .jpg 0 0 0 0 0 0 0 0 0
gaia v1 doc_1 text_1 0 .ltf.xml 0 0 0 0 0 0 0 0 0
```
Please avoid `.` in the file names and use `JPG` as image suffix. 

The sample code of preparation is in `uiuc_ie_pipeline_fine_grained/multimedia/sample_data_preparation.py`. 

Please find the sample data and result in [sample_data](https://uofi.box.com/s/fuqkq9zv5iwmtfemw94eec5yv9cbtxiy). The `CU_toolbox` can be downloaded in [CU_toolbox](https://uofi.box.com/s/v9508jvjbl170pu67rej8f8oiwyv20mq). 

#### Step 2. Object detection and cross-media coreference
Please run `uiuc_ie_pipeline_fine_grained/multimedia/multimedia.sh` to extract objects from images, and perform cross-media coreference.
The object results are saved in `cu_objdet_results/aida_output_34.pkl`(pickle format), and grounding results are saved in `cu_grounding_results`(pickle format) and `cu_graph_merging_ttl` (RDF format). Please find the grounding result visualization code in `uiuc_ie_pipeline_fine_grained/multimedia/visualize_ttl_grounding.py` using the RDF format output. 


## Source Code

Please find source code in https://github.com/limanling/uiuc_ie_pipeline_finegrained_source_code.


## License

GAIA system is licensed under the [GNU General Public License v3](https://www.gnu.org/licenses/gpl-3.0.en.html) or later.

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

