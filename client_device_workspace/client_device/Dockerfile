FROM ros:humble-ros-base

# Install pip dependencies
RUN apt update && apt install -y python3-pip && apt clean
RUN python3 -m pip install awscrt awsiotsdk

WORKDIR /workspace
ADD ./workspace/src/ /workspace/src
RUN colcon build

ADD ./ros_entrypoint.sh /
