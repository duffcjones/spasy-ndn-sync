#!/bin/bash

pyinstaller "SpatialSync3.py" --onefile --specpath "./spec" --clean
#pyinstaller "Consumer.py" --onefile --specpath "./spec" --clean
#pyinstaller "Producer.py" --onefile --specpath "./spec"
