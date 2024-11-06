"""Utility functions to create Vector Search resources

"""
import hashlib
import uuid

from typing import TYPE_CHECKING, Iterator, List, Optional, Sequence
from google.cloud import storage
from google.cloud import aiplatform
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from google.cloud.aiplatform import MatchingEngineIndex, MatchingEngineIndexEndpoint


def create_uuid(name: str) -> str:
    hex_string = hashlib.md5(name.encode("UTF-8")).hexdigest()
    return str(uuid.UUID(hex=hex_string))


def create_bucket(bucket_name: str, create_resources: bool) -> storage.Bucket:
    # create Cloud Storage bucket if does not exists
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    if bucket.exists():
        print(f"Bucket {bucket.name} exists")
        return bucket

    if not create_resources:
        return bucket

    bucket = storage_client.create_bucket(bucket_name)
    print(f"Bucket {bucket.name} created")
    return bucket


def create_index(
    project_id: str,
    region: str,
    sync_job: bool,
    create_resources: bool, 
    vs_index_name: str,
    vs_dimensions: int,
    vs_approx_neghbors: int,
    distance_measure_type: str,
    vs_leaf_node_emb_count: int,
    vs_leaf_search_percent: int,
    vs_description: str,
    vs_index_shard_size: str,
    vs_index_update_method: str,
) -> Optional[MatchingEngineIndex]:
    index_names = [
        index.resource_name
        for index in MatchingEngineIndex.list(filter=f"display_name={vs_index_name}")
    ]

    if len(index_names) > 0:
        vs_index = MatchingEngineIndex(index_name=index_names[0])
        print(
            f"Vector Search index {vs_index.display_name} exists with resource name {vs_index.resource_name}"
        )
        return vs_index

    if not create_resources:
        print(
            f"CREATE_RESOURCES flag set to {create_resources}. Skip creating resources"
        )
        return None

    print(f"Creating Vector Search index {vs_index_name} ...")
    vs_index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
        display_name=vs_index_name,
        dimensions=vs_dimensions,
        approximate_neighbors_count=vs_approx_neghbors,
        distance_measure_type=distance_measure_type,
        leaf_node_embedding_count=vs_leaf_node_emb_count,
        leaf_nodes_to_search_percent=vs_leaf_search_percent,
        description=vs_description,
        shard_size=vs_index_shard_size,
        index_update_method=vs_index_update_method,
        project=project_id,
        location=region,
        sync=sync_job
    )
    print(
        f"Vector Search index {vs_index.display_name} created with resource name {vs_index.resource_name}"
    )
    return vs_index


def create_index_endpoint(
    project_id: str,
    region: str,
    sync_job: bool,
    create_resources: bool, 
    vs_index_endpoint_name: str,
    vs_description: str,
) -> Optional[MatchingEngineIndexEndpoint]:
    endpoint_names = [
        endpoint.resource_name
        for endpoint in MatchingEngineIndexEndpoint.list(
            filter=f"display_name={vs_index_endpoint_name}"
        )
    ]

    if len(endpoint_names) > 0:
        vs_endpoint = MatchingEngineIndexEndpoint(index_endpoint_name=endpoint_names[0])
        print(
            f"Vector Search index endpoint {vs_endpoint.display_name} exists with resource name {vs_endpoint.resource_name}"
        )
        return vs_endpoint

    if not create_resources:
        print(
            f"CREATE_RESOURCES flag set to {create_resources}. Skip creating resources"
        )
        return None

    print(f"Creating Vector Search index endpoint {vs_index_endpoint_name} ...")
    vs_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
        display_name=vs_index_endpoint_name,
        public_endpoint_enabled=True,
        description=vs_description,
        project=project_id,
        location=region,
        sync=sync_job
    )
    print(
        f"Vector Search index endpoint {vs_endpoint.display_name} created with resource name {vs_endpoint.resource_name}"
    )
    return vs_endpoint


def deploy_index(
    index: MatchingEngineIndex, 
    endpoint: MatchingEngineIndexEndpoint,
    create_resources: bool,
    vs_index_name: str,
    vs_machine_type: str,
    vs_min_replicas: int,
    vs_max_replicas: int,
) -> Optional[MatchingEngineIndexEndpoint]:
    index_endpoints = [
        (deployed_index.index_endpoint, deployed_index.deployed_index_id)
        for deployed_index in index.deployed_indexes
    ]

    if len(index_endpoints) > 0:
        vs_deployed_index = MatchingEngineIndexEndpoint(
            index_endpoint_name=index_endpoints[0][0]
        )
        print(
            f"Vector Search index {index.display_name} is already deployed at endpoint {vs_deployed_index.display_name}"
        )
        return vs_deployed_index

    if not create_resources:
        print(
            f"CREATE_RESOURCES flag set to {create_resources}. Skip creating resources"
        )
        return None

    print(
        f"Deploying Vector Search index {index.display_name} at endpoint {endpoint.display_name} ..."
    )
    deployed_index_id = (
        f'{vs_index_name}_{create_uuid(vs_index_name).split("-")[-1]}'.replace("-", "_")
    )
    vs_deployed_index = endpoint.deploy_index(
        index=index,
        deployed_index_id=deployed_index_id,
        display_name=vs_index_name,
        machine_type=vs_machine_type,
        min_replica_count=vs_min_replicas,
        max_replica_count=vs_max_replicas,
    )
    print(
        f"Vector Search index {index.display_name} is deployed at endpoint {vs_deployed_index.display_name}"
    )
    return vs_deployed_index


def create_docai_processor(
    project_id: str,
    region: str,
    create_resources: bool,
    docai_location: str="us",
    processor_display_name: str="diydocai-v1",
    processor_type: str="LAYOUT_PARSER_PROCESSOR",
    processor_version: str="pretrained-layout-parser-v1.0-2024-06-03",
) -> Optional[documentai.Processor]:
    
    # Set the api_endpoint if you use a location other than 'us'
    opts = ClientOptions(api_endpoint=f"{docai_location}-documentai.googleapis.com")
    docai_client = documentai.DocumentProcessorServiceClient(client_options=opts)
    parent = docai_client.common_location_path(project_id, docai_location)
    
    # Check if processor exists
    processor_list = docai_client.list_processors(parent=parent)
    processors = [
        processor.name
        for processor in processor_list
        if (
            processor.display_name == processor_display_name
            and processor.type_ == processor_type
        )
    ]

    if len(processors) > 0:
        docai_processor = docai_client.get_processor(name=processors[0])
        print(
            f"Document AI processor {docai_processor.display_name} is already created"
        )
        return docai_processor

    if not create_resources:
        print(
            f"CREATE_RESOURCES flag set to {create_resources}. Skip creating resources"
        )
        return None

    # Create a processor
    print(
        f"Creating Document AI processor {processor_display_name} of type {processor_type} ..."
    )
    docai_processor = docai_client.create_processor(
        parent=parent,
        processor=documentai.Processor(
            display_name=processor_display_name, 
            type_=processor_type, 
            default_processor_version=processor_version
        ),
    )
    print(
        f"Document AI processor {processor_display_name} of type {processor_type} is created."
    )
    return docai_processor