#!/usr/bin/env bash

if [ -d "${PWD}/system/aida_edl" ]
then
    echo "KB for linking is already in "${PWD}"/system/aida_edl"
else
    docker run --rm -v `pwd`:`pwd` -w `pwd` -i limanling/uiuc_ie_m18 mkdir -p ${PWD}/system/aida_edl
    docker run -v ${PWD}/system/aida_edl:/data panx27/data-processor wget http://159.89.180.81/demo/resources/edl_data.tar.gz -P /data
    docker run -v ${PWD}/system/aida_edl:/data panx27/data-processor tar zxvf /data/edl_data.tar.gz -C /data

fi
docker run --rm -v ${PWD}/system/aida_edl/edl_data/db:/data/db --name db mongo

docker run -d -i -t --rm -w /aida_nominal_coreference_en -p 2468:2468 --name nominal_coreference wangqy96/aida_nominal_coreference_en python nominal_backend.py

docker run -d -i -t --rm --name uiuc_ie_m18 -w /entity_api -p 5500:5500 --name aida_entity limanling/uiuc_ie_m18 \
    /opt/conda/envs/aida_entity/bin/python \
    /entity_api/entity_api/app.py

docker run -d -i -t --rm -w /event_coreference_xdoc -p 6001:6001 --name event_coreference_en dylandilu/event_coreference_xdoc python aida_event_coreference_backen_eng.py
docker run -d -i -t --rm -w /event_coreference_xdoc -p 6101:6101 --name event_coreference_ru dylandilu/event_coreference_xdoc python aida_event_coreference_backen_rus.py
docker run -d -i -t --rm -w /event_coreference_xdoc -p 6201:6201 --name event_coreference_uk dylandilu/event_coreference_xdoc python aida_event_coreference_backen_ukr.py
