import boto3
from simple_container_runtime.exceptions import ScrBaseException

from simple_container_runtime.modules.Module import SignalModule
from simple_container_runtime.util import get_instance_id, with_boto_retry, get_logger


class AwsCfnSignal(SignalModule):
    def __init__(self, config: dict):
        super().__init__(config)

        self.logger = get_logger("AwsCfnSignal")

        self.region = config["region"]
        self.stack_name = config["stack_name"]
        self.logical_resource_id = config["logical_resource_id"]
        self.instance_id = get_instance_id()

    @with_boto_retry()
    def run(self, successful: bool):
        if successful:
            status = "SUCCESS"
        else:
            status = "FAILURE"

        boto3.client("cloudformation", region_name=self.region).signal_resource(
            StackName=self.stack_name,
            LogicalResourceId=self.logical_resource_id,
            UniqueId=self.instance_id,
            Status=status
        )
