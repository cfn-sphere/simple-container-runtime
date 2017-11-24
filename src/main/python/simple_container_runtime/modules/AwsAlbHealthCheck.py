import logging
import boto3
from time import sleep

from simple_container_runtime.modules.Module import HealthCheckModule
from simple_container_runtime.util import get_instance_id, with_boto_retry, get_logger


class AwsAlbHealthCheck(HealthCheckModule):
    def __init__(self, config: dict):
        super().__init__(config)
        self.logger = get_logger("AwsAlbHealthCheck")
        self.region = config["region"]
        self.target_group_arn = config["target_group_arn"]
        self.timeout = int(config.get("timeout", 300))
        self.interval = int(config.get("interval", 10))
        self.instance_id = config.get("instance_id")

        if not self.instance_id:
            self.instance_id = get_instance_id()

        print(self.instance_id)
        self.client = boto3.client('elbv2', region_name=self.region)

    def run(self) -> None:
        if not self.target_is_in_service():
            raise Exception("Failed to wait for the instance to stabilize")

    @with_boto_retry()
    def _get_target_group_health(self, target_group_arn: str, instance_id: str) -> dict:
        result = self.client.describe_target_health(TargetGroupArn=target_group_arn, Targets=[{"Id": instance_id}])

        target_health = result["TargetHealthDescriptions"][0]["TargetHealth"]

        self.logger.debug("Target group state: {}".format(target_health))
        return target_health

    def target_is_in_service(self) -> bool:
        self.logger.info("Waiting for instance to become healthy in target group")

        for i in range(0, max(int(self.timeout / self.interval), 1)):
            target_health = self._get_target_group_health(self.target_group_arn, self.instance_id)
            state = target_health["State"]
            reason = target_health["Description"]

            if state == "healthy":
                self.logger.info("Instance in service")
                return True
            else:
                self.logger.info("Instance is in {} state ({})".format(state, reason))
                sleep(self.interval)

        self.logger.error("Timeout occured waiting for the instance to be healthy")
        return False


if __name__ == "__main__":
    AwsAlbHealthCheck({"region": "eu-west-1", "instance_id": "i-0656914e5d367fffe",
                       "target_group_arn": "arn:aws:elasticloadbalancing:eu-west-1:744969810879:targetgroup/grafana-test/e17ad9a360b45a95"}).run()
