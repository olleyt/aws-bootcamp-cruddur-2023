import pathlib
import boto3
import json

# switch to cloudwatch 
import logging

# might not need these 3
import os


# enable logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

def upload_template_to_s3(template_file, bucket_name, bucket_prefix, object_key):
    s3 = boto3.client('s3')

    with open(template_file, 'r') as file:
        template_body = file.read()

    # Add prefix to the object key
    object_key_with_prefix = f'{bucket_prefix}/{object_key}'

    s3.put_object(
        Body=template_body,
        Bucket=bucket_name,
        Key=object_key_with_prefix
    )


def deploy_stack(cfn_client, cfn_resource, stack_name, template_file, parameters):
    
    tags = [
        {
            'Key': 'application',
            'Value': 'cruddur'
        }
    ]

    stack_params = [{'ParameterKey': key, 'ParameterValue': value} for key, value in parameters.items()]
    
    with open(template_file, 'r') as file:
        template_body = file.read()

    #response = cloudformation.create_stack(
    stack = cfn_resource.create_stack(
        StackName=stack_name,
     #   TemplateURL=template_file,
        TemplateBody=template_body,
        Parameters=stack_params,
        Capabilities=['CAPABILITY_IAM'],
        Tags=tags
    )

    stack_id = stack.stack_id
    print(f"Stack '{stack_name}' creation initiated.")
    print(f"Stack creation job ID: {stack_id}")

    waiter = cfn_client.get_waiter('stack_create_complete')
    waiter.wait(StackName=stack_name)

    print(f"Stack '{stack_name}' creation completed.")

def load_template(self, *args):
        """
        loads sql statement into a string
        """
        green = '\033[92m'
        no_color = '\033[0m'
        print(f'{green} PATH {no_color}')

        app_path = pathlib.Path('.')
        template_path = app_path.joinpath('params').with_suffix('.json')
        template_content = template_path.read_text()
        return template_content


def load_parameters(parameter_file):
    with open(parameter_file, 'r') as file:
        parameter_data = json.load(file)
    return parameter_data


def main():
    # Load stack names, template files, and parameter mappings
    # replace with pathlib
    stack_info_file = './bin/cfn/stack_info.json'
    with open(stack_info_file, 'r') as file:
        stack_info = json.load(file)

    # Load parameters to use for tags or cloudformation resources later on
     # replace with pathlib
    parameter_file = './bin/cfn/common_params.json'
    parameters = load_parameters(parameter_file)
    region = parameters['region']

    # create session
    cfn_client = boto3.client('cloudformation')
    cfn_session = boto3.Session(region_name = region)
    cfn_resource = cfn_session.resource("cloudformation") 
    
 
    
    # for future use
    previous_outputs = {}
    
    # Deploy stacks
    for stack in stack_info:
        stack_name = stack['stack_name']
        template_file = stack['template_url']
        stack_parameters = stack['params']

         # Upload the template to S3 bucket (only for cruddur)
        bucket_name = parameters["bucket"]
        bucket_prefix = stack['stack_id']
        upload_template_to_s3(template_file, bucket_name, bucket_prefix, template_file)
        template_url = f"https://s3.amazonaws.com/{bucket_prefix}/{bucket_name}/{template_file}"

        deploy_stack(cfn_client, cfn_resource, stack_name, template_file, stack_parameters)

        # Store stack outputs for use in the next stack
        response = cfn_client.describe_stacks(StackName=stack_name)
        stack_info = response['Stacks'][0]
        
        print(stack_info)

        # this code needs to be debugged
        # stack_outputs = stack_info.get('Outputs', [])

        # outputs = {}
        # for output in stack_outputs:
        #     output_key = output['OutputKey']
        #     output_value = output['OutputValue']
        #     outputs[output_key] = output_value

        # print(stack_outputs)
         
    print("Stack deployment completed.")

if __name__ == '__main__':
    main()





