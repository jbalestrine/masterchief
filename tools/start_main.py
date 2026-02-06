#!/usr/bin/env python3
import os
import runpy

# Set environment variable for main process
os.environ['DISABLE_BACKGROUND_INDEXER'] = '1'

# Run the main app
runpy.run_path('main.py', run_name='__main__')
