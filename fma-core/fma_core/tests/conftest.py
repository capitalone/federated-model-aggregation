import os
import sys
from os.path import abspath, dirname

root_dir = dirname(dirname(dirname(abspath(__file__))))
print(root_dir)
sys.path.append(root_dir)
os.environ["FMA_SETTINGS_MODULE"] = "fma_core.tests.fma_settings"
