FROM brsynth/rpbase:dev

RUN conda install -c rdkit rdkit
RUN conda install -c anaconda biopython
RUN conda install -c bioconda emboss
RUN conda install -c biobuilds t-coffee

RUN apt-get install -y libxrender1 libsm6 libxext6
#WARNING: we are copying a py37 compatible version of selenzyme -- need to update this if there are selenzyme updates
#add the allow_pickle=True to the np.load( command
COPY selenzy /home/
COPY data.tar.xz /home/selenzy/
RUN tar xf selenzy/data.tar.xz -C /home/selenzy/
RUN rm /home/selenzy/data.tar.xz

COPY rpToolServe.py /home/
COPY rpTool.py /home/
COPY tool_rpSelenzyme.py /home/
