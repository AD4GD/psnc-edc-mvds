#!/bin/bash

if [ -z "$(curl -is $1 | head -n 1)" ] ; then
  	echo "0"
else
  	echo "1"
fi