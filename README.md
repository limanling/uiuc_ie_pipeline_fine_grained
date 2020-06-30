# UIUC Information Extraction Pipeline
One single script to run text information extraction, including fine-grained entity extraction, relation extraction and event extraction.

## Prerequisites
### Packages to install
Docker (Please do not set up UIUC IE Pipeline in a NAS, as the EDL needs MongoDB, which may lead to permission issues in a NAS.)


## Run the codes
* Make sure you have RSD (Raw Source Data, ending with `*.rsd.txt`) and LTF (Logical Text Format, ending with `*.ltf.xml`) files. 
	* If you have RSD files, please use the `aida_utilities/rsd2ltf.py` to generate the LTF files. 
	* If you have LTF files, please use the AIDA ltf2rsd tool (`LDC2018E62_AIDA_Month_9_Pilot_Eval_Corpus_V1.0/tools/ltf2txt/ltf2rsd.perl`) to generate the RSD files. 
* Edit the `pipeline_sample.sh` for your run, including `data_root` containing a subfolder `ltf` with your input LTF files and a subfolder `rsd` with your input RSD files. Then run the shell file, 
```bash
sh pipeline_sample.sh ${data_root} ${parent_child_tab} ${en_asr_path} ${en_ocr_path} ${ru_ocr_path}
```
For example, 
```bash
sh pipeline_sample.sh data/testdata_all data/testdata_all/parent_children.sorted.tab data/asr.english data/video.ocr/en.cleaned.csv data/video.ocr/ru.cleaned.csv
```

For OneIE version, please use the script `pipeline_sample_oneie.sh` 
```bash
sh pipeline_sample_oneie.sh ${data_root} ${parent_child_tab} ${en_asr_path} ${en_ocr_path} ${ru_ocr_path}
```
For example, 
```bash
sh pipeline_sample_oneie.sh data/testdata_all data/testdata_all/parent_children.sorted.tab data/asr.english data/video.ocr/en.cleaned.csv data/video.ocr/ru.cleaned.csv
```
