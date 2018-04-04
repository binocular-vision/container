FROM continuumio/miniconda3


# Install app dependencies
RUN pip install --upgrade pip
RUN pip install Pillow
RUN pip install numpy
RUN pip install scipy
RUN pip install sklearn
RUN python -mpip install -U pip
RUN python -mpip install -U matplotlib
RUN pip install https://github.com/binocular-vision/ibv/zipball/master

RUN mkdir feb27




# Bundle app source
COPY shift5_70patch.png shift5_70patch.png
COPY dm.png dm.png
COPY exp.py exp.py
