FROM brsynth/rpbase

RUN apt-get install -y libxrender1 libsm6 libxext6

RUN conda install -c rdkit rdkit
RUN conda install -c anaconda biopython==1.77
RUN conda install -c bioconda emboss
RUN conda install -c biobuilds t-coffee

#WARNING: we are copying a skinny py37 compatible version of selenzyme -- need to update this if there are selenzyme updates
#essentially added the allow_pickle=True flag to the np.load( commands along the code
COPY selenzy /home/
COPY data.tar.xz /home/selenzy/
RUN tar xf selenzy/data.tar.xz -C /home/selenzy/
RUN rm /home/selenzy/data.tar.xz

COPY rpToolServe.py /home/
COPY rpTool.py /home/
COPY galaxy/code/tool_rpSelenzyme.py /home/
