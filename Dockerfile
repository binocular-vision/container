FROM continuumio/miniconda3


# Install app dependencies
RUN pip install --upgrade pip
RUN pip install Pillow
RUN pip install numpy
RUN pip install scipy
RUN pip install sklearn
RUN pip install ipywidgets
RUN python -mpip install -U pip
RUN python -mpip install -U matplotlib
RUN pip install progressbar2




# Bundle app source
COPY import_test.py import_test.py

CMD ["python", "import_test.py"]
