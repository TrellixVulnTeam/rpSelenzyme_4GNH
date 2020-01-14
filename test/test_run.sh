#!/bin/sh

rm -f test_output.tar
docker run -d -p 5000:5000 --name test_rpSelenzyme -e LD_LIBRARY_PATH='/opt/conda/bin/../lib' brsynth/selenzyme
sleep 30
python tool_rpSelenzyme.py -inputTar test_input.tar -outputTar test_output.tar -pathway_id rp_pathway -server_url http://0.0.0.0:5000/REST
docker kill test_rpSelenzyme
docker rm test_rpSelenzyme
