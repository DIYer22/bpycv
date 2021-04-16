# git clone https://github.com/DIYer22/bpycv && cd bpycv && docker build -t bpycv ./ && docker run -v /tmp:/tmp -it bpycv

FROM nytimes/blender:2.92-gpu-ubuntu18.04

LABEL Author="Lei Yang <DIYer22@GitHub>"
LABEL Title="bpycv in Docker"

RUN apt-get update
RUN apt install git -y

RUN ${BLENDERPY} -m pip install -U pip setuptools wheel 
RUN ${BLENDERPY} -m pip install -U ipython

COPY . /bpycv/
WORKDIR /bpycv
RUN ${BLENDERPY} setup.py install
WORKDIR /tmp
CMD blender -b -E CYCLES -P /bpycv/example/6d_pose_demo.py && sh /bpycv/example/run_ycb_demo.sh
