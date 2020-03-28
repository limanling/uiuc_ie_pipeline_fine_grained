#!/bin/bash
langid="ru"
ltf_list_fname="/data/m1/whites5/AIDA/M18/eval/data/ru_all.ltf_files.lst"
ltf_dir="/data/m1/lim22/aida2019/LDC2019E42/source/ru_all"
edl_cs_fname="/data/m1/lim22/aida2019/LDC2019E42/0628/ru_all/edl/merged.cs"
edl_tab_fname="/nas/data/m1/lud2/AIDA/eval/y1/v1/entity_coreference/ru_all/ru.linking.corf.tab"
out_fname="/data/m1/whites5/AIDA/M18/eval/results/ru_all/ru_all.rel.final.cs"
cd ../
python -u exec_relation_extraction.py -i $langid -l $ltf_list_fname -f $ltf_dir -e $edl_cs_fname -t $edl_tab_fname -o $out_fname