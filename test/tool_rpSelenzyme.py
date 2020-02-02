#!/usr/bin/env python3

import argparse
import sys #exit using sys exit if any error is encountered
import os
import requests
import json
import tempfile
import glob
import shutil

from io import BytesIO
import tarfile

import libsbml


## given a reaction SMILES query Selenzyme for the Uniprot ID's and its associated score
#
#
#def selenzymeREST(reaction_smile, url='http://selenzyme.synbiochem.co.uk/REST'):
def selenzymeREST(reaction_smile, url):
    #columns = ['smarts', 'Seq. ID', 'Score', 'Organism Source', 'Description']
    r = requests.post( os.path.join(url, 'Query') , json={'smarts': reaction_smile} )
    res = json.loads( r.content.decode('utf-8') )
    uniprotID_score = {}
    if res['data'] is not None:
        val = json.loads( res['data'] )
    else:
        raise ValueError
    if 'Seq. ID' in val and len(val['Seq. ID'])>0:
        for ix in sorted(val['Seq. ID'], key=lambda z: int(z)):
            uniprotID_score[val['Seq. ID'][ix]] = val['Score'][ix]
    else:
        raise ValueError
    return uniprotID_score



## Extract the reaction SMILES from an SBML, query selenzyme and write the results back to the SBML
#
#
def parseReactionSBML(model, url, pathId='rp_pathway'):
    groups = model.getPlugin('groups')
    rp_pathway = groups.getGroup(pathId)
    for member in rp_pathway.getListOfMembers():
        reaction = model.getReaction(member.getIdRef())
        annot = reaction.getAnnotation()
        bag_brsynth = annot.getChild('RDF').getChild('BRSynth').getChild('brsynth')
        bag_miriam = annot.getChild('RDF').getChild('Description').getChild('is').getChild('Bag')
        sel = bag_brsynth.getChild('selenzyme')
        if sel.toXMLString()=='':
            annot_string = '''
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bqbiol="http://biomodels.net/biology-qualifiers/">
  <rdf:BRSynth rdf:about="toadd">
    <brsynth:brsynth xmlns:brsynth="http://brsynth.eu">
      <brsynth:selenzyme>
      </brsynth:selenzyme>
    </brsynth:brsynth>
  </rdf:BRSynth>
</rdf:RDF>'''
            tmp_annot = libsbml.XMLNode.convertStringToXMLNode(annot_string)
            bag_brsynth.addChild(tmp_annot.getChild('BRSynth').getChild('brsynth').getChild('selenzyme'))
            sel = bag_brsynth.getChild('selenzyme')
        react_smiles = bag_brsynth.getChild('smiles').getChild(0).toString()
        try:
            uniprotID_score = selenzymeREST(react_smiles.replace('&gt;', '>'), url)
        except ValueError:
            continue
        for uniprot in uniprotID_score:
            ##### IBIBSA ###
            annot_string = '''
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bqbiol="http://biomodels.net/biology-qualifiers/">
  <rdf:BRSynth rdf:about="toadd">
    <brsynth:brsynth xmlns:brsynth="http://brsynth.eu">
      <brsynth:selenzyme>
        <brsynth:'''+str(uniprot)+''' value="'''+str(uniprotID_score[uniprot])+'''" />
      </brsynth:selenzyme>
    </brsynth:brsynth>
  </rdf:BRSynth>
</rdf:RDF>'''
            tmp_annot = libsbml.XMLNode.convertStringToXMLNode(annot_string)
            sel.addChild(tmp_annot.getChild('BRSynth').getChild('brsynth').getChild('selenzyme').getChild(uniprot))
            ''' to loop through all of them use this
            for i in range(sel.getNumChildren()):
                print(sel.getChild(i).toXMLString())
            '''
            ##### MIRIAM ###
            # NO idea why I have to create such a large tmp annotation to add to a current one
            annot_string = '''
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bqbiol="http://biomodels.net/biology-qualifiers/">
  <rdf:Description rdf:about="TOADD">
  <bqbiol:is>
  <rdf:Bag>
   <rdf:li rdf:resource="https://identifiers.org/uniprot/'''+str(uniprot)+'''" />
  </rdf:Bag>
  </bqbiol:is>
  </rdf:Description>
</rdf:RDF>'''
            q = libsbml.XMLNode.convertStringToXMLNode(annot_string)
            bag_miriam.addChild(q.getChild('Description').getChild('is').getChild('Bag').getChild('li'))


##
#
#
def processRun(inputTar, outTar, url, pathId):
    #loop through all of them and run FBA on them
    with tarfile.open(outTar, 'w:xz') as tf:
        with tarfile.open(inputTar, 'r:xz') as in_tf:
            for member in in_tf.getmembers():
                if not member.name=='':
                    sbml = libsbml.readSBMLFromString(in_tf.extractfile(member).read().decode("utf-8"))
                    parseReactionSBML(sbml.model, url, pathId)
                    data = libsbml.writeSBMLToString(sbml).encode('utf-8')
                    fiOut = BytesIO(data)
                    info = tarfile.TarInfo(member.name)
                    info.size = len(data)
                    tf.addfile(tarinfo=info, fileobj=fiOut)


#TODO: write the _hdd version of the process

##
#
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser('Given an SBML, extract the reaction rules and pass them to Selenzyme REST service and write the results to the SBML')
    parser.add_argument('-input', type=str)
    parser.add_argument('-output', type=str)
    parser.add_argument('-input_format', type=str)
    parser.add_argument('-url', type=str)
    parser.add_argument('-pathId', type=str)
    params = parser.parse_args()
    if params.input_format=='tar':
        processRun(params.input, params.output, params.url, params.pathId)
    elif params.input_format=='sbml':
        #make the tar.xz 
        with tempfile.TemporaryDirectory() as tmpOutputFolder:
            inputTar = tmpOutputFolder+'/tmp_input.tar.xz'
            outputTar = tmpOutputFolder+'/tmp_output.tar.xz'
            with tarfile.open(inputTar, mode='w:xz') as tf:
                info = tarfile.TarInfo('single.rpsbml.xml') #need to change the name since galaxy creates .dat files
                info.size = os.path.getsize(params.input)
                tf.addfile(tarinfo=info, fileobj=open(params.input, 'rb'))
            processRun(inputTar, outputTar, params.url, params.pathId)
            with tarfile.open(outputTar) as outTar:
                outTar.extractall(tmpOutputFolder)
            out_file = glob.glob(tmpOutputFolder+'/*.rpsbml.xml')
            if len(out_file)>1:
                logging.warning('There are more than one output file...')
            shutil.copy(out_file[0], params.output)
    else:
        logging.error('Cannot identify the input/output format: '+str(params.input_format))
