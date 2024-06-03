FROM ros:humble-ros-base

RUN apt update && apt install -y python3-pip && apt clean
RUN python3 -m pip install awscrt awsiotsdk

WORKDIR /workspace
ADD ./aws-iot-robot-connectivity-samples-ros2/workspace/src /workspace/src
RUN bash -c "source /opt/ros/humble/setup.bash && colcon build"

ADD ./ros_entrypoint.sh /
