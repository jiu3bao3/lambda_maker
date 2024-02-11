# -*- coding: utf-8 -*-
from abc import ABC
from botocore.exceptions import ClientError
from zipfile import ZipFile
import boto3
import os
import yaml
import tempfile

class AWSClient(ABC):
  """
  AWS操作の抽象クラス
  """
  def __init__(self, config_path="config.yml"):
    self.config = self.load_yml(config_path)
    self.client = self.create_client(self.SERVICE)

  def load_yml(self, config_path):
    with open(config_path, 'r') as yml:
      return yaml.safe_load(yml)

  def create_client(self, service_name):
    param = {}
    param["region_name"] = self.config["aws"]["region"]
    param["endpoint_url"] = self.config["aws"]["endpoint_url"]
    param["aws_access_key_id"] = self.config["aws"]["access_key_id"]
    param["aws_secret_access_key"] = self.config["aws"]["secret_access_key"]
    return boto3.client(service_name, **param)

class LambdaCreater(AWSClient):
  """
  Lambda操作クラス
  """
  SERVICE = "lambda"
  def create_function(self):
    name = self.function_name()
    lambda_config = self.config["aws"]["lambda"]
    if self.__is_function_exists(name):
      if lambda_config["override"]:
        self.client.delete_function(FunctionName=name)
      else:
        raise Exception("Function {} already exists!".format(name))

    param = { "Publish" : True }
    param["Runtime"] = lambda_config["runtime"]
    param["Role"] = lambda_config["role"]
    param["Handler"] = lambda_config["handler"]
    param["FunctionName"] = name
    param["Code"] = { "ZipFile" :  self.__compress_source() }
    response = self.client.create_function(**param)
    if response['ResponseMetadata']['HTTPStatusCode'] >= 400:
      print(response)
      raise Exception("Failed to make lambda")
    return response['FunctionArn']

  def function_name(self):
    handler = self.config["aws"]["lambda"]["handler"]
    return handler.split(".")[1]

  def module_name(self):
    handler = self.config["aws"]["lambda"]["handler"]
    return handler.split(".")[0]

  def __is_function_exists(self, function_name):
    try:
      response = self.client.get_function(FunctionName=function_name)
      if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return response["Configuration"]["State"]
      return False
    except ClientError as e:
      return False

  def __compress_source(self):
    directory = self.config["aws"]["lambda"]["source_dir"]
    source_path = os.path.join(directory, "{}.py".format(self.module_name()))
    data = None
    with tempfile.TemporaryDirectory() as tmpdir:
      zip_path = os.path.join(tmpdir, "lambda.zip")
      with ZipFile(zip_path, 'w') as zip:
        zip.write(source_path, "{}.py".format(self.module_name()))
      with open(zip_path, 'rb') as f:
        data = f.read()
    return data

class APIGatewayCreater(AWSClient):
  """
  APIGateway操作クラス
  """
  SERVICE = "apigateway"
  def create_api_gateway(self, function_arn):
    rest_api_gateway_id = self.make_rest_api_gateway(self.config["aws"]["apigateway"]["rest_api_gateway_name"])
    root_resource_id = self.get_root_resource(rest_api_gateway_id)
    sub_resource_id = self.create_sub_resource(rest_api_gateway_id, root_resource_id)
    self.put_method(rest_api_gateway_id, sub_resource_id)
    self.put_integration(rest_api_gateway_id, sub_resource_id, function_arn)
    self.deploy(rest_api_gateway_id)
    print(self.get_endpoint(rest_api_gateway_id, function_arn))

  def get_endpoint(self, rest_api_gateway_id, function_arn):
    function_name = function_arn.split(":")[-1]
    endpoint = "http://localhost:4566/restapis/{}/test/_user_request_/{}".format(rest_api_gateway_id, function_name)
    return endpoint

  def make_rest_api_gateway(self, name):
    response = self.client.create_rest_api(name=name)
    if response['ResponseMetadata']['HTTPStatusCode'] >= 400:
      raise Exception(response)
    return response['id']

  def get_root_resource(self, restapi_gateway_id):
    response = self.client.get_resources(restApiId=restapi_gateway_id)
    if response['ResponseMetadata']['HTTPStatusCode'] >= 400:
      raise Exception(response)
    else:
      for item in response['items']:
        if item['path'] == '/':
          return item['id']
    return None

  def create_sub_resource(self, resource_id, root_resource_id):
    response = self.client.create_resource(parentId=root_resource_id, restApiId=resource_id, pathPart="{proxy+}")
    if response['ResponseMetadata']['HTTPStatusCode'] >= 400:
      raise Exception(response)
    return response['id']

  def put_method(self, gateway_id, resource_id):
    response = self.client.put_method(restApiId=gateway_id, resourceId=resource_id, httpMethod="ANY", authorizationType='None')
    if response['ResponseMetadata']['HTTPStatusCode'] >= 400:
      raise Exception(response)

  def put_integration(self, rest_api_gateway_id, resource_id, function_arn):
    uri_template = "arn:aws:apigateway:{}:lambda:path/2015-03-31/functions/{}/invocations"
    apigateway_config = self.config["aws"]["apigateway"]
    param = { "restApiId" :rest_api_gateway_id, "resourceId" : resource_id }
    param["httpMethod"] =  apigateway_config["http_method"]
    param["type"] = apigateway_config["type"]
    param["integrationHttpMethod"] = apigateway_config["integration_http_method"]
    param["uri"] = uri_template.format(self.config["aws"]["region"], function_arn)
    response = self.client.put_integration(**param)
    if response['ResponseMetadata']['HTTPStatusCode'] >= 400:
      raise Exception(response)

  def deploy(self, restapi_gateway_id):
    response = self.client.create_deployment(restApiId=restapi_gateway_id, stageName=self.config["aws"]["apigateway"]["stage_name"])
    if response['ResponseMetadata']['HTTPStatusCode'] >= 400:
      raise Exception(response)

def main():
  # Lambdaを作成
  lambda_creater = LambdaCreater()
  function_arn = lambda_creater.create_function()
  # API Gateway作成
  apigateway_creater = APIGatewayCreater()
  apigateway_creater.create_api_gateway(function_arn)

if __name__ == '__main__':
  print('START')
  main()
  print('END')
