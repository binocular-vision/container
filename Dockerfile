FROM continuumio/miniconda3


# Install app dependencies
RUN pip install --upgrade pip
RUN pip install Pillow
RUN pip install numpy
RUN pip install scipy
RUN pip install sklearn
RUN pip install google-cloud-storage
RUN python -mpip install -U pip
RUN python -mpip install -U matplotlib
RUN pip install https://github.com/binocular-vision/ibv/zipball/master






# Bundle app source
COPY storage.json storage.json
ENV GOOGLE_APPLICATION_CREDENTIALS="storage.json"
COPY exp.py exp.py
