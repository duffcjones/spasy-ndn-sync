#!/bin/bash

cd /spatialsync

cmd="sudo python3 -m mini.experiments.scenario${1}.${2} ${3}"

eval "$cmd"

#sudo python3 -m mini.experiments.scenario2.updatesize
