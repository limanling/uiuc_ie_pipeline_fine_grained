#!/bin/bash

# https://github.com/NextCenturyCorporation/AIDA-Interchange-Format/blob/ef8beffc50d05466be730fd3c67330d6dfbdeaf3/python/tests/py_validator.sh

# if a command returns a non zero return value, exit script
set -e

# run examples.py
# DIR_PATH is the directory where example files are to be written
DIR_PATH=$1

# # get current time
# test_directory=${DIR_PATH}_`date +%s`
# mkdir $test_directory

# validate test file directory
# if any files are invalid, the script will end (see above)
docker run --rm -it \
       -v ${DIR_PATH}:/v \
       --entrypoint /opt/aif-validator/java/target/appassembler/bin/validateAIF \
       nextcenturycorp/aif_validator:latest \
       -o --ont /opt/aif-validator/java/src/main/resources/com/ncc/aif/ontologies/LDCOntologyM36 --nist -d /v

# # if all files are valid, delete the test file directory
# rm -r $test_directory