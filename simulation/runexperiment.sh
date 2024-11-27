#!/bin/bash
cmd="sudo python3 -m experiments.scenario${1}.${2} ${3} ${4} ${5}"

eval "$cmd"
