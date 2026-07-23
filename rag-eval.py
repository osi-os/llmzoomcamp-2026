# %%
import pandas as pd

df_ground_truth = pd.read_csv("data/ground_truth-new.csv")
ground_truth = df_ground_truth.to_dict(orient="records")

# %%
from ingest import load_faq_data, build_index

documents = load_faq_data()

documents_llm = []

for doc in documents:
    if doc["course"] == "llm-zoomcamp":
        documents_llm.append(doc)

documents = documents_llm
index = build_index(documents)

# %%
ground_truth[10]

# %%
doc_idx = {}

for doc in documents:
    doc_idx[doc["id"]] = doc

# %%
doc_idx

# %%
q = ground_truth[10]
q

# %%
doc_idx[q['document']]

# %%
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('llm.env')
openai_client = OpenAI()

# %%
from evaluation_utils import RAGWithUsage

assistant = RAGWithUsage(
    index=index,
    llm_client=openai_client,
)

# %%
rec = ground_truth[0]
question = rec["question"]

answer_llm = assistant.rag(question)
answer_llm

# %%
assistant.total_cost()

# %%
doc_id = rec["document"]
original_doc = doc_idx[doc_id]
answer_orig = original_doc["answer"]

answer_orig

# %%
rag_result = {
    "question": question,
    "answer_llm": answer_llm,
    "answer_orig": answer_orig,
    "document": doc_id,
}

rag_result

# %%
def generate_rag_answer(rec):
    question = rec["question"]
    doc_id = rec["document"]
    original_doc = doc_idx[doc_id]

    answer_llm = assistant.rag(question)
    answer_orig = original_doc["answer"]

    result = {
        "question": question,
        "answer_llm": answer_llm,
        "answer_orig": answer_orig,
        "document": doc_id,
    }

    return result

# %%
answer_record = generate_rag_answer(ground_truth[0])
answer_record

# %%
assistant.reset_usage()

# %%
from concurrent.futures import ThreadPoolExecutor
from evaluation_utils import map_progress

# %%
print('c6c2888275' in doc_idx)


