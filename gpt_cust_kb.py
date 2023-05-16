from llama_index import download_loader, SimpleDirectoryReader, ServiceContext, LLMPredictor, GPTVectorStoreIndex, PromptHelper, StorageContext, load_index_from_storage
from pathlib import Path
import openai
import os
from langchain import OpenAI
import streamlit as st
from streamlit_chat import message
import time
from langchain.chat_models import ChatOpenAI


key = os.getenv("OPENAI_API_KEY")
os.environ['OPENAI_API_KEY'] = key
llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"))
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

#build index from PDF
def pdf_to_index(pdf_path, save_path):
    PDFReader = download_loader('PDFReader')
    loader = PDFReader()
    documents = loader.load_data(file=Path(pdf_path))
    index = GPTVectorStoreIndex.from_documents(documents)
    # index.save_to_disk(save_path)
    index.storage_context.persist(persist_dir=save_path)
    print('saved to disk')


#query index using GPT
def query_index(index_path, query_u):
    # index = GPTVectorStoreIndex.load_from_disk(index_path, service_context=service_context)
    PATH = 'C/gpt_indexes'
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir=f"{PATH}/test.json")

    # load index
    index = load_index_from_storage(storage_context, service_context=service_context)
    query_engine = index.as_query_engine()
    response = query_engine.query(query_u)
    # response=index.query(query_u)
    st.session_state.past.append(query_u)
    st.session_state.generated.append(response.response)   


def clear_convo():
    st.session_state['past'] = []
    st.session_state['generated'] = []

def save_pdf(file):
    PATH = 'C/gpt_indexes'
    if not os.path.exists(PATH):
        os.makedirs(PATH)
        pdf_to_index(pdf_path='C:/'+file, save_path=f'{PATH}/{file}')
        print('saving index')


def get_manual():
    manual_names = []
    manual = st.sidebar. radio("Choose a manual:", ("Yukon Test PDF", "LLM Research"))
    if manual== "Yukon Test":
        return f"./{name_of_pdf}.json"

def init():
    st.set_page_config(page_title='PDF ChatBot', page_icon=':robot_face: ') 
    st.sidebar.title('Available manuals')



if __name__ == '__main__':
    
    clear_button = st.sidebar.button("Clear Conversation", key="clear") 
    if clear_button:
        clear_convo()

    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    if 'manual' not in st.session_state:
        st.session_state['manual'] = []

    with st.form(key='my_form', clear_on_submit=True):
        user_input= st.text_area("You:", key="input", height=75) 
        submit_button =st.form_submit_button(label="Submit")

    if user_input and submit_button:
        query_index(index_path='./test_chat.json',query_u=user_input)

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1, -1, -1): 
            message(st.session_state['generated'][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + "user")
    
    st.sidebar.radio("Choose a manual:", ("Yukon Test PDF", "LLM Research"))
    file = st.file_uploader("Choose a PDF file to index...")
    save_pdf(file.name)
    