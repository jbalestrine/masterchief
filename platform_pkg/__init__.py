import os
# Make this package load modules from the existing 'platform' folder
__path__ = [os.path.join(os.path.dirname(__file__), '..', 'platform')]
