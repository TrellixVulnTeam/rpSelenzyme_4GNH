# Docker file that installs docker container for Selenzy
#
# rename this file to "Dockerfile"
# build with: "sudo docker build -t selenzy ."

#
#
#FROM continuumio/anaconda3
FROM continuumio/anaconda3:4.4.0

# Install rdkit
RUN conda install -c conda-forge flask-restful
RUN conda install -c rdkit rdkit
RUN conda install -c anaconda biopython
RUN conda install -c bioconda emboss
RUN conda install -c biobuilds t-coffee
# can use a single Dockerfile instead of the above
#FROM sbc/selenzybase 

# To be replaced by a git clone
#RUN wget http://130.88.113.226/selenzy/selenzy.tar.gz
COPY selenzy.tar.gz .
#TODO: check the hash of the tar.gz to make sure that all is good
RUN tar -xzvf selenzy.tar.gz

ENTRYPOINT ["python"]

CMD ["/selenzyPro/flaskform.py", "-uploaddir", "/selenzyPro/uploads", "-datadir", "/selenzyPro/data", "-logdir", "/selenzyPro/log" ]

EXPOSE 5000


