FROM ros:humble-ros-base

# Install pip dependencies
RUN apt update && apt install -y python3-pip && apt clean
RUN python3 -m pip install awscrt awsiotsdk

WORKDIR /workspace
ADD ./aws-iot-robot-connectivity-samples-ros2/workspace/src/telemetry_mqtt /workspace/src/telemetry_mqtt
RUN colcon build

ADD ./ros_entrypoint.sh /
