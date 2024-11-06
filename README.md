# RAG from scratch

Extending [this example](https://github.com/GoogleCloudPlatform/applied-ai-engineering-samples/blob/agents-api-notebooks/genai-on-vertex-ai/retrieval_augmented_generation/diy_rag_with_vertexai_apis/build_grounded_rag_app_with_vertex.ipynb)

### Setup instructions

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

## Random tips

* run this command in terminal from root to clear `__pycache__` files:

> `find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf`