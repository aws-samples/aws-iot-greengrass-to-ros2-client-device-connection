#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time
from awscrt import mqtt, io
from awsiot import mqtt_connection_builder
from awsiot.greengrass_discovery import DiscoveryClient

RETRY_WAIT_TIME_SECONDS = 5


class MqttPublisher(Node):
    def __init__(self):
        super().__init__('mqtt_publisher')

        self.declare_parameter("path_for_config", "")
        self.declare_parameter("connection_retries", 5)

        path_for_config = self.get_parameter("path_for_config").get_parameter_value().string_value

        with open(path_for_config) as f:
          cert_data = json.load(f)

        self.get_logger().info("Config we are loading is :\n{}".format(cert_data))

        self.discover_connection(cert_data)
        self.init_subs()

    def discover_connection(self, cert_data) -> bool:
        tries = 0

        tls_options = io.TlsContextOptions.create_client_with_mtls_from_path(
            cert_data["certificatePath"],
            cert_data["privateKeyPath"],
        )
        tls_options.override_default_trust_store_from_path(None, cert_data["rootCAPath"])
        tls_context = io.ClientTlsContext(tls_options)

        discovery_client = DiscoveryClient(
            io.ClientBootstrap.get_or_create_static_default(),
            io.SocketOptions(),
            tls_context,
            # TODO: Get region from config!
            "us-west-2",
        )
        resp_future = discovery_client.discover(cert_data["clientID"])
        discover_response = resp_future.result()
        self.get_logger().debug(f"Discovery response is: {discover_response}")

        for tries in range(self.get_parameter("connection_retries").value):
            self.get_logger().info(f"Connection attempt: {tries}")
            for gg_group in discover_response.gg_groups:
                for gg_core in gg_group.cores:
                    for connectivity_info in gg_core.connectivity:
                        try:
                            self.get_logger().debug(
                                "Trying core {} as host {}:{}".format(
                                    gg_core.thing_arn,
                                    connectivity_info.host_address,
                                    connectivity_info.port
                                )
                            )
                            self.mqtt_conn = self.build_connection(
                                gg_group,
                                connectivity_info,
                                cert_data
                            )
                            return
                        except Exception as e:
                            self.get_logger().error(f"Connection failed with exception: {e}")
                            continue
            time.sleep(RETRY_WAIT_TIME_SECONDS)
        raise Exception("All connection attempts failed!")

    def build_connection(self, gg_group, connectivity_info, cert_data):
        conn = mqtt_connection_builder.mtls_from_path(
            endpoint=connectivity_info.host_address,
            port=connectivity_info.port,
            cert_filepath=cert_data["certificatePath"],
            pri_key_filepath=cert_data["privateKeyPath"],
            ca_bytes=gg_group.certificate_authorities[0].encode('utf-8'),
            client_id=cert_data["clientID"],
            clean_session=False,
            keep_alive_secs=30
        )
        connect_future = conn.connect()
        connect_future.result()
        self.get_logger().info("Connected!")
        return conn

    def init_subs(self):
        """Subscribe to mock ros2 telemetry topic"""
        self.subscription = self.create_subscription(
            String,
            'mock_telemetry',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        """Callback for the mock ros2 telemetry topic"""
        message_json = msg.data
        self.get_logger().info("Received data on ROS2 {}\nPublishing to AWS IoT".format(msg.data))
        self.mqtt_conn.publish(
            topic="ros2_mock_telemetry_topic",
            payload=message_json,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MqttPublisher()

    rclpy.spin(minimal_subscriber)

    # Destroy the node
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



