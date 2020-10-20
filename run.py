#!/usr/bin/env python3
"""
Created on September 21 2019

@author: Melchior du Lac
@description: Extract the sink from an SBML into RP2 friendly format

"""
import argparse
import tempfile
import os
import logging
import shutil
import docker


##
#
#
def main(inputfile,
         output,
         input_format,
         pathway_id,
         num_results,
         taxonomy_format,
         taxonomy_input,
         direction,
         noMSA,
         fp,
         rxntype,
         min_aa_length):
    """Run rpSelenzyme on a collection of rpSBML files in the form of a TAR file

    :param inputTar: The path to the input collection of rpSBML as a TAR file or single rpSBML file
    :param outputTar: The output file path
    :param input_format: The input file format. Valid options: sbml, tar
    :param pathway_id: Group id of the heterologous pathway (Default: rp_pathway)
    :param num_results: Number of UNIPROT id's to return per reaction rule (Default: 50)
    :param taxonomy_format: The input format of the taxonomy. Valid options: json, str
    :param taxonomy_input: The input of the taxonomy id of the host oeganism
    :param direction: Forward (1) to reverse (0) direction (Default: 0)
    :param noMSA: Perform sequence alignement or not (Default: True)
    :param fp: Fingerprint for reactants for quickRSiml (Default: RDK)
    :param rxntype: The type of reaction rule. Valid options: smarts, smiles. (Default: smarts)
    :param min_aa_length: Filter the UNIRPOT proteins and return only whose amino acid lengths are greater than the input value. (Default: 100)

    :type inputTar: str
    :type outputTar: str
    :type input_format: str
    :type pathway_id: str
    :type num_results: int
    :type taxonomy_format: str
    :type taxonomy_input: str
    :type direction: int
    :type noMSA: bool
    :type fp: str
    :type rxntype: str 
    :type min_aa_length: int

    :rtype: None
    :return: None
    """
    docker_client = docker.from_env()
    image_str = 'brsynth/rpselenzyme-standalone:v2'
    try:
        image = docker_client.images.get(image_str)
    except docker.errors.ImageNotFound:
        logging.warning('Could not find the image, trying to pull it')
        try:
            docker_client.images.pull(image_str)
            image = docker_client.images.get(image_str)
        except docker.errors.ImageNotFound:
            logging.error('Cannot pull image: '+str(image_str))
            exit(1)
    with tempfile.TemporaryDirectory() as tmpOutputFolder:
        if os.path.exists(inputfile):
            shutil.copy(inputfile, tmpOutputFolder+'/input.dat')
            command = ['/home/tool_rpSelenzyme.py',
                       '-input',
                       '/home/tmp_output/input.dat',
                       '-output',
                       '/home/tmp_output/output.dat',
                       '-input_format',
                       str(input_format),
                       '-pathway_id',
                       str(pathway_id),
                       '-num_results',
                       str(num_results),
                       '-taxonomy_format',
                       str(taxonomy_format),
                       '-taxonomy_input',
                       str(taxonomy_input),
                       '-direction',
                       str(direction),
                       '-noMSA',
                       str(noMSA),
                       '-fp',
                       str(fp),
                       '-rxntype',
                       str(rxntype),
                       '-min_aa_length',
                       str(min_aa_length)]
            container = docker_client.containers.run(image_str,
                                                     command,
                                                     detach=True,
                                                     stderr=True,
                                                     volumes={tmpOutputFolder+'/': {'bind': '/home/tmp_output', 'mode': 'rw'}})
            container.wait()
            err = container.logs(stdout=False, stderr=True)
            err_str = err.decode('utf-8')
            if 'ERROR' in err_str:
                print(err_str)
            elif 'WARNING' in err_str:
                print(err_str)
            if not os.path.exists(tmpOutputFolder+'/output.dat'):
                print('ERROR: Cannot find the output file: '+str(tmpOutputFolder+'/output.dat'))
            else:
                shutil.copy(tmpOutputFolder+'/output.dat', output)
            container.remove()
        else:
            logging.error('Cannot find the input file: '+str(inputfile))
            exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Given an SBML, extract the reaction rules and pass them to Selenzyme REST service and write the results to the SBML')
    parser.add_argument('-input', type=str)
    parser.add_argument('-output', type=str)
    parser.add_argument('-input_format', type=str)
    parser.add_argument('-pathway_id', type=str, default='rp_pathway')
    parser.add_argument('-num_results', type=int, default=10)
    parser.add_argument('-taxonomy_format', type=str)
    parser.add_argument('-taxonomy_input', type=int)
    parser.add_argument('-direction', type=int, default=0)
    parser.add_argument('-noMSA', type=bool, default=True)
    parser.add_argument('-fp', type=str, default='RDK')
    parser.add_argument('-rxntype', type=str, default='smarts')
    parser.add_argument('-min_aa_length', type=int, default=100)
    params = parser.parse_args()
    main(params.input,
         params.output,
         params.input_format,
         params.pathway_id,
         params.num_results,
         params.taxonomy_format,
         params.taxonomy_input,
         params.direction,
         params.noMSA,
         params.fp,
         params.rxntype,
         params.min_aa_length)
