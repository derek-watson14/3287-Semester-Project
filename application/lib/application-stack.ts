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
      environment: {
        DB_BUCKET_NAME: bucketDeployment.deployedBucket.bucketName,
      },
    });
    bucketDeployment.deployedBucket.grantRead(router);

    const api = new apigateway.RestApi(this, 'dbApi', {
      restApiName: 'Database Service',
      description: 'This service serves database queries.',
      apiKeySourceType: apigateway.ApiKeySourceType.HEADER,
      deployOptions: {
        stageName: 'prod',
      },
    });

    // Protect API with API Key 
    const apiKey = api.addApiKey('ApiKey');
    const plan = api.addUsagePlan('UsagePlan', {
      name: 'Easy',
      throttle: {
        rateLimit: 10,
        burstLimit: 2,
      },
    });
    plan.addApiKey(apiKey);
    plan.addApiStage({
      stage: api.deploymentStage,
    });

    const proxyResource = api.root.addProxy({
      defaultIntegration: new apigateway.LambdaIntegration(router),
      defaultMethodOptions: {
        apiKeyRequired: true,
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      },
    });
  }
}
