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
        self.default_path=os.getcwd().replace('\\','/')+'/data/'
        self.name='db2'
        self.client=chromadb.Client()
        self.collection=self.client.get_or_create_collection(self.name)
        self.index=0

    def get_path(self):
        return self.default_path
    def set_path(self,path):
        if type(path)!=str:
            raise TypeError("Path should be string")
        else:
            self.default_path=path

    def read_text_file(file_path):
    
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            data = file.read()
        return {'file_name':file_path.split('\\')[-1], 'content':data}

    def read_pdf(self,file_path):
        
        data=''
        reader = PdfReader(file_path)
        for page in reader.pages:
            res+=page.extract_text()
        return {'file_name':file_path.split('\\')[-1], 'content':data}

    def read_all_files(self,path):
        if path=='':
            path=self.default_path
        print(path)
        # for file in os.listdir(path):
        #     if file.endswith(".txt"):
        #         self.read_txt(path+'\\'+file)
        #     elif file.endswith(".pdf"):
        #         self.read_pdf(path+'\\'+file)
        #     else:
        #         print("Not a valid file format")
    
    def add(self,path):
        pass


if __name__=="__main__":
    data=Data()
    