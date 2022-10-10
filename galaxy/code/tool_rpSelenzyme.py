#!/usr/bin/env python3

import sys #exit using sys exit if any error is encountered
import os
import requests
import json
import logging
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
    parser.add_argument('-num_results', type=int, default=10)
    parser.add_argument('-taxonomy_format', type=str, default='str')
    parser.add_argument('-taxonomy_input', type=str, default='511145')
    parser.add_argument('-direction', type=int, default=0)
    parser.add_argument('-noMSA', type=bool, default=True)
    parser.add_argument('-fp', type=str, default='RDK')
    parser.add_argument('-rxntype', type=str, default='smarts')
    parser.add_argument('-min_aa_length', type=int, default=100)
    params = parser.parse_args()
    if params.min_aa_length<=0:
        logging.error('Cannot have protein size of less or equal to 0: '+str(params.min_aa_length))
        exit(1)
    tax_id = -1
    ##### taxonomy #######
    if params.taxonomy_format=='json':
        tax_id = None
        with open(params.taxonomy_input, 'r') as ti:
            tax_dict = json.load(ti)
            tax_id = int(tax_dict['taxonomy'][0])
    elif params.taxonomy_format=='string' or params.taxonomy_format=='str' or params.taxonomy_format=='int':
        tax_id = int(params.taxonomy_input)
    else:
        logging.error('Taxonomy Input format not recognised')
        exit(1)
    ####### MSA #########
    noMSA = True
    if params.noMSA=='True' or params.noMSA=='true' or params.noMSA=='T' or params.noMSA==True:
        noMSA = True
    elif params.noMSA=='False' or params.noMSA=='false' or params.noMSA=='F' or params.noMSA==False:
        noMSA = False
    else:
        logging.error('The MSA input cannot be recognised')
        exit(1)
    ####### input #######
    if params.input_format=='tar':
        rpToolServe.runSelenzyme_hdd(params.input,
                                     params.output,
                                     params.pathway_id,
                                     tax_id,
                                     params.num_results,
                                     params.direction,
                                     noMSA,
                                     params.fp,
                                     params.rxntype,
                                     params.min_aa_length)
    elif params.input_format=='sbml':
        #make the tar.xz 
        with tempfile.TemporaryDirectory() as tmpOutputFolder:
            input_tar = tmpOutputFolder+'/tmp_input.tar'
            output_tar = tmpOutputFolder+'/tmp_output.tar'
            with tarfile.open(input_tar, mode='w:gz') as tf:
                info = tarfile.TarInfo('single.rpsbml.xml') #need to change the name since galaxy creates .dat files
                info.size = os.path.getsize(params.input)
                tf.addfile(tarinfo=info, fileobj=open(params.input, 'rb'))
            rpToolServe.runSelenzyme_hdd(input_tar,
                                         output_tar,
                                         params.pathway_id,
                                         tax_id,
                                         params.num_results,
                                         params.direction,
                                         noMSA,
                                         params.fp,
                                         params.rxntype,
                                         params.min_aa_length)
            with tarfile.open(output_tar) as outTar:
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(outTar, tmpOutputFolder)
            out_file = glob.glob(tmpOutputFolder+'/*.xml')
            if len(out_file)>1:
                logging.error('There are more than one output file...')
                exit(1)
            shutil.copy(out_file[0], params.output)
    else:
        logging.error('Cannot identify the input/output format: '+str(params.input_format))
        exit(1)
