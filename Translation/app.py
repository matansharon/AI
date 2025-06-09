from openai import OpenAI
openai_client = OpenAI()
import os, json

import unstructured_client
from unstructured_client.models import operations, shared

client = unstructured_client.UnstructuredClient(
    api_key_auth=os.getenv("UNSTRUCTURED_API_KEY")
)




def translate_with_openai(text,src_lang='en', tgt_lang='he'):
    completion = openai_client.chat.completions.create(
        model="gpt-4.1-mini-2025-04-14",
        messages=[
            {
                'role': 'assistant',
                'content': f"""You are a professional translator. Your task is to translate the text from {src_lang} to {tgt_lang}. 
                'You must return the translation without any additional text. 
                'You must not return the original text. 
                the document are an engineering document,specific to the field manufacture engendering on the medical devices industry. 
                """
            },
            {
                "role": "user",
                "content": f"Translate this text to Hebrew: {text} just return the translation without any additional text."
            }
        ]
    )

    return completion.choices[0].message.content



def get_list_of_elements_from_file_with_unstructured_client(file_path:str,src_lang='he', tgt_lang='en'):
    """
    This function uses the Unstructured Client to process a file and return a list of elements.
    :param filename: The path to the input file.
    :param src_lang: Source language for translation.
    :param tgt_lang: Target language for translation.
    :return: List of elements processed from the file.
    """
    

    import unstructured_client
    from unstructured_client.models import operations, shared

    client = unstructured_client.UnstructuredClient(
        api_key_auth=os.getenv("UNSTRUCTURED_API_KEY")
    )

    filename = file_path

    req = operations.PartitionRequest(
        partition_parameters=shared.PartitionParameters(
            files=shared.Files(
                content=open(filename, "rb"),
                file_name=filename,
            ),
            strategy=shared.Strategy.HI_RES,
            
        ),
    )

    try:
        res = client.general.partition(
            request=req
        )
        element_dicts = [element for element in res.elements]
        return element_dicts
        
    except Exception as e:
        print(e)