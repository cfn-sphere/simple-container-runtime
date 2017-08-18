import os
import boto3
import json
from pathlib import Path
from simple_container_runtime.modules.Module import PreStartModule
from simple_container_runtime.util import get_logger


class AwsEcrLogin(PreStartModule):
    def __init__(self, config: dict):
        super().__init__(config)

        self.logger = get_logger("AwsEcrLogin")
        self.region = config["region"]
        self.account_id = str(config["account_id"])

    def run(self):
        response = boto3.client("ecr", region_name=self.region).get_authorization_token(
            registryIds=[self.account_id]
        )

        auth_data = response["authorizationData"][0]
        endpoint = auth_data["proxyEndpoint"]
        token = auth_data["authorizationToken"]

        self.logger.info("Writing credentials for ECR repo {}".format(endpoint))

        path = "{}/.docker".format(Path.home())
        if not os.path.exists(path):
            os.makedirs(path)

        with open("{}/config.json".format(path), "w") as f:
            f.write(json.dumps({"auths": {endpoint: {"auth": token, "email": ""}}}))

        return True
