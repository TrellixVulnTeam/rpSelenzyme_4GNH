#!/usr/bin/env python3
"""
Created on September 21 2019

@author: Melchior du Lac
@description: rpSelenzyme REST entry script

"""

import os
import json
import libsbml
from datetime import datetime
from flask import Flask, request, jsonify, send_file, abort
from flask_restful import Resource, Api
import io
import tarfile
import csv
import sys
import glob
import tempfile

sys.path.insert(0, '/home/')
import rpSBML
import rpTool
sys.path.insert(0, '/home/selenzy/')
import Selenzy

############## Cache ##############

DATADIR = '/home/selenzy/data/'
selenzy_data = Selenzy.readData(DATADIR)

uniprot_aaLenght = {}
with open(DATADIR+'sel_len.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    next(csv_reader)
    for row in csv_reader:
        uniprot_aaLenght[row[0].split('|')[1]] = int(row[1])

#######################################################
############## REST ###################################
#######################################################

app = Flask(__name__)
api = Api(app)

def stamp(data, status=1):
    appinfo = {'app': 'rpSelenzyme', 'version': '0.1',
               'author': 'Pablo Carbonel, Melchior du Lac',
               'organization': 'BRS',
               'time': datetime.now().isoformat(),
               'status': status}
    out = appinfo.copy()
    out['data'] = data
    return out


## REST App.
#
#
class RestApp(Resource):
    def post(self):
        return jsonify(stamp(None))
    def get(self):
        return jsonify(stamp(None))


##
#
#
def runSelenzyme_mem(inputTar,
                     outputTar,
                     pathway_id='rp_pathway',
                     host_taxonomy_id=83333,
                     num_results=50,
                     direction=0,
                     noMSA=True,
                     fp='RDK',
                     rxn_type='smarts',
                     min_aa_length=100):
    #loop through all of them and run FBA on them
    with tarfile.open(fileobj=outputTar, mode='w:xz') as tf:
        with tarfile.open(fileobj=inputTar, mode='r:xz') as in_tf:
            for member in in_tf.getmembers():
                if not member.name=='':
                    rpsbml = rpSBML.rpSBML(member.name, libsbml.readSBMLFromString(in_tf.extractfile(member).read().decode("utf-8")))
                    if rpTool.singleSBML(selenzy_data, uniprot_aaLenght, rpsbml, host_taxonomy_id, pathway_id, num_results, direction, noMSA, fp, rxn_type, min_aa_length):
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
                     num_results=50,
                     direction=0,
                     noMSA=True,
                     fp='RDK',
                     rxn_type='smarts',
                     min_aa_length=100):
    with tempfile.TemporaryDirectory() as tmpOutputFolder:
        with tempfile.TemporaryDirectory() as tmpInputFolder:
            tar = tarfile.open(fileobj=inputTar, mode='r:xz')
            tar.extractall(path=tmpInputFolder)
            tar.close()
            for sbml_path in glob.glob(tmpInputFolder+'/*'):
                fileName = sbml_path.split('/')[-1].replace('.sbml', '').replace('.xml', '').replace('.rpsbml', '')
                rpsbml = rpSBML.rpSBML(fileName)
                rpsbml.readSBML(sbml_path)
                if rpTool.singleSBML(selenzy_data, uniprot_aaLenght, rpsbml, host_taxonomy_id, pathway_id, num_results, direction, noMSA, fp, rxn_type, min_aa_length):
                    rpsbml.writeSBML(tmpOutputFolder)
                rpsbml = None
            with tarfile.open(fileobj=outputTar, mode='w:xz') as ot:
                for sbml_path in glob.glob(tmpOutputFolder+'/*'):
                    fileName = str(sbml_path.split('/')[-1].replace('.sbml', '').replace('.xml', '').replace('.rpsbml', ''))+'.rpsbml.xml'
                    info = tarfile.TarInfo(fileName)
                    info.size = os.path.getsize(sbml_path)
                    ot.addfile(tarinfo=info, fileobj=open(sbml_path, 'rb'))


## REST Query
#
# REST interface that generates the Design.
# Avoid returning numpy or pandas object in
# order to keep the client lighter.
class RestQuery(Resource):
    def post(self):
        inputTar = request.files['inputTar']
        params = json.load(request.files['data'])
        #pass the cache parameters to the rpSelenzyme object
        outputTar = io.BytesIO()
        ######## HDD #######
        runSelenzyme_hdd(inputTar,
                         outputTar,
                         params['pathway_id'],
                         params['host_taxonomy_id'],
                         params['num_results'],
                         params['direction'],
                         params['noMSA'],
                         params['fp'],
                         params['rxn_type'],
                         params['min_aa_length'])
        ######## MEM #######
        #runSelenzyme_mem(inputTar, outputTar, params['pathway_id'], params['host_taxonomy'], params['num_results'])
        ###### IMPORTANT ######
        outputTar.seek(0)
        #######################
        return send_file(outputTar, as_attachment=True, attachment_filename='rpSelenzyme.tar', mimetype='application/x-tar')


api.add_resource(RestApp, '/REST')
api.add_resource(RestQuery, '/REST/Query')


if __name__== "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True, threaded=True)
