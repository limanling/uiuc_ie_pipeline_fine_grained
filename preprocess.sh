#!/usr/bin/env bash

data_root_lang=$1
lang=$2
parent_child_tab_path=$3
sorted=$4

(
    sh preprocess_parser.sh ${data_root_lang} ${lang} ${parent_child_tab_path} ${sorted}
    sh preprocess_framenet.sh ${data_root_lang} ${lang}
)&