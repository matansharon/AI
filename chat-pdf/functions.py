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
    
    pdf_files.close()
    
def Answer_from_document(user_input):
    user_query_vector=get_embedding(user_input,engine='text-embedding-ada-002')
    with open('my_knowledge_base.json','r',encoding='utf-8') as jasonfile:
        data=json.load(jasonfile)
        for item in data:
            item['embedding']=np.array(item['embedding'])
        
        for item in data:
            item['similarity']=cosine_similarity(item['embedding'],user_query_vector)
        
        
        sorted_data=sorted(data,key=lambda x:x['similarity'],reverse=True)
        
        context=''
        for item in sorted_data[:2]:
            context+=item['text']
        
        my_message=[
            {"role":'system','content':"your a helpful AI"},
            {"role":'user','content':"the folowing is a context: \n {}\n\n is the answer to your question"},
            
        ]
        response=openai.Completion.create(
            model='gpt-3.5-turbo',
            messages=my_message,
            max_tokens=200
        )
        return response['choices'][0]['message']['content']
        
    
