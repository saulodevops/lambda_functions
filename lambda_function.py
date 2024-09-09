import json

def lambda_handler(event, context):
    # Log the received event
    print("Received event: " + json.dumps(event, indent=2))

    # Return a response
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
