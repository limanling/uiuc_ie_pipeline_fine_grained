# UIUC Information Extraction Pipeline
One single script to run text information extraction, including fine-grained entity extraction, relation extraction and event extraction.

## Prerequisites
### Packages to install
Docker (Please do not set up UIUC IE Pipeline in a NAS, as the EDL needs MongoDB, which may lead to permission issues in a NAS.)

### Download the latest docker images
Docker images will work as services (`mongo`, `panx27/edl`, `limanling/uiuc_ie_m18`， `charlesztt/aida_event`,  `dylandilu/event_coreference_xdoc`, and `wangqy96/aida_nominal_coreference_en`).
```bash
docker pull mongo
docker pull panx27/edl
docker pull limanling/uiuc_ie_m18
docker pull charlesztt/aida_event
docker pull dylandilu/event_coreference_xdoc
docker pull wangqy96/aida_nominal_coreference_en
docker pull panx27/data-processor
docker pull limanling/aida-tools
docker pull graham3333/corenlp-complete
```

## Deployment
Please ensure that you are under the root folder of this project, and after each of the following dockers (step 1~5) is started, please open a new terminal to continue with another docker (of course, under the same root folder).

Also please reserve the the following ports and ensure that no other programs/services are occupying these ports: `27017`, `2468`, `5500`, `5000`, `5234`, `9000`, `6001`, `6101` and `6201`.

Step 1. Start the EDL mongo database server

Please wait until you see "waiting for connections on port 27017" message appear on the screen.

```bash
docker run -v ${PWD}/system/aida_edl:/data panx27/data-processor wget http://159.89.180.81/demo/resources/edl_data.tar.gz -P /data
docker run -v ${PWD}/system/aida_edl:/data panx27/data-processor tar zxvf /data/edl_data.tar.gz -C /data
docker run --rm -v ${PWD}/system/aida_edl/edl_data/db:/data/db --name db mongo
```

Step 2. Start the nominal coreference server
```bash
docker run -i -t --rm -w /aida_nominal_coreference_en -p 2468:2468 --name nominal_coreference wangqy96/aida_nominal_coreference_en python nominal_backend.py
```

Step 3. Start the name tagger
```bash
docker run -i -t --rm --name uiuc_ie_m18 -w /entity_api -p 5500:5500 --name aida_entity limanling/uiuc_ie_m18 \
    /opt/conda/envs/aida_entity/bin/python \
    /entity_api/entity_api/app.py
```

Step 4. Start the event extractor

This step will take a few minutes, you can proceed after you see "Serving Flask app ..." message.
```bash
docker run -v ${PWD}/system/aida_event:/tmp_event panx27/data-processor wget http://159.89.180.81/demo/resources/aida_event_data.tgz -P /tmp_event
docker run -v ${PWD}/system/aida_event:/tmp_event panx27/data-processor tar zxvf /tmp_event/aida_event_data.tgz -C /tmp_event
docker run -i -t --rm -v ${PWD}/system/aida_event/aida_event_data:/tmp -w /aida_event -p 5234:5234 --name aida_event charlesztt/aida_event python gail_event.py
```

Step 5. Start the event coreference solution

This step will take a few minutes, you can proceed after you see "Serving Flask app "aida_event_coreference_backen_{eng, rus, ukr}"" message. Notice that the port 6001, 6101 and 6201 are for English, Russian and Ukrainian respectively.
```bash
docker run -i -t --rm -w /event_coreference_xdoc -p 6001:6001 --name event_coreference dylandilu/event_coreference_xdoc python aida_event_coreference_backen_eng.py
```


## Run the codes
* Make sure you have RSD (Raw Source Data, ending with `*.rsd.txt`) and LTF (Logical Text Format, ending with `*.ltf.xml`) files. 
	* If you have RSD files, please use the `aida_utilities/rsd2ltf.py` to generate the LTF files. 
	* If you have LTF files, please use the AIDA ltf2rsd tool (`LDC2018E62_AIDA_Month_9_Pilot_Eval_Corpus_V1.0/tools/ltf2txt/ltf2rsd.perl`) to generate the RSD files. 
* Edit the `pipeline_sample.sh` for your run, including `data_root` containing a subfolder `ltf` with your input LTF files and a subfolder `rsd` with your input RSD files. Then run the shell file, 
```bash
sh pipeline_sample.sh ${data_root}
```
For example, 
```bash
sh pipeline_sample.sh data/testdata_all
```
<!--
For each raw document `doc_id.ltf.xml` and `doc_id.rsd.txt`, there will be a RDF format KB `doc_id.ttl` generated. If the final *.ttl files needs to be renamed, please provide the mapping file between the raw_id and rename_id as a second parameter, and the raw_id_column as the third parameter, rename_id_column as the fourth parameter. For example, in AIDA project, each file can be mapped a parent file. The final *.ttl files should be renamed to parent_file_id, whereas the raw document is named by child_file_id. 
```bash
sh pipeline_sample.sh ${data_root} ${parent_child_mapping_tab} ${child_column} ${parent_column}
```
-->
