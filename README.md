# RAG from scratch w/ Vertex AI

> These code examples demonstrate how to implement a RAG workflow using Vertex managed services (e.g., Vector Search, Batch Prediction), as well as APIs from the GenAI stack (e.g., Gemini, Embeddings for Text, Grounding, Ranking). Additionally, we use [Document AI](https://cloud.google.com/document-ai/?hl=en) to organize, annotate, and chunk our documents 

## Key highlights

1. the RAG is *grounded*, meaning the LLM's output is tethered to specific, verifiable sources of information. This service supports grounding with my proprietary data, as well as Google Search (see [Grounding API](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/overview) for details)
2. Document AI's [Layout Parser](https://cloud.google.com/document-ai/docs/layout-parse-chunk) is specifically designed for creating chunks of desired sizes while also maintaining location information from a documents hierarchy: `title > chapter > section > ... headings`
3. the [Ranking API](https://cloud.google.com/generative-ai-app-builder/docs/ranking) reranks a list of candidate documents based on their relevancy to a corresponding query. This contrasts embedding retreival which look only at the semantic similarity of query and candidate pairs
4. [Vertex AI Vector Search](https://cloud.google.com/vertex-ai/docs/vector-search/overview) is the vector database of choice. This service maintains high QPS and retreival recall as it scales to billions of vectors. It also supports filtering and enforcing diversity at query time


<details>
  <summary>How does RAG work?</summary>
    
<img src='imgs/joe_dirte_logic.png' width='924' height='500'>
    
</details>


# Using this Repo


#### Setup instructions

<details>
  <summary>Install Vertex AI SDK and Other Packages</summary>

Run the following in a terminal:

```
pip install google-cloud-aiplatform --upgrade --quiet
pip install google-cloud-discoveryengine --upgrade --quiet
pip install google-cloud-documentai google-cloud-documentai-toolbox --upgrade --quiet
pip install google-cloud-storage --upgrade --quiet
pip install langchain-google-community --upgrade --quiet
pip install langchain-google-vertexai --upgrade --quiet
pip install langchain-google-community[vertexaisearch] --upgrade --quiet
pip install langchain-google-community[docai] --upgrade --quiet
pip install rich --upgrade --quiet
```

</details>

<details>
  <summary>Google Cloud IAM permissions</summary>

* `roles/serviceusage.serviceUsageAdmin` to enable APIs
* `roles/iam.serviceAccountAdmin` to modify service agent permissions
* `roles/aiplatform.user` to use AI Platform components
* `roles/storage.objectAdmin` to modify and delete GCS buckets
* `roles/documentai.admin` to create and use Document AI Processors
* `roles/discoveryengine.admin` to modify Vertex AI Search assets
    
</details>

### Random tips

run this command in terminal from root to clear `__pycache__` files:

> `find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf`

---

<img src='imgs/deep_retrievers.png' width='1015' height='275'>