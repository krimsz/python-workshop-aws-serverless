# Python Workshop. Serverless app

The aim of this repo is to show a use case using the serverless stack in AWS using Python.
The project is about creating a data pipeline that will get data from a web page and process it forward until it reaches a database. The high level architecture can be found in the diagram below.
![Architecture Diagram](./images/architecture.png?raw=true "Architecture Diagram")
### Dependencies
1) Python >= 3.6. [Download here](https://www.python.org/downloads/)
2) awscli [Instructions here](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
    - pip3 install awscli --upgrade --user
3) Configure awscli. A User will be provided per working station
    - Create/Edit file ~/.aws/credentials and add the following:
    ```
    [courseX]
    region=eu-west-2
    aws_access_key_id=PROVIDED_ACCESS_KEY
    aws_secret_access_key=PROVIDED_SECRET_ACCESS_KEY
    ```
4) npm. [Download here](https://nodejs.org/en/)
5) serverles [More info here](https://serverless.com/framework/docs/providers/aws/guide/installation/)
    - npm install -g serverless

#### Recommendations for installation

It is recommended to create [virtualenvs](https://virtualenv.pypa.io/en/latest/) for Python projects to not pollute your local python installation. 

Virtualenv is a tool that allows to create isolated python environments. Allows to have different dependencies per project and avoids that these dependencies conflict with each other (e.g. having different versions of the same library for different projects)

```
pip3 install virtualenv
```
There are several strategies on how many virtualenvs to create and where. Some people prefer to have a directory where all the virtualenvs are being stored. We will proceed with the approach of one virtualenv per project, always called "venv" in the root folder of the project (helps to standarize the way of working)

Therefore run the following commands **from the root folder of the project**
```
virtualenv -p python3 venv
```
Finally virtualenvs need to be activated (can also be deactivated). While a virtualenv is activated, the python related commands (pip,python...) will point towards this venv rather than the local python installation
In order to activate the virtualenv
```
source venv/bin/activate
```
In case we want to deactivate it
```
deactivate
```
Once the virtualenv is active we might want to install the required dependencies. The file "requirements.txt" contains the dependencies needed
```
pip install -r requirements.txt
```
### Assumptions:
- In order to prevent the attendees from bringing down a webpage from a 3rd party provider (DDOs it), a url will be provided with a webpage that can safely be scrapped.
- It is nice to have but not expected to have a full TDD approach.
- An skeleton of the project structure is provided. The content of this skeleton is mainly the folder structure as well as the required resources for the architecture above 
- Some dependencies are suggested to be used (are used in the proposed solution)

### How to work during the session
The aim of the session is to create a data pipeline, including scrapper, kinesis streams and data processors using the provided resources and skeleton. There are some scripts provided that try to ease the deployment part. The scripts require:
- ENV VAR **suffix**: The name of the user each workstation is using
- ENV VAR **url**: The url of the webpage that is going to be scrapped

The AWS_PROFILE name should be "courseX" (being X the specific number) as shown above in the configuration section, please update the scripts accordingly

Example
```
suffix=courseX url=http://my.url ./deploy-resources.sh
```

## AWS services 

We are not going to have to manage any server directly in AWS, everything we are going to use are managed services (Hey, serverless!). This means there is no need to ssh inside anywhere, there is no need to apply security patches ever time a vulnerability is discovered in any OS.

Please bear in mind that no server doesn't mean no configuration. There is a lot of configuration going on when using a cloud provider(in this case also specifc just to AWS) and in a real project scenario way more configuration than shown here will be needed.

Security wise, moving to a serverless framework will change the way attackers will try to attack our system and **WE STILL HAVE TO CARE ABOUT SECURITY**. Amazon takes care of their part of security (the services should work the way they are intended to work) but they don't take responsibility on badly designed/insecure use cases uses might take. 

### [IAM](https://aws.amazon.com/iam/)
Stands for Identity and Access Management. It is the "user administration" service within AWS. Allows administrators to set up users, groups and the permissions these have.
In our particular case we are using it in two different ways:
- All of the users provided have permissions so they can deploy resources in AWS. This is already handled
- The code itself will need permission to access different resources. This will have to be explicitly set in the serverless.yml files
- The permissions are set through Roles and Policies. Using these we set which **Actions** can be applied on which **Resources** and **WHO** can assume these permissions and apply them (either a service, user...)

In serverless an example of a role for the entire file would be:
```
provider:
  name: aws
  iamRoleStatements:
    - Effect: "Allow"
      Action:
        - "kinesis:PutRecord"
        - "kinesis:PutRecords"
        - "kinesis:GetShardIterator"
        - "kinesis:DescribeStream"
      Resource: some-kinesis-arn-goes-here
    - Effect: "Allow"
      Action:
        - "logs:CreateLogGroup"
        - "logs:CreateLogStream"
        - "logs:PutLogEvents"
      Resource: "arn:aws:logs:*:*:*"
```

### [Lambda](https://aws.amazon.com/lambda/)
A lambda in AWS is a piece of code that is executed as a service. This means no server needs to be spinned up by us and the lambda will take care itself in case it needs to be scaled up.

A lambda consists of some code with an entrypoint (a function, typically called handle()) that accepts an event and a context (always does it this way). 
- The event will contain details of the caller of the lambda 
- The context will contain other meta data linked to the lambda

The billing of the lambda works per GB/hour in increments of 100ms. Therefore lambda will cost more when more memory is allocated and more time is running.

Lambda can also accept Environment Variables that can be accessed within the code (usually these contain details that are dependant per environment and can be set on deploy time).

The handler is the entrypoint for our lambda, it means that it is going to be the function executed whenever the lambda is invoked.

In our pipeline, lambda is the unit of execution for all the logic to happen. In serverless it is defined as following:
```
functions:
  sample-lambda:
    handler: path/to/handler.handle
    MemorySize: 128
    Timeout: 20
    environment:
      SCRAP_URL: ${env:url}
```
### [Kinesis](https://aws.amazon.com/kinesis/)
Kinesis is a data streaming service that allows real time data to be moved around. It allows to attach multiple producers and consumers and process the data

Taking advantage of triggering lambdas using events, we can easily make an event driven architecture using kinesis as the channel of communication.
Kinesis also stores the data for a period of time, until that point the data can be retrieved again. 

**Note**. If a lambda fails after being triggered by a kinesis message it will try to reprocess it again. It could reach the point to prevent our application from not processing anything because of a "bad" record that makes it fail forever since the order is also preserved(until the record gets removed because of the TTL).

```
resources:
  Resources:
    KinesisDataProcessing:
      Type: AWS::Kinesis::Stream
      Properties:
        Name: data-processing-stream-${env:suffix}
        ShardCount: 1
```

[We could also have used SQS?](https://aws.amazon.com/sqs/)

### [DynamoDB](https://aws.amazon.com/dynamodb/)
Amazon DynamoDB is a key-value and document database. It's not optimal for any use case but is the cheapest option that AWS offers as a noSQL database and the only one that can be used as a service. 

In Dynamo we need to define the schema for the keys and indexes that we are going to use. Other attributes are not needed to be defined on creation time.

Dynamo (at least until recently) has always needed to define RCU and WCU (Read/Write Capacity Units) that basically set how much "power" we set to each table/index. Trespassing this "power" will result in calls to dynamo failing, that will mean that the user wil lhave to handle this failure (since Dynamo will not throttle it or retry later). Dynamo is also not realy well thought for use cases where the spike of information happens in a short span of time since the scaling options don't allow it to scale fast enough as to fulfill the spike need.

The pricing model is per WCU/RCU being used. 
It also doesn't fit virtually almost any use case due to its nature. It can't easily be partitioned based on a field/condition, a lot of manual maintenance and not really prepared for spikes of requests coming in (at least not until recently). Best practices [can be found here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)


It could be defined in serverless as:
```
resources:
  Resources:
    MoviesTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: movie
        AttributeDefinitions:
          - AttributeName: id
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH
        ProvisionedThroughput:
          ReadCapacityUnits: 1
          WriteCapacityUnits: 1
```

### [API Gateway](https://aws.amazon.com/api-gateway/)
Amazon API Gateway is a fully managed service that makes it easy to create, publish, maintain, monitor, and secure APIs. In our use case we are creating an event that will trigger the lambda that will initiate the process of scrapping.

API Gateway can be used in many ways and combined with lambda we are going to use the "Lambda Proxy integration" that enables our lambda to fully access the content of the request using the event object. In serverless we are defining the API gateway endpoint using the events section within the lambda declaration:

```
functions:
  sample-lambda:
    handler: path/to/handler.handle
    MemorySize: 128
    Timeout: 20
    environment:
      SCRAP_URL: ${env:url}
    events:
      - http:
          path: scrap_movies
          method: get
```


### [Cloud Formation](https://aws.amazon.com/cloudformation/)
AWS CloudFormation provides a common language for us to describe and provision all the infrastructure resources in the AWS environment. 

We are not going to directly use CloudFormation templates but we are going to use serverless as an intermediary that will do things for us without us having to worry about the exact syntax of CloudFormation (be careful with this too, bein a third party up makes it not optimal for production-ready deployments, [SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) or plain CloudFormation are a better idea (both maintained by AWS))

## [Serverless](https://serverless.com/)

Serverless is a framework we use for the configuration and deployment. The syntax is similar to CloudFormation but it will do some things for us (such as creating intermediate resources, events...). The creation of resources and lambda functions will be splitted in different files and the resources will be referenced using **Outputs** and Importing the values when needed
Since the environment will be shared between different users, it is needed to add a "suffix" to the resource names to avoid conflicts in the names.

We will also use a serverless plugin that will build the dependencies for the lambda and package it for us. The plugin is called "serverless-python-requirements" and can be installed using the bash script "install-sls-dependencies"

### Proposed improvements:
For those teams that finish with the implementation within the time of the workshop. The possible improvements are marked in the diagram with a blue background and could be (not limited to only these, if you think of any other thing feel free to do so):
- [ ] Create a lambda with an API Gateway interface to query the database (Improvement Proposal 1)
- [ ] Create another table and store the data that errors inside (Improvement Proposal 2)
- [ ] Try to mess around with unittest in Python, you will probably have to fight python import system and understand how it works (Improvement Proposal 4)
- [ ] Change the webpage to be scrapped to something that feels more appealing