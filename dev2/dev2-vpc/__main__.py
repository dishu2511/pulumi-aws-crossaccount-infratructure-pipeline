from pulumi import export, ResourceOptions
import pulumi
import os
import pulumi_aws as aws
import json

TGW_ID = os.environ['TGW_ID']
#TGW_ID = "tgw-0cf125626b356ccec"
#Defining config file
with open('./../../config.json') as config_file:
    data = json.load(config_file)

VPC_CIDR = data['ACCOUNT']['DEV2']['VPC_CIDR']
PRIVATE_SUBNET = data['ACCOUNT']['DEV2']['PRIVATE_SUBNET']
PUBLIC_SUBNET = data['ACCOUNT']['DEV2']['PUBLIC_SUBNET']
AZ = data['AZ']

VPC_NAME = "dev2"
vpc = aws.ec2.Vpc(
    "vpc",
    cidr_block=VPC_CIDR,
    tags={
        "Name": f"{VPC_NAME}-vpc"
    }
    )

igw = aws.ec2.InternetGateway("igw",
    vpc_id=vpc.id,
    tags={
        "Name": f"{VPC_NAME}-igw",
    })
def subnet(cidr, name):
    aws.ec2.Subnet(f"{name}-subnet",
    vpc_id=vpc.id,
    cidr_block=cidr,
    tags={
        "Name": name,
    }
    )

private_subnet_1= aws.ec2.Subnet("private-subnet-1",
    vpc_id=vpc.id,
    cidr_block=PRIVATE_SUBNET[0],
    availability_zone= AZ[0],
    tags={
        "Name": f"{VPC_NAME}-private-subnet-1",
    }
    )
private_subnet_2= aws.ec2.Subnet("private-subnet-2",
    vpc_id=vpc.id,
    cidr_block=PRIVATE_SUBNET[1],
    availability_zone= AZ[1],
    tags={
        "Name": f"{VPC_NAME}-private-subnet-2",
    }
    )
private_subnet_3= aws.ec2.Subnet("private-subnet-3",
    vpc_id=vpc.id,
    cidr_block=PRIVATE_SUBNET[2],
    availability_zone= AZ[2],
    tags={
        "Name": f"{VPC_NAME}-private-subnet-3",
    }
    )

public_subnet_1= aws.ec2.Subnet("public-subnet-1",
    vpc_id=vpc.id,
    cidr_block=PUBLIC_SUBNET[0],
    availability_zone= AZ[0],
    tags={
        "Name": f"{VPC_NAME}-public-subnet-1",
    }
    )

public_subnet_2= aws.ec2.Subnet("public-subnet-2",
    vpc_id=vpc.id,
    cidr_block=PUBLIC_SUBNET[1],
    availability_zone= AZ[1],
    tags={
        "Name": f"{VPC_NAME}-public-subnet-2",
    }
    )
public_subnet_3= aws.ec2.Subnet("public-subnet-3",
    vpc_id=vpc.id,
    cidr_block=PUBLIC_SUBNET[2],
    availability_zone= AZ[2],
    tags={
        "Name": f"{VPC_NAME}-public-subnet-3",
    }
    )
public_route_table = aws.ec2.RouteTable("public-route-table",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=igw.id,
        )
    ],
    tags={
        "Name": f"{VPC_NAME}-public-route-table",
    }
    )
def route_table_association(subnet, route_table, type):
    aws.ec2.RouteTableAssociation(f"route-table-association-{type}",
    subnet_id=subnet,
    route_table_id=route_table
    )



vpc_tgw_attachment=aws.ec2transitgateway.VpcAttachment(
    "tvpc-tgw-attachment",
    subnet_ids=[
        private_subnet_1.id,
        private_subnet_2.id,
        private_subnet_3.id,
    ],
    transit_gateway_id=TGW_ID,
    vpc_id=vpc.id,
    tags={
        "Name": f"{VPC_NAME}-tgw-attachment",
    }
    )
nacl_public = aws.ec2.NetworkAcl("nacl-public",
    vpc_id=vpc.id,
    subnet_ids=[
        public_subnet_1.id,
        public_subnet_2.id,
        public_subnet_3.id,
    ],
    egress=[aws.ec2.NetworkAclEgressArgs(
        protocol="-1",
        rule_no=200,
        action="allow",
        cidr_block="0.0.0.0/0",
        from_port=0,
        to_port=0,
    )],
    ingress=[aws.ec2.NetworkAclIngressArgs(
        protocol="-1",
        rule_no=100,
        action="allow",
        cidr_block="0.0.0.0/0",
        from_port=0,
        to_port=0,
    )],
    tags={
        "Name": f"{VPC_NAME}-nacl-public",
    })

private_route_table=aws.ec2.RouteTable("private-route-table",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            transit_gateway_id= TGW_ID,
            #nat=natgw_1.id,
        )
    ],
    tags={
        "Name": f"{VPC_NAME}-private-route-table",
    }
    )

route_table_association(public_subnet_1.id, public_route_table.id, "public-1")
route_table_association(public_subnet_2.id, public_route_table.id, "public-2")
route_table_association(public_subnet_3.id, public_route_table.id, "public-3")
route_table_association(private_subnet_1.id, private_route_table.id, "private-1")
route_table_association(private_subnet_2.id, private_route_table.id, "private-2")
route_table_association(private_subnet_3.id, private_route_table.id, "private-3")

nacl_public = aws.ec2.NetworkAcl("nacl-private",
    vpc_id=vpc.id,
    subnet_ids=[
        private_subnet_1.id,
        private_subnet_2.id,
        private_subnet_3.id,
    ],
    egress=[aws.ec2.NetworkAclEgressArgs(
        protocol="-1",
        rule_no=200,
        action="allow",
        cidr_block="0.0.0.0/0",
        from_port=0,
        to_port=0,
    )],
    ingress=[aws.ec2.NetworkAclIngressArgs(
        protocol="-1",
        rule_no=100,
        action="allow",
        cidr_block="0.0.0.0/0",
        from_port=0,
        to_port=0,
    )],
    tags={
        "Name": f"{VPC_NAME}-nacl-private",
    })
