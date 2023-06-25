import PyPDF2,uuid,os,json,openai
import dotenv
import numpy as np
from openai.embeddings_utils import get_embedding,cosine_similarity


def save_uploaded(uploadfile):
    with open(uploadfile.name, 'wb') as f:
        f.write(uploadfile.getbuffer())

def learn_pdf(file_path):
    content_chunks=[]
    pdf_files=open(file_path,'rb')
    pdf_reader=PyPDF2.PdfFileReader(pdf_files)
    for page in pdf_reader:
        content=page.extractText()
        obj={
            "id":str(uuid.uuid4()),
            'text':content,
            'embedding':get_embedding(content,engine='text-embedding-ada-002')
            
        }
        content_chunks.append(obj)
        
    json_file_path='my_knowledge_base.json'
    with open(json_file_path,'r',encoding='utf-8') as f:
        data=json.load(f)
        
    for i in content_chunks:
        data.append(i)
    with open(json_file_path,'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=4)
    
def Answer_from_document(user_input):
    return "This is a dummy answer from document"
    
