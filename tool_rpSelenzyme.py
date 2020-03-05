#!/usr/bin/env python3

import sys #exit using sys exit if any error is encountered
import os
import requests
import json
import tempfile
import glob
import shutil
import argparse

from io import BytesIO
import tarfile

sys.path.insert(0, '/home/')
import rpToolServe


##
#
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser('Given an SBML, extract the reaction rules and pass them to Selenzyme REST service and write the results to the SBML')
    parser.add_argument('-input', type=str)
    parser.add_argument('-output', type=str)
    parser.add_argument('-input_format', type=str)
    parser.add_argument('-pathway_id', type=str)
    parser.add_argument('-num_results', type=int)
    parser.add_argument('-taxonomy_format', type=str)
    parser.add_argument('-taxonomy_input', type=str)
    params = parser.parse_args()
    tax_id = -1
    ##### taxonomy #######
    if params.taxonomy_format=='json':
        tax_id = None
        with open(params.taxonomy_input, 'r') as ti:
            tax_dict = json.load(ti)
            tax_id = int(tax_dict['taxonomy'][0])
    elif params.taxonomy_format=='string':
        tax_id = int(params.taxonomy_input)
    else:
        logging.warning('Taxonomy Input format not recognised')
    ####### input #######
    if params.input_format=='tar':
		rpToolServe.runSelenzyme_hdd(params.input,
									 params.output,
									 params.pathway_id,
									 tax_id,
									 params.num_targets)
    elif params.input_format=='sbml':
        #make the tar.xz 
        with tempfile.TemporaryDirectory() as tmpOutputFolder:
            input_tar = tmpOutputFolder+'/tmp_input.tar.xz'
            output_tar = tmpOutputFolder+'/tmp_output.tar.xz'
            with tarfile.open(input_tar, mode='w:xz') as tf:
                info = tarfile.TarInfo('single.rpsbml.xml') #need to change the name since galaxy creates .dat files
                info.size = os.path.getsize(params.input)
                tf.addfile(tarinfo=info, fileobj=open(params.input, 'rb'))
			rpToolServe.runSelenzyme_hdd(input_tar,
										 output_tar,
										 params.pathway_id,
										 tax_id,
										 params.num_targets)
            with tarfile.open(output_tar) as outTar:
                outTar.extractall(tmpOutputFolder)
            out_file = glob.glob(tmpOutputFolder+'/*.rpsbml.xml')
            if len(out_file)>1:
                logging.warning('There are more than one output file...')
            shutil.copy(out_file[0], params.output)
    else:
        logging.error('Cannot identify the input/output format: '+str(params.input_format))
