pulumi stack select $STACK
RESULT=$?
if
 [ $RESULT -ne 0 ]
then
    echo "Stack not found creating stack $STACK"
    pulumi stack init $STACK
    pulumi config set aws:region ap-southeast-2
fi
    echo "Updating Pulumi Stack"
    pulumi $ACTION --yes