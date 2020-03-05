FROM brsynth/rpbase:dev

COPY environment_selenzyme.yml .
RUN conda env create -f environment_selenzyme.yml
#ENV PATH /usr/local/envs/conda_selenzyme/bin:$PATH
#ENV CONDA_DEFAULT_ENV conda_selenzyme 
#RUN /bin/bash -c "source activate conda_selenzyme"
#SHELL ["conda", "run", "-n", "conda_selenzyme", "/bin/bash", "-c"]
RUN echo "source activate $(head -1 /home/environment_selenzyme.yml | cut -d' ' -f2)" > ~/.bashrc
ENV PATH /usr/local/envs/$(head -1 /home/environment_selenzyme.yml | cut -d' ' -f2)/bin:$PATH

RUN apt-get install -y libxrender1 libsm6 libxext6

RUN git clone -b Flask https://github.com/pablocarb/selenzy.git
COPY data.tar.xz /home/selenzy/
RUN tar xf selenzy/data.tar.xz -C /home/selenzy/

##### If using Pablo's Flask service ############## 
#RUN sed -i "s/app\.config\['KEEPDAYS'\] = 10/app\.config\['KEEPDAYS'\] = 0\.125 \#three hours/g" /home/selenzy/flaskform.py
#RUN sed -i "s/maintenance(app\.config\['KEEPDAYS'\])/maintenance(-1)/g" selenzy/flaskform.py
#RUN mkdir selenzy/log
#RUN mkdir selenzy/uploads

COPY rpToolServe.py /home/
COPY rpTool.py /home/
COPY tool_rpSelenzyme.py /home/
