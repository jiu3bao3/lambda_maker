import boto3
import json

def hello(event, context):
  print(event)
  response = {}
  response["isBase64Encoded"] = False
  response["statusCode"] = 200
  response["headers"] = { "Content-Type" : "application/json" }
  response["body"] = { "message" : "Hello Lambda" }
  print(response)
  return response
