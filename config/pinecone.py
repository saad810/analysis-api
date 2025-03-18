from pinecone import (
    Pinecone,
    ServerlessSpec,
    CloudProvider,
    AwsRegion,
    VectorType
)
import os
from dotenv import load_dotenv

load_dotenv()
# 1. Instantiate the Pinecone client
pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

# 2. Create an index (if not exists)
index_name = "education-index"

if index_name not in [idx["name"] for idx in pc.list_indexes()]:
    index_config = pc.create_index(
        name=index_name,
        dimension=1536,  # Must match OpenAI embedding dimension
        spec=ServerlessSpec(
            cloud=CloudProvider.AWS,
            region=AwsRegion.US_EAST_1
        ),
        vector_type=VectorType.DENSE
    )

# 3. Instantiate Index Client
idx = pc.Index(index_name)  # ✅ Use index name directly, no need for `host`
