#!/usr/bin/env python3
"""
Created on September 21 2019

@author: Melchior du Lac
@description: rpSelenzyme REST entry script

"""

import os
import json
import libsbml
import io
import tarfile
import csv
import sys
import glob
import tempfile
import logging

sys.path.insert(0, '/home/')
import rpSBML
import rpTool


def runSelenzyme_mem(inputTar,
                     outputTar,
                     pathway_id='rp_pathway',
                     host_taxonomy_id=83333,
                     num_results=50,
                     direction=0,
                     noMSA=True,
                     fp='RDK',
                     rxntype='smarts',
                     min_aa_length=100):
    """Run rpSelenzyme on a collection of rpSBML files in the form of a TAR file without writing to disk

    :param inputTar: The path to the input collection of rpSBML as a TAR file
    :param outputTar: The output file path
    :param pathway_id: Group id of the heterologous pathway (Default: rp_pathway)
    :param host_taxonomy_id: The taxonomy id of the host (Default: 83333, ie. E.Coli)
    :param num_results: Number of UNIPROT id's to return per reaction rule (Default: 50)
    :param direction: Forward (1) to reverse (0) direction (Default: 0)
    :param noMSA: Perform sequence alignement or not (Default: True)
    :param fp: Fingerprint for reactants for quickRSiml (Default: RDK)
    :param rxntype: The type of reaction rule. Valid options: smarts, smiles. (Default: smarts)
    :param min_aa_length: Filter the UNIRPOT proteins and return only whose amino acid lengths are greater than the input value. (Default: 100)

    :type inputTar: str
    :type outputTar: str
    :type reaction_smile: str
    :type host_taxonomy_id: int
    :type num_results: int
    :type direction: int
    :type noMSA: bool
    :type fp: str
    :type rxntype: str 
    :type min_aa_length: int

    :rtype: bool
    :return: The success or failure of the function
    """
    #loop through all of them and run FBA on them
    with tarfile.open(fileobj=outputTar, mode='w:gz') as tf:
        with tarfile.open(fileobj=inputTar, mode='r') as in_tf:
            for member in in_tf.getmembers():
                if not member.name=='':
                    rpsbml = rpSBML.rpSBML(member.name, libsbml.readSBMLFromString(in_tf.extractfile(member).read().decode("utf-8")))
                    if rpTool.singleSBML(rpsbml, host_taxonomy_id, pathway_id, num_results, direction, noMSA, fp, rxntype, min_aa_length):
                        sbml_bytes = libsbml.writeSBMLToString(rpsbml.document).encode('utf-8')
                        fiOut = io.BytesIO(sbml_bytes)
                        info = tarfile.TarInfo(fileName+'.rpsbml.xml')
                        info.size = len(sbml_bytes)
                        tf.addfile(tarinfo=info, fileobj=fiOut)


def runSelenzyme_hdd(inputTar,
                     outputTar,
                     pathway_id='rp_pathway',
                     host_taxonomy_id=83333,
                     num_results=50,
                     direction=0,
                     noMSA=True,
                     fp='RDK',
                     rxntype='smarts',
                     min_aa_length=100):
    """Run rpSelenzyme on a collection of rpSBML files in the form of a TAR file

    :param inputTar: The path to the input collection of rpSBML as a TAR file
    :param outputTar: The output file path
    :param pathway_id: Group id of the heterologous pathway (Default: rp_pathway)
    :param host_taxonomy_id: The taxonomy id of the host (Default: 83333, ie. E.Coli)
    :param num_results: Number of UNIPROT id's to return per reaction rule (Default: 50)
    :param direction: Forward (1) to reverse (0) direction (Default: 0)
    :param noMSA: Perform sequence alignement or not (Default: True)
    :param fp: Fingerprint for reactants for quickRSiml (Default: RDK)
    :param rxntype: The type of reaction rule. Valid options: smarts, smiles. (Default: smarts)
    :param min_aa_length: Filter the UNIRPOT proteins and return only whose amino acid lengths are greater than the input value. (Default: 100)

    :type inputTar: str
    :type outputTar: str
    :type reaction_smile: str
    :type host_taxonomy_id: int
    :type num_results: int
    :type direction: int
    :type noMSA: bool
    :type fp: str
    :type rxntype: str 
    :type min_aa_length: int

    :rtype: bool
    :return: The success or failure of the function
    """
    with tempfile.TemporaryDirectory() as tmpOutputFolder:
        with tempfile.TemporaryDirectory() as tmpInputFolder:
            tar = tarfile.open(inputTar, mode='r')
            tar.extractall(path=tmpInputFolder)
            tar.close()
            if len(glob.glob(tmpInputFolder+'/*'))==0:
                logging.error('Input file is empty')
                return False
            for sbml_path in glob.glob(tmpInputFolder+'/*'):
                fileName = sbml_path.split('/')[-1].replace('.sbml', '').replace('.xml', '').replace('.rpsbml', '')
                rpsbml = rpSBML.rpSBML(fileName)
                rpsbml.readSBML(sbml_path)
                if rpTool.singleSBML(rpsbml, host_taxonomy_id, pathway_id, num_results, direction, noMSA, fp, rxntype, min_aa_length):
                    rpsbml.writeSBML(tmpOutputFolder)
                rpsbml = None
            if len(glob.glob(tmpOutputFolder+'/*'))==0:
                logging.error('rpSelenzyme has not produced any results')
                return False
            with tarfile.open(outputTar, mode='w:gz') as ot:
                for sbml_path in glob.glob(tmpOutputFolder+'/*'):
                    fileName = str(sbml_path.split('/')[-1].replace('.sbml', '').replace('.xml', '').replace('.rpsbml', ''))+'.sbml.xml'
                    info = tarfile.TarInfo(fileName)
                    info.size = os.path.getsize(sbml_path)
                    ot.addfile(tarinfo=info, fileobj=open(sbml_path, 'rb'))
    return True
