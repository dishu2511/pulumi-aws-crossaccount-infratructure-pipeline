from pulumi import export, ResourceOptions
import pulumi
import pulumi_aws as aws
import json


#Defining config file
with open('./../../config.json') as config_file:
    data = json.load(config_file)

VPC_CIDR = data['ACCOUNT']['SHARED_NETWORKING']['VPC_CIDR']
PRIVATE_SUBNET = data['ACCOUNT']['SHARED_NETWORKING']['PRIVATE_SUBNET']
PUBLIC_SUBNET = data['ACCOUNT']['SHARED_NETWORKING']['PUBLIC_SUBNET']
MASTER_ACCOUNT = data['ACCOUNT']['MASTER_ACCOUNT']['ID']
ORGANIZATION_ID = data['ORGANIZATION_ID']
AZ = data['AZ']

VPC_NAME = "shared-networking"
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



natgw_elastic_ip_1 = aws.ec2.Eip("natgw-1-elastic-ip",
    vpc=True,
    tags={
        "Name": f"{VPC_NAME}-natgw-1",
    }
    )
natgw_1 =  aws.ec2.NatGateway("natgw-1",
    allocation_id=natgw_elastic_ip_1.id,
    subnet_id=public_subnet_1.id,
    tags={
        "Name": f"{VPC_NAME}-natgw-1",
    },
    opts=pulumi.ResourceOptions(depends_on=[igw])
    )

natgw_1_route_table= aws.ec2.RouteTable("natgw-1-public-route-table",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            nat_gateway_id= natgw_1.id,
            #nat=natgw_1.id,
        )
    ],
    tags={
        "Name": f"{VPC_NAME}-natgw-1-public-route-table",
    }
    )


natgw_elastic_ip_2 = aws.ec2.Eip("natgw-2-elastic-ip",
    vpc=True,
    tags={
        "Name": f"{VPC_NAME}-natgw-2",
    }
    )
natgw_2 =  aws.ec2.NatGateway("natgw-2",
    allocation_id=natgw_elastic_ip_2.id,
    subnet_id=public_subnet_2.id,
    tags={
        "Name": f"{VPC_NAME}-natgw-2",
    },
    opts=pulumi.ResourceOptions(depends_on=[igw])
    )

natgw_2_route_table= aws.ec2.RouteTable("natgw-2-public-route-table",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            nat_gateway_id= natgw_2.id,
            #nat=natgw_1.id,
        )
    ],
    tags={
        "Name": f"{VPC_NAME}-natgw-2-public-route-table",
    }
    )

natgw_elastic_ip_3 = aws.ec2.Eip("natgw-3-elastic-ip",
    vpc=True,
    tags={
        "Name": f"{VPC_NAME}-natgw-3",
    }
    )
natgw_3 =  aws.ec2.NatGateway("natgw-3",
    allocation_id=natgw_elastic_ip_3.id,
    subnet_id=public_subnet_3.id,
    tags={
        "Name": f"{VPC_NAME}-natgw-3",
    },
    opts=pulumi.ResourceOptions(depends_on=[igw])
    )

natgw_3_route_table= aws.ec2.RouteTable("natgw-3-public-route-table",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            nat_gateway_id= natgw_3.id,
            #nat=natgw_1.id,
        )
    ],
    tags={
        "Name": f"{VPC_NAME}-natgw-3-public-route-table",
    }
    )
route_table_association(public_subnet_1.id, public_route_table.id, "public-1")
route_table_association(public_subnet_2.id, public_route_table.id, "public-2")
route_table_association(public_subnet_3.id, public_route_table.id, "public-3")
route_table_association(private_subnet_1.id, natgw_1_route_table.id, "private-1")
route_table_association(private_subnet_2.id, natgw_2_route_table.id, "private-2")
route_table_association(private_subnet_3.id, natgw_3_route_table.id, "private-3")

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
nacl_private = aws.ec2.NetworkAcl("nacl-private",
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


tgw = aws.ec2transitgateway.TransitGateway("tgw",
    description=f"{VPC_NAME}-tgw",
    auto_accept_shared_attachments="enable",
    default_route_table_association="enable",
    default_route_table_propagation="enable",
    dns_support="enable",
    tags={
        "Name": f"{VPC_NAME}-tgw",
    }
    )
vpc_tgw_attachment=aws.ec2transitgateway.VpcAttachment("vpc-tgw-attachment",
    subnet_ids=[
        private_subnet_1.id,
        private_subnet_2.id,
        private_subnet_3.id,
    ],
    transit_gateway_id=tgw.id,
    vpc_id=vpc.id,
    tags={
        "Name": f"{VPC_NAME}-tgw-attachment",
    }
    )
public_route_dev2 = aws.ec2.Route(
    "public-route-dev2",
    destination_cidr_block="10.1.0.0/16",
    transit_gateway_id=tgw.id,
    route_table_id=public_route_table.id

)
public_route_dev3 = aws.ec2.Route(
    "public-route-dev3",
    destination_cidr_block="10.2.0.0/16",
    transit_gateway_id=tgw.id,
    route_table_id=public_route_table.id
)

# tgw_route_table_id=aws.ec2transitgateway.get_route_table( "tgw-route-table-id",
#     id = tgw.id    
# )

tgw_route_dev2=aws.ec2transitgateway.Route("tgw-route-dev2",
    destination_cidr_block="0.0.0.0/0",
    transit_gateway_attachment_id=vpc_tgw_attachment.id,
    transit_gateway_route_table_id=tgw.association_default_route_table_id
)



tgw_share_organization=aws.ram.ResourceShare("tgw-share-organization",
    allow_external_principals=True,
    tags={
        "Name": f"{VPC_NAME}-tgw-share-organization",
    }
    )
ram_resource_association=aws.ram.ResourceAssociation("ram-resource-association",
    resource_arn=tgw.arn,
    resource_share_arn=tgw_share_organization.arn)

share_principal_association=aws.ram.PrincipalAssociation("share-principal-association",
    principal=f"arn:aws:organizations::{MASTER_ACCOUNT}:organization/{ORGANIZATION_ID}",
    resource_share_arn=tgw_share_organization.arn
    )

tgw_id_ssm = aws.ssm.Parameter("tgw-id-ssm",
    type="String",
    name=f"{VPC_NAME}-tgw-id",
    value=tgw.id
    )

