# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
This is an example dag for using `AWSDataSyncOperator` in a straightforward manner.

This DAG gets an AWS TaskArn for a specified source and destination, and then attempts to execute it.
It assumes there is a single task returned and does not do error checking (eg if multiple tasks were found).

This DAG relies on the following environment variables:

* SOURCE_LOCATION_URI - Source location URI, usually on premises SMB or NFS
* DESTINATION_LOCATION_URI - Destination location URI, usually S3
"""

from datetime import datetime
from os import getenv

from airflow import models
from airflow.providers.amazon.aws.operators.datasync import AWSDataSyncOperator

# [START howto_operator_datasync_1_args_1]
TASK_ARN = getenv("TASK_ARN", "my_aws_datasync_task_arn")
# [END howto_operator_datasync_1_args_1]

# [START howto_operator_datasync_1_args_2]
SOURCE_LOCATION_URI = getenv("SOURCE_LOCATION_URI", "smb://hostname/directory/")

DESTINATION_LOCATION_URI = getenv("DESTINATION_LOCATION_URI", "s3://mybucket/prefix")
# [END howto_operator_datasync_1_args_2]


with models.DAG(
    "example_datasync_1_1",
    schedule_interval=None,  # Override to match your needs
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:

    # [START howto_operator_datasync_1_1]
    datasync_task_1 = AWSDataSyncOperator(task_id="datasync_task_1", task_arn=TASK_ARN)
    # [END howto_operator_datasync_1_1]

with models.DAG(
    "example_datasync_1_2",
    start_date=datetime(2021, 1, 1),
    schedule_interval=None,  # Override to match your needs
) as dag:
    # [START howto_operator_datasync_1_2]
    datasync_task_2 = AWSDataSyncOperator(
        task_id="datasync_task_2",
        source_location_uri=SOURCE_LOCATION_URI,
        destination_location_uri=DESTINATION_LOCATION_URI,
    )
    # [END howto_operator_datasync_1_2]
