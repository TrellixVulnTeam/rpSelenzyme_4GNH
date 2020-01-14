# Docker file that installs docker container for Selenzy
#
# rename this file to "Dockerfile"
# build with: "sudo docker build -t selenzy ."

FROM continuumio/anaconda3:4.4.0

# Install rdkit
RUN conda install -c conda-forge flask-restful
RUN conda install -c rdkit rdkit
# To avoid error: "SystemError: initialization of rdmolops raised unreported exception"
RUN conda install numpy=1.13
RUN conda install -c anaconda biopython
RUN conda install -c bioconda emboss
RUN conda install -c biobuilds t-coffee

WORKDIR home

RUN git clone -b Flask https://github.com/pablocarb/selenzy.git
COPY data.tar.xz /home/selenzy/
RUN tar xf selenzy/data.tar.xz -C /home/selenzy/
RUN rm /home/selenzy/data.tar.xz
RUN sed -i "s/app\.config\['KEEPDAYS'\] = 10/app\.config\['KEEPDAYS'\] = 0\.125 #three hours/g" /home/selenzy/flaskform.py
RUN mkdir /home/selenzy/log
RUN mkdir /home/selenzy/uploads

ENTRYPOINT ["python"]

CMD ["/home/selenzy/flaskform.py", "-uploaddir", "/home/selenzy/uploads", "-datadir", "/home/selenzy/data", "-logdir", "/home/selenzy/log" ]

EXPOSE 5000
