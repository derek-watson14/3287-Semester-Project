import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { BucketDeployment } from 'aws-cdk-lib/aws-s3-deployment';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';

export class ApplicationStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

    // Create S3 bucket
    const dbBucket = new s3.Bucket(this, 'dbBucket');
    const bucketDeployment = new BucketDeployment(this, 'dbBucketDeployment', {
      sources: [cdk.aws_s3_deployment.Source.asset('./db/db.zip')],
      destinationBucket: dbBucket,
    });

    const router = new lambda.Function(this, 'router', {
      runtime: lambda.Runtime.PYTHON_3_11,
      code: lambda.Code.fromAsset('./router'),
      handler: 'index.handler',
      functionName: 'soccer-db-router',
      environment: {
        DB_BUCKET_NAME: bucketDeployment.deployedBucket.bucketName,
      },
      reservedConcurrentExecutions: 2,
    });
    bucketDeployment.deployedBucket.grantRead(router);

    const api = new apigateway.LambdaRestApi(this, 'dbApi', {
      description: 'This service serves sqlite database queries.',
      handler: router,
      proxy: true,
      apiKeySourceType: apigateway.ApiKeySourceType.HEADER,
      deployOptions: {
        stageName: 'prod',
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      },
      defaultMethodOptions: {
        apiKeyRequired: true,
      },
    });

    // Protect API with API Key 
    const apiKey = api.addApiKey('ApiKey', {
      apiKeyName: 'GeneralUsageKey',
    });

    const plan = api.addUsagePlan('UsagePlan', {
      name: 'General',
      throttle: {
        rateLimit: 10,
        burstLimit: 2,
      },
    });
    plan.addApiKey(apiKey);
    plan.addApiStage({
      stage: api.deploymentStage,
    });
  }
}
