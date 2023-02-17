"""Sets root directory for repo and env vars for tests."""
import os
import sys
from os.path import abspath, dirname

root_dir = dirname(abspath(__file__))
sys.path.append(root_dir)

os.environ["FMA_SETTINGS_MODULE"] = "federated_learning_project.fma_settings"
os.environ["FMA_DATABASE_NAME"] = "None"
os.environ["FMA_DATABASE_HOST"] = "None"
os.environ["FMA_DATABASE_PORT"] = "None"
os.environ["FMA_DB_SECRET_PATH"] = "fake/path"
