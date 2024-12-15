import pandas as pd
import torch
from transformers import BertTokenizer, BertModel
from tqdm import tqdm
import numpy as np

# CSV 파일 불러오기
file_path = '/Users/baehanjun/PycharmProjects/PythonProject/Bitamin/Project/24_2/final.csv'
data = pd.read_csv(file_path)

# 임베딩할 텍스트 열과 라벨 열 이름 설정
text_column = 'paragraph_txt'
label_columns = ['essay_scoreT_exp_avg', 'essay_scoreT_org_avg', 'essay_scoreT_cont_avg', 'paragraph_scoreT_avg']

# BERT 모델 및 토크나이저 로드
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# 맥북용 GPU 가속화
device = torch.device("mps")
model.to(device)

model.eval()
batch_size = 16

# 임베딩 생성 함수 정의
def get_embedding(texts):
    inputs = tokenizer(texts, return_tensors='pt', truncation=True, padding=True, max_length=512)
    inputs = {key: value.to(device) for key, value in inputs.items()} 
    with torch.no_grad():
        outputs = model(**inputs)
    cls_embeddings = outputs.last_hidden_state[:, 0, :]
    return cls_embeddings.squeeze().cpu().numpy() 

# 텍스트 임베딩을 배치 단위로 생성
embeddings = []
for i in tqdm(range(0, len(data), batch_size)):
    batch_texts = data[text_column].iloc[i:i+batch_size].fillna('')  
    batch_embeddings = get_embedding(batch_texts.tolist()) 
    embeddings.extend(batch_embeddings)  
    del batch_embeddings  

embeddings_array = np.array(embeddings)

labels_array = data[label_columns].values

embedding_output_path = '/Users/baehanjun/PycharmProjects/PythonProject/Bitamin/Project/24_2/paragraph_embeddings.npy'
label_output_path = '/Users/baehanjun/PycharmProjects/PythonProject/Bitamin/Project/24_2/paragraph_labels.npy'

np.save(embedding_output_path, embeddings_array)
np.save(label_output_path, labels_array)