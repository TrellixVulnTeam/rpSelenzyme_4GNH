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

sys.path.insert(0, '/home/')
import rpSBML
import rpTool


##
#
#
def runSelenzyme_mem(inputTar, 
                     outputTar, 
                     pathway_id='rp_pathway', 
                     host_taxonomy_id=83333, 
                     num_targets=50, 
                     direction=0, 
                     noMSA=True, 
                     fp='RDK', 
                     rxntype='smarts'):
    #loop through all of them and run FBA on them
    with tarfile.open(fileobj=outputTar, mode='w:xz') as tf:
        with tarfile.open(fileobj=inputTar, mode='r:xz') as in_tf:
            for member in in_tf.getmembers():
                if not member.name=='':
                    rpsbml = rpSBML.rpSBML(member.name, libsbml.readSBMLFromString(in_tf.extractfile(member).read().decode("utf-8")))
                    if rpTool.singleSBML(rpsbml, host_taxonomy_id, pathway_id, num_targets, direction, noMSA, fp, rxntype):
                        sbml_bytes = libsbml.writeSBMLToString(rpsbml.document).encode('utf-8')
                        fiOut = io.BytesIO(sbml_bytes)
                        info = tarfile.TarInfo(fileName+'.rpsbml.xml')
                        info.size = len(sbml_bytes)
                        tf.addfile(tarinfo=info, fileobj=fiOut)


## run using HDD 3X less than the above function
#
#
def runSelenzyme_hdd(inputTar, 
                     outputTar, 
                     pathway_id='rp_pathway', 
                     host_taxonomy_id=83333, 
                     num_targets=50, 
                     direction=0, 
                     noMSA=True, 
                     fp='RDK', 
                     rxntype='smarts'):
    with tempfile.TemporaryDirectory() as tmpOutputFolder:
        with tempfile.TemporaryDirectory() as tmpInputFolder:
            tar = tarfile.open(inputTar, mode='r:xz')
            tar.extractall(path=tmpInputFolder)
            tar.close()
            for sbml_path in glob.glob(tmpInputFolder+'/*'):
                fileName = sbml_path.split('/')[-1].replace('.sbml', '').replace('.xml', '').replace('.rpsbml', '')
                rpsbml = rpSBML.rpSBML(fileName)
                rpsbml.readSBML(sbml_path)
                if rpTool.singleSBML(rpsbml, host_taxonomy_id, pathway_id, num_targets, direction, noMSA, fp, rxntype):
                    rpsbml.writeSBML(tmpOutputFolder)
                rpsbml = None
            with tarfile.open(outputTar, mode='w:xz') as ot:
                for sbml_path in glob.glob(tmpOutputFolder+'/*'):
                    fileName = str(sbml_path.split('/')[-1].replace('.sbml', '').replace('.xml', '').replace('.rpsbml', ''))+'.rpsbml.xml'
                    info = tarfile.TarInfo(fileName)
                    info.size = os.path.getsize(sbml_path)
                    ot.addfile(tarinfo=info, fileobj=open(sbml_path, 'rb'))
