#!/usr/bin/env python3
"""
Created on September 21 2019

@author: Melchior du Lac
@description: rpSelenzyme REST entry script

"""

import logging
import tempfile
import json
import sys
import csv
sys.path.insert(0, '/home/selenzy/')
#sys.path.insert(0, '/home/mdulac/workspace/Galaxy-SynBioCAD/rpSelenzyme/selenzy/')
import Selenzy

## global parameter 
DATADIR = '/home/selenzy/data/'
#DATADIR = '/home/mdulac/workspace/Galaxy-SynBioCAD/rpSelenzyme/selenzy/data/'
pc = Selenzy.readData(DATADIR)


############## Cache ##############


uniprot_aaLenght = {}
with open(DATADIR+'sel_len.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    next(csv_reader)
    for row in csv_reader:
        uniprot_aaLenght[row[0].split('|')[1]] = int(row[1])


############## Tools ##############


def singleReactionRule(reaction_rule,
                       host_taxonomy_id,
                       num_results=50,
                       direction=0,
                       noMSA=True,
                       fp='RDK',
                       rxntype='smarts'):
    """Query Selenzyme given a single reaction rule

    :param reaction_rule: The reaction rule
    :param host_taxonomy_id: The taxonomy id associated with the reaction rule
    :param num_results: The number of uniprot ids to return (Default: 50)
    :param direction: Forward (1) to reverse (0) direction (Default: 0)
    :param noMSA: Perform sequence alignement or not (Default: True)
    :param fp: Fingerprint for reactants for quickRSiml (Default: RDK)
    :param rxntype: The type of reaction rule. Valid options: smarts, smiles. (Default: smarts)

    :type reaction_rule: str
    :type host_taxonomy_id: int
    :type num_results: int
    :type direction: int
    :type noMSA: bool
    :type fp: str
    :type rxntype: str 

    :rtype: dict
    :return: The UNIPROT id's and its associated score
    """
    uniprotID_score = {}
    score = Selenzy.seqScore()
    with tempfile.TemporaryDirectory() as tmpOutputFolder:
        success, results = Selenzy.analyse(['-'+rxntype, reaction_rule], num_results, DATADIR, tmpOutputFolder, 'tmp.csv', 0, host_taxonomy_id, pc=pc, NoMSA=noMSA)
        data = Selenzy.updateScore(tmpOutputFolder+'/tmp.csv', score)
        val = json.loads(data.to_json())
        if 'Seq. ID' in val and len(val['Seq. ID'])>0:
            for ix in sorted(val['Seq. ID'], key=lambda z: int(z)):
                uniprotID_score[val['Seq. ID'][ix]] = val['Score'][ix]
        else:
            raise ValueError
        return uniprotID_score


def singleSBML(rpsbml,
               host_taxonomy_id=83333,
               pathway_id='rp_pathway',
               num_results=50,
               direction=0,
               noMSA=True,
               fp='RDK',
               rxntype='smarts',
               min_aa_length=100):
    """Return UNIPROT id's associated with each reaction using Selenzyme, from a rpSBML object

    :param rpsbml: The input rppSBML object
    :param host_taxonomy_id: The taxonomy id of the host (Default: 83333, ie. E.Coli)
    :param pathway_id: Group id of the heterologous pathway (Default: rp_pathway)
    :param num_results: Number of UNIPROT id's to return per reaction rule (Default: 50)
    :param direction: Forward (1) to reverse (0) direction (Default: 0)
    :param noMSA: Perform sequence alignement or not (Default: True)
    :param fp: Fingerprint for reactants for quickRSiml (Default: RDK)
    :param rxntype: The type of reaction rule. Valid options: smarts, smiles. (Default: smarts)
    :param min_aa_length: Filter the UNIRPOT proteins and return only whose amino acid lengths are greater than the input value. (Default: 100)

    :type rpsbml: rpSBML object
    :type host_taxonomy_id: int
    :type pathway_id: str
    :type num_results: int
    :type direction: int
    :type noMSA: bool
    :type fp: str
    :type rxntype: str 
    :type min_aa_length: int

    :rtype: bool
    :return: The success or failure of the function
    """
    for reac_id in rpsbml.readRPpathwayIDs(pathway_id):
        reac = rpsbml.model.getReaction(reac_id)
        brs_reac = rpsbml.readBRSYNTHAnnotation(reac.getAnnotation())
        if brs_reac['smiles']:
            try:
                uniprotID_score = singleReactionRule(brs_reac['smiles'], host_taxonomy_id, num_results, direction, noMSA, fp, rxntype)
                uniprotID_score_restricted = {}
                for uniprot in uniprotID_score:
                    try:
                        if uniprot_aaLenght[uniprot]>int(min_aa_length):
                            uniprotID_score_restricted[uniprot] = uniprotID_score[uniprot]
                    except KeyError:
                        logging.warning('Cannot find the following UNIPROT '+str(uniprot)+' in uniprot_aaLenght')
                xref = {'uniprot': [i for i in uniprotID_score_restricted]}
                rpsbml.addUpdateMIRIAM(reac, 'reaction', xref)
                rpsbml.addUpdateBRSynth(reac, 'selenzyme', uniprotID_score_restricted, None, False, True, True)
            except ValueError:
                logging.warning('Problem with retreiving the selenzyme information for model '+str(rpsbml.model.getId()))
                return False
        else:
            logging.warning('Cannot retreive the reaction rule of model '+str(rpsbml.model.getId()))
            return False
    return True
