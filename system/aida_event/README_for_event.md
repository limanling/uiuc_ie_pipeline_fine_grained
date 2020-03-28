# RPI Event Extraction

## Prerequisites
### Packages to install
1. Docker
2. Python=2.7 with requests, jieba, nltk package installed (As most Linux distros deliver by default)

### Download the latest docker images
Docker images will work as services (`zhangt13/aida_event`).
```bash
docker pull zhangt13/aida_event
```

## Deployment
After the following docker is started, please open a new terminal to continue.

Also please reserve the the following ports and ensure that no other programs/services are occupying port `5234`.

### Start the event extractor service

This step will take a few minutes, you can proceed after you see "Serving Flask app ..." message.
```bash
docker run -i -t --rm -w /aida_event -p 5234:5234 zhangt13/aida_event python gail_event.py
```

## Usage 

### Runing on your documents
Please ensure that you are under the root folder of this project (`aida_pipeline`).

#### Step 1, prepare the raw files under `data_root/rsd`
Please prepare raw documents under `data_root/rsd`, and the name of each file should be in the form of `xxxx.rsd.txt`).

#### Step 2, prepare the tokenized file under `data_root/ltf`
```bash
python aida_utilities/rsd2ltf.py ${data_root}/rsd ${data_root}/ltf
```

### Step 3. Specify the `data_root` in `event_sample.sh`, and run the script.
```bash
sh event_sample.sh
```

## API Usage
We provide a REST API to extract events. Please post to `http://127.0.0.1:5234/aida_event_en_imitation` with a json with following contents:
* File content of EDL Cold Start file (with 'edl_cs' key)
* File content of EDL tab file (with 'edl_tab' key)
* File content of filler cs file (with 'filler_cs' key)
* Contents of ltf xml files (key format: 'input' -> <file_id> -> 'ltf') (<file_id> is the ltf file name, in the format of `xxxx.ltf.xml`).

The output (response) will be file content of event output with cs format, simply write it with `open().write()`.

Please find the example of calling API in `gail_event_test.py`.