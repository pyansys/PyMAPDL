#!/bin/bash
echo "Waiting for the MAPDL service to be up..."
nc -v -z localhost "$PYMAPDL_PORT"
echo "::group:: ps aux Output" && ps aux && echo "::endgroup::" 

echo "Waiting for MAPDL port is open..."
echo "::group:: Waiting for the MAPDL port to be open..." 
while ! nc -z localhost "$PYMAPDL_PORT"; do
sleep 0.1
done
echo "::endgroup::"
echo "MAPDL service is up!"
