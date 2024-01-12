FROM ubuntu:latest
RUN apt -y update && apt -y upgrade
RUN apt -y install python3 python3-pip
RUN apt-get -y autoclean
RUN pip install -r requirements.txt
#
# Depending on the system on which this container is running, it may be necessary to configure
# this line in relation to an existing user on the OS.
#
# RUN chown 1026:100
ENTRYPOINT ["/bin/bash"]