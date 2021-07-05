import pulumi
from pulumi import export, ResourceOptions
import pulumi_aws as aws
import json

#Environment variable file
with open("./../../config.json") as config_file:
    data = json.load(config_file)
SHAREDSERVICES_ACCOUNT_ID = data['ACCOUNT']['SHARED_SERVICES']['ID']
STATE_BUCKET = data['STATE_BUCKET']
ENV = "train"
assume_role_policy = aws.iam.Policy("policy",
    path="/",
    name = "assume_role_policy",
    description="assume_role_policy",
    policy=json.dumps(
            
        {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "s3:GetObject",
                "s3:GetObjectAcl",
                "s3:ListBucketMultipartUploads",
                "s3:ListAllMyBuckets",
                "s3:GetObject",
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": [
                "arn:aws:s3:::{}".format(STATE_BUCKET),
                "arn:aws:s3:::{}/*".format(STATE_BUCKET),
            ],
            "Effect": "Allow",
            "Sid": "VisualEditor1"
        },
        {
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "*"
            ],
            "Effect": "Allow",
            "Sid": "VisualEditor2"
        },
        
        {
            "Action": [
                "ecs:*",
                "apigateway:*",
                "iam:CreateRole",
                "iam:CreatePolicy",
                "ecs:*",
                "apigateway:*",
                "iam:CreateRole",
                "iam:GetRole",
                "iam:GetPolicy",
                "cloudformation:*",
                "ec2:*",
                "ram:*",
                "ssm:*",
                "iam:UpdateAssumeRolePolicy",
                "iam:ListRoleTags",
                "iam:PutRolePermissionsBoundary",
                "iam:UpdateRoleDescription",
                "iam:ListRoles",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PutRolePolicy",
                "iam:AddRoleToInstanceProfile",
                "iam:ListInstanceProfilesForRole",
                "iam:GetServiceLinkedRoleDeletionStatus",
                "iam:CreateServiceLinkedRole",
                "iam:ListAttachedRolePolicies",
                "iam:UpdateRole",
                "iam:ListRolePolicies",
                "iam:ListPolicyVersions",
                "iam:CreatePolicyVersion",
                "iam:DeletePolicyVersion",
                "iam:GetPolicyVersion",
                "iam:DetachRolePolicy",
                "iam:DeleteRole",
                "iam:DeletePolicy",
                "iam:GetRolePolicy",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:CreateLogGroup",
                "logs:DescribeLogGroups",
                "logs:ListTagsLogGroup",
                "logs:*",
                "application-autoscaling:RegisterScalableTarget",
                "application-autoscaling:DescribeScalableTargets",
                "application-autoscaling:DescribeScalingActivities",
                "application-autoscaling:DescribeScalingPolicies",
                "application-autoscaling:PutScalingPolicy",
                "application-autoscaling:DescribeScheduledActions",
                "application-autoscaling:PutScheduledAction",
                "application-autoscaling:DeregisterScalableTarget",
                "application-autoscaling:DeleteScalingPolicy",
                "elasticloadbalancing:*",
                "servicediscovery:*",
                "route53:CreateHostedZone",
                "ssm:GetParameter",
                "ssm:GetParameter",
                "ssm:PutParameter",
                "ssm:GetParameters",
                "ssm:DescribeParameters",
                "ssm:ListTagsForResource",
                "ssm:DeleteParameter",
                "route53resolver:*",
                "cloudfront:CreateDistribution",
                "cloudfront:UpdateDistribution",
                "cloudfront:ListDistributions",
                "cloudfront:GetDistribution",
                "cloudfront:TagResource",
                "cloudfront:ListTagsForResource",
                "s3:CreateBucket",
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:GetObject",
                "s3:PutBucketAcl",
                "s3:GetObjectAcl",
                "s3:PutObjectVersionAcl",
                "s3:GetObjectVersionAcl",
                "s3:GetBucketAcl",
                "s3:GetBucketCORS",
                "s3:PutBucketCORS",
                "s3:GetBucketWebsite",
                "s3:DeleteBucketWebsite",
                "s3:PutBucketWebsite",
                "s3:Get*",
                "s3:DeleteBucketPolicy",
                "s3:DeleteObject",
                "s3:PutBucketPolicy",
                "s3:PutAccessPointPolicy",
                "s3:GetEncryptionConfiguration",
                "s3:PutEncryptionConfiguration",
                "lambda:List*",
                "lambda:Get*",
                "lambda:Create*",
                "lambda:Update*"
            ],
            "Resource": "*",
            "Effect": "Allow",
            "Sid": "VisualEditor3"
        },
        {
            "Action": [
                "kms:CreateGrant",
                "kms:ListGrants",
                "kms:RevokeGrant",
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
                "kms:DescribeKey"
            ],
            "Resource": [
                "*"
            ],
            "Effect": "Allow",
            "Sid": "VisualEditor4"
        },
        {
            "Action": [
                "iam:PassRole"
            ],
            "Resource": [
                "*"
            ],
            "Effect": "Allow",
            "Sid": "VisualEditor5"
        },
    ]
}
        
        ))


assume_role =  aws.iam.Role (
    "assume_role",
    name = "codebuild_role_crossaccount",
    managed_policy_arns = [
        assume_role_policy.arn
    ],
    assume_role_policy=json.dumps   (
        {
        "Version": "2012-10-17",
        "Statement": [
            {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::{}:root".format(SHAREDSERVICES_ACCOUNT_ID)            
                },
            "Action": "sts:AssumeRole"
            }
        ]
        }

        )
)