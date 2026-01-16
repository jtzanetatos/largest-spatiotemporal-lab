FROM ros:jazzy-ros-base

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_ROOT=/opt/ros2_ws

# Install minimal dev tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3-pip \
      python3-colcon-common-extensions \
      git && \
    apt-get clean

# Set up ROS workspace
WORKDIR ${ROS_ROOT}
RUN mkdir -p src

# Auto-source ROS in new shells
RUN echo "source /opt/ros/setup.bash" >> /root/.bashrc
RUN echo "source ${ROS_ROOT}/install/setup.bash" >> /root/.bashrc

ENTRYPOINT ["/bin/bash"]