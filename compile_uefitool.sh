#!/bin/bash
pushd ./UEFITool
./unixbuild.sh
cp ./UEFIExtract/UEFIExtract ..
popd
