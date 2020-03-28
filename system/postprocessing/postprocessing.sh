#!/usr/bin/env bash

docker run --rm -v `pwd`:`pwd` -w `pwd` -i -t limanling/aida_tools \
    /aida-tools-master/aida-eval-tools/target/appassembler/bin/coldstart2AidaInterchange  \
    ${lang} ${ltf_source} ${edl_json_fine} ${edl_tab_freebase} \
    ${edl_cs_coarse} ${event_coarse_with_time} ${event_fine} \
    --filler_coarse ${filler_coarse} \
    --entity_finegrain_aida ${edl_cs_fine_all}