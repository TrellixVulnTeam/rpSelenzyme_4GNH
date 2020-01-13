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
# To avoid error: "SystemError: initialization of rdmolops raised unreported exception"
RUN conda install numpy=1.13
RUN conda install -c anaconda biopython
RUN conda install -c bioconda emboss
RUN conda install -c biobuilds t-coffee

RUN cd /home \
 && git clone -b Flask https://github.com/pablocarb/selenzy.git \
 && sed -i "s/app\.config\['KEEPDAYS'\] = 10/app\.config\['KEEPDAYS'\] = 0\.125 \#three hours/g" selenzy/flaskform.py \
 && mkdir selenzy/log selenzy/uploads

ENTRYPOINT ["python"]

#CMD ["/selenzyPro/flaskform.py", "-uploaddir", "/selenzyPro/uploads", "-datadir", "/selenzyPro/data", "-logdir", "/selenzyPro/log" ]
CMD ["/home/selenzy/flaskform.py", "-uploaddir", "/home/selenzy/uploads", "-datadir", "/selenzy/data", "-logdir", "/home/selenzy/log" ]

EXPOSE 5000
