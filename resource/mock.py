import boto3
import json

def hello(event, context):
  print(event)
  response = {}
  config = {}
  with open("config.json") as f:
    config = json.load(f)
  response["isBase64Encoded"] = False
  response["statusCode"] = 200
  response["headers"] = { "Content-Type" : "application/json" }
  response["body"] = { "message" : config["config"]["message"] }
  print(response)
  return response
