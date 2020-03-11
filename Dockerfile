FROM brsynth/rprest:dev

RUN apt-get install -y libxrender1 libsm6 libxext6

RUN conda install -c rdkit rdkit
RUN conda install -c anaconda biopython
RUN conda install -c bioconda emboss
RUN conda install -c biobuilds t-coffee

#WARNING: we are copying a skinny py37 compatible version of selenzyme -- need to update this if there are selenzyme updates
#essentially added the allow_pickle=True flag to the np.load( commands along the code
COPY selenzy /home/
COPY data.tar.xz /home/selenzy/
RUN tar xf selenzy/data.tar.xz -C /home/selenzy/
RUN rm /home/selenzy/data.tar.xz

##### If using Pablo's Flask service ############## 
#RUN sed -i "s/app\.config\['KEEPDAYS'\] = 10/app\.config\['KEEPDAYS'\] = 0\.125 \#three hours/g" /home/selenzy/flaskform.py
#RUN sed -i "s/maintenance(app\.config\['KEEPDAYS'\])/maintenance(-1)/g" selenzy/flaskform.py
#RUN mkdir selenzy/log
#RUN mkdir selenzy/uploads

#ENTRYPOINT ["python"]
#CMD ["/home/selenzy/flaskform.py", "-uploaddir", "/home/selenzy/uploads", "-datadir", "/home/selenzy/data", "-logdir", "/home/selenzy/log" ]
#EXPOSE 5000
###################################################
#ENTRYPOINT ["conda", "run", "-n", "conda_selenzyme", "python", "rpToolServe.py"]

#COPY rpToolServe.py /home/
#COPY rpTool.py /home/

#ENTRYPOINT ["conda", "run", "-n", "conda_selenzyme", "python"]
#CMD ["/home/rpToolServe.py"]
#EXPOSE 8888
