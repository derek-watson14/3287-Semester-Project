import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { BucketDeployment } from 'aws-cdk-lib/aws-s3-deployment';
import * as lambda from 'aws-cdk-lib/aws-lambda';

export class ApplicationStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

    // Create S3 bucket
    const dbBucket = new s3.Bucket(this, 'dbBucket', {
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const deployment = new BucketDeployment(this, 'dbBucketDeployment', {
      sources: [cdk.aws_s3_deployment.Source.asset('./db/db.zip')],
      destinationBucket: dbBucket,
    });

    const dbLambda = new lambda.Function(this, 'dbLambda', {
      runtime: lambda.Runtime.PYTHON_3_11,
      code: lambda.Code.fromAsset('./lambda'),
      handler: 'dbLambda.handler',
      environment: {
        DB_BUCKET_NAME: deployment.deployedBucket.bucketName,
      },
    });
    deployment.deployedBucket.grantRead(dbLambda);
  }
}
