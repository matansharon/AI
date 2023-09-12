import chromadb
import os
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import seaborn as sns
import re
from PyPDF2 import PdfReader
import os


class Data:
    def __init__(self):
        import chromadb
        self.name=''
        self.client=chromadb.Client()
        self.collection=self.client.get_or_create_collection('db2')
        self.index=0

    

    def read_txt(self,path):
        with open(path, 'r', encoding='ISO-8859-1') as file:
            data = file.read()

    def read_pdf(self,path):
        from PyPDF2 import PdfReader
        res=''
        reader = PdfReader(path)
        for page in reader.pages:
            res+=page.extract_text()

    def read_all_files(self,path):
        for file in os.listdir(path):
            if file.endswith(".txt"):
                self.read_txt(path+file)
            elif file.endswith(".pdf"):
                self.read_pdf(path+file)
            else:
                print("Not a valid file format")
    
    def add(self,path):
        pass
    
    
    if __name__=="__main__":
        print("Hello World")