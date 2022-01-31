#!/bin/bash

VAR="TEST"
echo $VAR
echo 'HOLY '$VAR

for i in ./custom_unicorn_output/*.json
do
    SEDINPUT='s/None/custom_unicorn_output\/'$i'/g'
    echo $SEDINPUT

    ls $i | xargs sed -i '' $SEDINPUT

done
