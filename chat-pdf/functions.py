import PyPDF2



def save_uploaded(uploadfile):
    with open(uploadfile, 'wb') as f:
        f.write(uploadfile.getbuffer())

def learn_pdf(file_path):
    content_chunks=[]
    pdf_files=open(file_path,'rb')
    # pdf_reader=PyPDF2.PdfFileReader(pdf_files)
    print(pdf_files)
    
