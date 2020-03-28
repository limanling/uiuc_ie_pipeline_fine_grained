#!/bin/bash
langid="uk"
ltf_list_fname="/data/m1/whites5/AIDA/M18/eval/data/uk.ltf_files.lst"
ltf_dir="/data/m1/lim22/aida2019/LDC2019E42/source/uk"
edl_cs_fname="/data/m1/lim22/aida2019/LDC2019E42/0628/uk/edl/merged.cs"
edl_tab_fname="/nas/data/m1/lud2/AIDA/eval/y1/v1/entity_coreference/uk/uk.linking.corf.tab"
out_fname="/data/m1/whites5/AIDA/M18/eval/results/uk/uk.rel.final.cs"
cd ../
python -u exec_relation_extraction.py -i $langid -l $ltf_list_fname -f $ltf_dir -e $edl_cs_fname -t $edl_tab_fname -o $out_fname