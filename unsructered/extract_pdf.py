from pathlib import Path
import os, json
import unstructured_client
from unstructured_client.models import operations, shared
from unstructured_client.models.errors import SDKError
from dotenv import load_dotenv
load_dotenv()
# Folder that contains this script
file_pat='unsructered/docs/GaLore- Memory-Efficient LLM Training by Gradient Low-Rank Projection.pdf'
with open(file_pat, 'rb') as f:
    file = f.read()
    print(file)