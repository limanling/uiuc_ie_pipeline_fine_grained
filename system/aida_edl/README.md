# RPI AIDA Pipeline
One single script to run AIDA pipeline. A demo is in [RPI AIDA Pipeline](https://blender04.cs.rpi.edu/~lim22/aida_api/extraction.html).

## Prerequisites
### Packages to install
1. Docker
2. Java
3. Python=2.7 with requests, jieba, nltk package installed (As most Linux distros deliver by default)

Please do not set up RPI AIDA Pipeline in a NAS, as the EDL needs MongoDB, which may lead to permission issues in a NAS.

### Download the latest docker images
Docker images will work as services (`mongo`, `panx27/edl`, `elisarpi/elisa-ie`， `limanling/aida_relation`, `zhangt13/aida_event`,  `dylandilu/event_coreference`, and `wangqy96/aida_nominal_coreference_en`) or runtime environments (`limanling/aida_converter`).
```bash
docker pull mongo
docker pull panx27/edl
docker pull elisarpi/elisa-ie
docker pull limanling/aida_converter
```

### Download the latest models
Please download the models for EDL, relation extraction and event extraction.
For entity discovery and linking model:
```bash
cd ./aida_edl
wget https://blender04.cs.rpi.edu/~zhangt13/pipeline/aida_edl_models.tgz
tar -xvf aida_edl_models.tgz
cd ./models
wget https://blender04.cs.rpi.edu/~zhangb8/lorelei/pytorch_models/en-nom.tar.gz
wget https://blender04.cs.rpi.edu/~zhangb8/lorelei/pytorch_models/en-nom_weaveh.tar.gz
tar -zxvf en-nom.tar.gz
tar -zxvf en-nom_weaveh.tar.gz
```

## Deployment
Please ensure that you are under the root folder of this project, and after each of the following dockers (step 1~5) is started, please open a new terminal to continue with another docker (of course, under the same root folder).

Also please reserve the the following ports and ensure that no other programs/services are occupying these ports: `27017`, `2201`, `3300`, `5000`, `5234`, `9000`, `6000`, `6100` and `6200`.

Step 1. Start the EDL mongo database server

Please wait until you see "waiting for connections on port 27017" message appear on the screen.

```bash
docker run --rm -v ${PWD}/aida_edl/index/db:/data/db --name db mongo
```

Step 2. Start the EDL server
```bash
docker run --rm -p 2201:2201 --link db:mongo panx27/edl python ./edl/api/web.py 2201
```

Step 3. Start the name tagger
```bash
docker run --rm -p 3300:3300 --network="host" -v ${PWD}/aida_edl/models/:/usr/src/app/data/name_tagger/pytorch_models -ti elisarpi/elisa-ie /usr/src/app/lorelei_demo/run.py --preload --in_domain
```

## Run the codes
* Save your raw text as RSD format (Raw Source Data, ending with `*.rsd.txt`), and put them in a `rsd` directory under `data_root` directory. 
* Run the following script, where `data_root` contains a subfolder `rsd` with your input RSD files. 
```bash
sh entity.sh ${data_root}
```
