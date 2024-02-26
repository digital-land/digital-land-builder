#!/bin/sh

set -e

s3="https://files.planning.data.gov.uk/"

python3 bin/resources.py |
while read collection pipeline resource
do
    # https://digital-land-production-collection-dataset.s3.eu-west-2.amazonaws.com/{COLLECTION}-collection/resource/{RESOURCE}
    dir=var/resource
    path=$dir/$resource

    if [ ! -f $path ] ; then
        mkdir -p $dir
        url="$s3$collection-collection/collection/resource/$resource" 
        set +e
        set -x
        curl -qsfL $flags $url > $path
        set +x
        status=$?
        set -e
        if [ $status -ne 0 ] ; then
            echo "FAILED [$status]: $url"
        fi
    fi
done
