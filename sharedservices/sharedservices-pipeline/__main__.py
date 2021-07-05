import pulumi
import pulumi_aws as aws
from pulumi import export, ResourceOptions
import json

# Buildspec SharedNetworking file
with open("./buildspec_sharednetworking.yaml", mode="r") as buildspec_sharednetworking:
    buildspec_sharednetworking = buildspec_sharednetworking.read()


# Buildspec Member accounts file
with open("./buildspec_memberaccounts.yaml", mode="r") as buildspec_memberaccounts:
    buildspec_memberaccounts = buildspec_memberaccounts.read()


with open("./../../config.json") as config_file:
    data = json.load(config_file)

############################################################################################################
#######################################Declaring Env Variables##############################################
BRANCH = "main"
ENV = "dev"
SHARED_NETWORKING_ACCOUNT_STAGE_ACTION= "up"
MEMBER_ACCOUNT_STAGE_ACTION= "up"
REPO_NAME = data['REPO_NAME']
SOURCE_VERSION = data['SOURCE_VERSION']
STATE_BUCKET = data['STATE_BUCKET']
SHAREDNETWORKING_ACCOUNT_ID = data['ACCOUNT']['SHARED_NETWORKING']['ID']
SHAREDSERVICES_ACCOUNT_ID = data['ACCOUNT']['SHARED_SERVICES']['ID']
DEV2 = data['ACCOUNT']['DEV2']['ID']
DEV3 = data['ACCOUNT']['DEV3']['ID']
############################################################################################################
################################Creating Codebuild role policy##############################################
Account_List = [
    "dev2",
    "dev3"
]


codebuild_role_policy = aws.iam.Policy(
    "codebuildRolePolicy",
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "CodeBuildDefaultPolicy",
                    "Effect": "Allow",
                    "Action": ["codebuild:*", "iam:PassRole"],
                    "Resource": "*",
                },
                {
                    "Sid": "CloudWatchLogsAccessPolicy",
                    "Effect": "Allow",
                    "Action": [
                        "logs:FilterLogEvents",
                        "logs:GetLogEvents",
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                    ],
                    "Resource": "*",
                },
                {
                    "Sid": "CodeCommitAccessPolicy",
                    "Effect": "Allow",
                    "Action": [
                        "codecommit:GitPull",
                        "codecommit:GetBranch",
                        "codecommit:GetCommit",
                        "codecommit:GetRepository",
                        "codecommit:ListBranches",
                        "codecommit:ListRepositories",
                    ],
                    "Resource": "*",
                },
                {
                    "Sid": "S3AccessPolicy",
                    "Effect": "Allow",
                    "Action": [
                        "s3:CreateBucket",
                        "s3:GetObject",
                        "s3:ListObject",
                        "s3:ListObjectV2",
                        "s3:PutObject",
                    ],
                    "Resource": "*",
                },
                {
                    "Sid": "S3BucketIdentity",
                    "Effect": "Allow",
                    "Action": ["s3:GetBucketAcl", "s3:GetBucketLocation"],
                    "Resource": "*",
                },
                {
                    "Sid": "AssumeRole",
                    "Effect": "Allow",
                    "Action": ["sts:AssumeRole"],
                    "Resource": [
                        "arn:aws:iam::{}:role/codebuild_role_crossaccount".format(SHAREDNETWORKING_ACCOUNT_ID),
                        "arn:aws:iam::{}:role/codebuild_role_crossaccount".format(DEV2),
                        "arn:aws:iam::{}:role/codebuild_role_crossaccount".format(DEV3)
                    ],
                },
            ],
        }
    ),
)
############################################################################################################
#######################################Creating Codebuild role##############################################
codebuild_role = aws.iam.Role(
    "codebuildRole",
    managed_policy_arns=[codebuild_role_policy.arn],
    name="Infrastructure_Codebuild_role_crossaccount_" +ENV,
    assume_role_policy="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codebuild.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
""",
)
############################################################################################################
#########################################Creating Artifact Bucket###########################################
codepipeline_bucket = aws.s3.Bucket(
    "codepipelineBucket", acl="private", tags={"Name": "dinesh-pulumi-codepipeline-bucket"}
)
###########################################################################################################
##############################Creating Codebuild project SharedNetworking##################################
codebuild_project_sharednetworking = aws.codebuild.Project(
    "CodebuildProjectSharednetworking",
    description="codebuild_project_sharednetworking",
    name="Infrastructure_cross_account_codebuild_project_sharednetworking_" + ENV,
    build_timeout=30,
    service_role=codebuild_role.arn,
    artifacts=aws.codebuild.ProjectArtifactsArgs(
        type="NO_ARTIFACTS",
    ),
    environment=aws.codebuild.ProjectEnvironmentArgs(
        compute_type="BUILD_GENERAL1_SMALL",
        image="aws/codebuild/standard:3.0",
        type="LINUX_CONTAINER",
        image_pull_credentials_type="CODEBUILD",
        environment_variables=[
            aws.codebuild.ProjectEnvironmentEnvironmentVariableArgs(
                name="PULUMI_CONFIG_PASSPHRASE", value=""
            ),
            aws.codebuild.ProjectEnvironmentEnvironmentVariableArgs(
                name="ACCOUNT_ID", value=SHAREDSERVICES_ACCOUNT_ID
            ),
            aws.codebuild.ProjectEnvironmentEnvironmentVariableArgs(
                name="STATE_BUCKET", value=STATE_BUCKET
            ),
        ],
    ),
    logs_config=aws.codebuild.ProjectLogsConfigArgs(
        cloudwatch_logs=aws.codebuild.ProjectLogsConfigCloudwatchLogsArgs(
            group_name="codebuild-sharednetworking-log-group-" + ENV,
            stream_name="codebuild-sharednetworking-log-stream-" + ENV,
        )
    ),
    source=aws.codebuild.ProjectSourceArgs(
        type="CODECOMMIT",
        location="https://git-codecommit.ap-southeast-2.amazonaws.com/v1/repos/" + REPO_NAME,
        git_clone_depth=1,
        git_submodules_config=aws.codebuild.ProjectSourceGitSubmodulesConfigArgs(
            fetch_submodules=True,
        ),
        buildspec=buildspec_sharednetworking,
    ),
    source_version=SOURCE_VERSION,
    tags={"Environment": ENV},
)

############################################################################################################
###############################Creating Codebuild project member accounts##################################
codebuild_project_memberaccounts = aws.codebuild.Project(
    "CodebuildProjectMemberaccounts",
    description="codebuild_project_memberaccounts",
    name="Infrastructure_cross_account_codebuild_project_memberaccounts_" + ENV,
    build_timeout=30,
    service_role=codebuild_role.arn,
    artifacts=aws.codebuild.ProjectArtifactsArgs(
        type="NO_ARTIFACTS",
    ),
    environment=aws.codebuild.ProjectEnvironmentArgs(
        compute_type="BUILD_GENERAL1_SMALL",
        image="aws/codebuild/standard:3.0",
        type="LINUX_CONTAINER",
        image_pull_credentials_type="CODEBUILD",
        environment_variables=[
            aws.codebuild.ProjectEnvironmentEnvironmentVariableArgs(
                name="PULUMI_CONFIG_PASSPHRASE", value=""
            ),
            aws.codebuild.ProjectEnvironmentEnvironmentVariableArgs(
                name="ACCOUNT_ID", value=DEV2
            ),
            aws.codebuild.ProjectEnvironmentEnvironmentVariableArgs(
                name="SHAREDNETWORKING_ACCOUNT_ID", value=SHAREDNETWORKING_ACCOUNT_ID
            ),
            aws.codebuild.ProjectEnvironmentEnvironmentVariableArgs(
                name="STATE_BUCKET", value=STATE_BUCKET
            ),
        ],
    ),
    logs_config=aws.codebuild.ProjectLogsConfigArgs(
        cloudwatch_logs=aws.codebuild.ProjectLogsConfigCloudwatchLogsArgs(
            group_name="codebuild-memberaccounts-log-group-" + ENV,
            stream_name="codebuild-memberaccounts-log-stream-" + ENV,
        )
    ),
    source=aws.codebuild.ProjectSourceArgs(
        type="CODECOMMIT",
        location="https://git-codecommit.ap-southeast-2.amazonaws.com/v1/repos/" + REPO_NAME,
        git_clone_depth=1,
        git_submodules_config=aws.codebuild.ProjectSourceGitSubmodulesConfigArgs(
            fetch_submodules=True,
        ),
        buildspec=buildspec_memberaccounts,
    ),
    source_version=SOURCE_VERSION,
    tags={"Environment": ENV},
)

############################################################################################################
####################################Creating Codepipeline Policy############################################
codepipeline_policy = aws.iam.Policy(
    "codepipelinePolicy",
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["s3:*"], "Resource": ["*"]},
                {
                    "Effect": "Allow",
                    "Action": [
                        "codebuild:*",
                    ],
                    "Resource": "*",
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "codecommit:*",
                    ],
                    "Resource": "arn:aws:codecommit:ap-southeast-2:{}:{}".format(SHAREDSERVICES_ACCOUNT_ID, REPO_NAME)
                },
            ],
        }
    ),
)
############################################################################################################
####################################Creating Codepipeline Role##############################################
codepipeline_role = aws.iam.Role(
    "codepipelineRole",
    managed_policy_arns=[codepipeline_policy.arn],
    name="Infrastructure_Codepipeline_role_" + ENV,
    assume_role_policy="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codepipeline.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
""",
)

############################################################################################################
####################################Creating Codepipeline Role##############################################
codepipeline = aws.codepipeline.Pipeline(
    "codepipeline",
    name="Infrastructure_cross_account_codepipeline_" + ENV,
    role_arn=codepipeline_role.arn,
    artifact_store=aws.codepipeline.PipelineArtifactStoreArgs(
        location=codepipeline_bucket.bucket,
        type="S3",
    ),
    stages=[
        aws.codepipeline.PipelineStageArgs(
            name="Source",
            actions=[
                aws.codepipeline.PipelineStageActionArgs(
                    name="Source",
                    category="Source",
                    owner="AWS",
                    provider="CodeCommit",
                    version="1",
                    output_artifacts=["source_output"],
                    configuration={
                        "RepositoryName": REPO_NAME,
                        "BranchName": BRANCH,
                    },
                )
            ],
        ),
        aws.codepipeline.PipelineStageArgs(
            name="DeployInfrastructure-SharedNetworking",
            actions=[
                aws.codepipeline.PipelineStageActionArgs(
                    name="DeployInfrastructure",
                    category="Build",
                    owner="AWS",
                    provider="CodeBuild",
                    input_artifacts=["source_output"],
                    version="1",
                    configuration={
                        "ProjectName": codebuild_project_sharednetworking.name,
                        "EnvironmentVariables": json.dumps(
                            [
                                {
                                    "name": "PULUMI_CONFIG_PASSPHRASE",
                                    "value": "",
                                    "type": "PLAINTEXT",
                                },
                                {
                                    "name": "PULUMI_CONFIG_PASSPHRASE_FILE",
                                    "value": "",
                                    "type": "PLAINTEXT",
                                },
                                {
                                    "name": "ACCOUNT",
                                    "value": "sharednetworking",
                                    "type": "PLAINTEXT",
                                },
                                {
                                    "name": "STACK",
                                    "value": "sharednetworking-vpc",
                                    "type": "PLAINTEXT",
                                },
                                {
                                    "name": "ENVIRONMENT",
                                    "value": ENV,
                                    "type": "PLAINTEXT",
                                },
                                {
                                    "name": "ACCOUNT_ID",
                                    "value": SHAREDNETWORKING_ACCOUNT_ID,
                                    "type": "PLAINTEXT",
                                },
                                {
                                    "name": "ACTION", 
                                    "value": SHARED_NETWORKING_ACCOUNT_STAGE_ACTION, 
                                    "type": "PLAINTEXT"
                                },
                            ]
                        ),
                    },
                )
            ],
        ),
        aws.codepipeline.PipelineStageArgs(

            name="DeployInfrastructure-MemberAccounts",
            actions=[
                aws.codepipeline.PipelineStageActionArgs(
                    name=name,
                    category="Build",
                    owner="AWS",
                    provider="CodeBuild",
                    input_artifacts=["source_output"],
                    version="1",
                    configuration={
                        "ProjectName": codebuild_project_memberaccounts.name,
                        "EnvironmentVariables": json.dumps(
                            [
                                {
                                    "name": "PULUMI_CONFIG_PASSPHRASE",
                                    "value": "",
                                    "type": "PLAINTEXT",
                                },
                                {
                                    "name": "PULUMI_CONFIG_PASSPHRASE_FILE",
                                    "value": "",
                                    "type": "PLAINTEXT",
                                },
                                {
                                    "name": "ACCOUNT",
                                    "value": name,
                                    "type": "PLAINTEXT",
                                },
                                {
                                    "name": "STACK",
                                    "value": f"{name}-vpc",
                                    "type": "PLAINTEXT",
                                },
                                {
                                    "name": "ENVIRONMENT",
                                    "value": ENV,
                                    "type": "PLAINTEXT",
                                },
                                {
                                    "name": "ACCOUNT_ID",
                                    "value":data['ACCOUNT'][name.upper()],
                                    "type": "PLAINTEXT",
                                },
                                {
                                    "name": "ACTION", 
                                    "value": MEMBER_ACCOUNT_STAGE_ACTION, 
                                    "type": "PLAINTEXT"
                                },
                            ]
                        ),
                    },
                )
                for name  in Account_List
            ],
        )
    ]
)