FROM python:3.7-slim

# Install base dependencies
RUN apt-get update && apt-get install -y wget libjpeg-dev libxml2-dev libxslt-dev lib32z1-dev python-lxml
RUN pip install virtualenv 

# Set up non-root user and assign manpage access
# since the splunkpackagingtoolkit requires access to the global manpage (man1) dir
RUN useradd -ms /bin/bash splunkbuild
RUN mkdir /usr/share/man/man1 
RUN chown -R splunkbuild:splunkbuild /usr/share/man/man1 
USER splunkbuild

# Change working directory to local user
WORKDIR /home/splunkbuild
RUN chown -R splunkbuild:splunkbuild /home/splunkbuild
RUN mkdir /home/splunkbuild/src

# Set up virtualenvironment for appinspect
ENV VIRTUAL_ENV_APPINSPECT=/home/splunkbuild/.venv/appinspect
RUN virtualenv -p python3 $VIRTUAL_ENV_APPINSPECT
ENV PATH="$VIRTUAL_ENV_APPINSPECT/bin:$PATH"

# Install and download appinspect + dependencies
RUN pip install Pillow
RUN wget https://download.splunk.com/misc/appinspect/splunk-appinspect-latest.tar.gz
RUN pip install splunk-appinspect-latest.tar.gz
RUN rm splunk-appinspect-latest.tar.gz

# Set up virtualenvironment for packagingtoolkit
ENV VIRTUAL_ENV_TOOLKIT=/home/splunkbuild/.venv/packagingtoolkit
RUN virtualenv -p python3 $VIRTUAL_ENV_TOOLKIT
ENV PATH="$VIRTUAL_ENV_TOOLKIT/bin:$PATH"

# Install and download appinspect + packagingtoolkit
RUN pip install semantic_version
RUN wget https://download.splunk.com/misc/packaging-toolkit/splunk-packaging-toolkit-1.0.1.tar.gz
RUN pip install splunk-packaging-toolkit-1.0.1.tar.gz
RUN rm splunk-packaging-toolkit-1.0.1.tar.gz

COPY --chown=splunkbuild:splunkbuild upload.py ./
WORKDIR /home/splunkbuild/src
