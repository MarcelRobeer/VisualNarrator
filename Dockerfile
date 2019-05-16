FROM python:3.6
LABEL maintainer "mosser@i3s.unice.fr"

######
# To build the image:
# docker build -t acedesign/visualnarrator .
# To publish the image:
# 
# To use the image:
# docker run -it --rm -v "$PWD":/usr/src/app/output acedesign/visualnarrator:latest output/example_stories.txt
######

# Installing Visual Narrator
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_md
COPY . .

# Preparing the mountpoint for loading stories files
RUN mkdir output
VOLUME output

# Starting Visual Narrator
ENTRYPOINT ["python", "run.py"]
