import logging
import boto3
from time import sleep

from simple_container_runtime.modules.Module import HealthCheckModule
from simple_container_runtime.util import get_instance_id


class AwsElbHealthCheck(HealthCheckModule):
    def __init__(self, config: dict):
        super().__init__(config)
        self.region = config["region"]
        self.loadbalancer_name = config["loadbalancer_name"]
        self.timeout = int(config.get("timeout", 300))
        self.interval = int(config.get("interval", 10))
        self.instance_id = get_instance_id()

    def run(self):
        if not self.is_in_service_from_elb_perspective(self.instance_id, self.loadbalancer_name):
            raise Exception("Failed to wait for the instance to stabilize")

    def _get_elb_instance_state(self, instance_id: str, elb_name: str):
        client = boto3.client('elb', region_name=self.region)
        result = client.describe_instance_health(LoadBalancerName=elb_name, Instances=[{"InstanceId": instance_id}])
        state = result["InstanceStates"][0]["State"]

        logging.debug("ELB state for instance {0}: {1}".format(instance_id, state))
        return state

    def is_in_service_from_elb_perspective(self, instance_id: str, elb_name: str):
        logging.info("Waiting for instance {} to become healthy in elb {}".format(instance_id, elb_name))

        for i in range(0, max(int(self.timeout / self.interval), 1)):
            state = self._get_elb_instance_state(instance_id, elb_name)
            if state == 'InService':
                logging.info("instance in service")
                return True
            else:
                logging.debug('waiting for instance')
                sleep(self.interval)

        logging.warning("timeout for in-service check exceeded")
        return False
