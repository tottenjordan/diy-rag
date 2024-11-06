import logging
from typing import TYPE_CHECKING, Iterator, List, Optional, Sequence
from langchain_community.document_loaders.base import BaseLoader
from langchain_community.document_loaders.gcs_directory import GCSDirectoryLoader
from langchain_community.document_loaders.gcs_file import GCSFileLoader
from langchain_community.utilities.vertexai import get_client_info
from langchain_core.document_loaders import BaseBlobParser
from langchain_core.document_loaders.blob_loaders import Blob
from langchain_core.documents import Document
import re

logger = logging.getLogger(__name__)


class CustomGCSDirectoryLoader(GCSDirectoryLoader, BaseLoader):
    def load(self, file_pattern=None) -> List[Document]:
        """Load documents."""
        try:
            from google.cloud import storage
        except ImportError:
            raise ImportError(
                "Could not import google-cloud-storage python package. "
                "Please install it with `pip install google-cloud-storage`."
            )
        client = storage.Client(
            project=self.project_name,
            client_info=get_client_info(module="google-cloud-storage"),
        )
        
        regex = None
        if file_pattern:
            regex = re.compile(r'{}'.format(file_pattern))

        docs = []
        for blob in client.list_blobs(self.bucket, prefix=self.prefix):
            # we shall just skip directories since GCSFileLoader creates
            # intermediate directories on the fly
            if blob.name.endswith("/"):
                continue
            if regex and not regex.match(blob.name):
                continue
            # Use the try-except block here
            try:
                logger.info(f"Processing {blob.name}")
                temp_blob = Blob(path=f"gs://{blob.bucket.name}/{blob.name}")
                docs.append(temp_blob)
            except Exception as e:
                if self.continue_on_failure:
                    logger.warning(f"Problem processing blob {blob.name}, message: {e}")
                    continue
                else:
                    raise e
        return docs