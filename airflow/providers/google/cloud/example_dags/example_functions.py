#
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
Example Airflow DAG that displays interactions with Google Cloud Functions.
It creates a function and then deletes it.

This DAG relies on the following OS environment variables
https://airflow.apache.org/concepts.html#variables

* GCP_PROJECT_ID - Google Cloud Project to use for the Cloud Function.
* GCP_LOCATION - Google Cloud Functions region where the function should be
  created.
* GCF_ENTRYPOINT - Name of the executable function in the source code.
* and one of the below:

    * GCF_SOURCE_ARCHIVE_URL - Path to the zipped source in Google Cloud Storage

    * GCF_SOURCE_UPLOAD_URL - Generated upload URL for the zipped source and GCF_ZIP_PATH - Local path to
      the zipped source archive

    * GCF_SOURCE_REPOSITORY - The URL pointing to the hosted repository where the function
      is defined in a supported Cloud Source Repository URL format
      https://cloud.google.com/functions/docs/reference/rest/v1/projects.locations.functions#SourceRepository

"""

import os
from datetime import datetime

from airflow import models
from airflow.providers.google.cloud.operators.functions import (
    CloudFunctionDeleteFunctionOperator,
    CloudFunctionDeployFunctionOperator,
    CloudFunctionInvokeFunctionOperator,
)

GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'example-project')
GCP_LOCATION = os.environ.get('GCP_LOCATION', 'europe-west1')
# make sure there are no dashes in function name (!)
GCF_SHORT_FUNCTION_NAME = os.environ.get('GCF_SHORT_FUNCTION_NAME', 'hello').replace("-", "_")
FUNCTION_NAME = f'projects/{GCP_PROJECT_ID}/locations/{GCP_LOCATION}/functions/{GCF_SHORT_FUNCTION_NAME}'
GCF_SOURCE_ARCHIVE_URL = os.environ.get('GCF_SOURCE_ARCHIVE_URL', '')
GCF_SOURCE_UPLOAD_URL = os.environ.get('GCF_SOURCE_UPLOAD_URL', '')
GCF_SOURCE_REPOSITORY = os.environ.get(
    'GCF_SOURCE_REPOSITORY',
    f'https://source.developers.google.com/projects/{GCP_PROJECT_ID}/'
    f'repos/hello-world/moveable-aliases/master',
)
GCF_ZIP_PATH = os.environ.get('GCF_ZIP_PATH', '')
GCF_ENTRYPOINT = os.environ.get('GCF_ENTRYPOINT', 'helloWorld')
GCF_RUNTIME = 'nodejs14'
GCP_VALIDATE_BODY = os.environ.get('GCP_VALIDATE_BODY', "True") == "True"

# [START howto_operator_gcf_deploy_body]
body = {"name": FUNCTION_NAME, "entryPoint": GCF_ENTRYPOINT, "runtime": GCF_RUNTIME, "httpsTrigger": {}}
# [END howto_operator_gcf_deploy_body]

# [START howto_operator_gcf_default_args]
default_args = {'retries': '3'}
# [END howto_operator_gcf_default_args]

# [START howto_operator_gcf_deploy_variants]
if GCF_SOURCE_ARCHIVE_URL:
    body['sourceArchiveUrl'] = GCF_SOURCE_ARCHIVE_URL
elif GCF_SOURCE_REPOSITORY:
    body['sourceRepository'] = {'url': GCF_SOURCE_REPOSITORY}
elif GCF_ZIP_PATH:
    body['sourceUploadUrl'] = ''
    default_args['zip_path'] = GCF_ZIP_PATH
elif GCF_SOURCE_UPLOAD_URL:
    body['sourceUploadUrl'] = GCF_SOURCE_UPLOAD_URL
else:
    raise Exception("Please provide one of the source_code parameters")
# [END howto_operator_gcf_deploy_variants]


with models.DAG(
    'example_gcp_function',
    default_args=default_args,
    schedule_interval='@once',  # Override to match your needs
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:
    # [START howto_operator_gcf_deploy]
    deploy_task = CloudFunctionDeployFunctionOperator(
        task_id="gcf_deploy_task",
        project_id=GCP_PROJECT_ID,
        location=GCP_LOCATION,
        body=body,
        validate_body=GCP_VALIDATE_BODY,
    )
    # [END howto_operator_gcf_deploy]
    # [START howto_operator_gcf_deploy_no_project_id]
    deploy2_task = CloudFunctionDeployFunctionOperator(
        task_id="gcf_deploy2_task", location=GCP_LOCATION, body=body, validate_body=GCP_VALIDATE_BODY
    )
    # [END howto_operator_gcf_deploy_no_project_id]
    # [START howto_operator_gcf_invoke_function]
    invoke_task = CloudFunctionInvokeFunctionOperator(
        task_id="invoke_task",
        project_id=GCP_PROJECT_ID,
        location=GCP_LOCATION,
        input_data={},
        function_id=GCF_SHORT_FUNCTION_NAME,
    )
    # [END howto_operator_gcf_invoke_function]
    # [START howto_operator_gcf_delete]
    delete_task = CloudFunctionDeleteFunctionOperator(task_id="gcf_delete_task", name=FUNCTION_NAME)
    # [END howto_operator_gcf_delete]
    deploy_task >> deploy2_task >> invoke_task >> delete_task
