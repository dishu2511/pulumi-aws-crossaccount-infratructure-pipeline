echo "Updating Pulumi Stack"

# Update the stack
#pulumi stack select pilot
pulumi stack select $STACK
#pulumi stack init -s $STACK
pulumi $ACTION --yes