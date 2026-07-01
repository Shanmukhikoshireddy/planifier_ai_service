from datetime import datetime

from app.repository.base_repository import BaseRepository


class EmbeddingRepository(BaseRepository):

    def __init__(self):

        super().__init__()

        self.collection = self.db[
            "embeddings"
        ]

    # =====================================================
    # Save Embedding
    # =====================================================

    def save_embedding(

        self,

        resume_id: str,

        upload_job_id: str,

        embedding: list,

        embedding_model: str,

        dimension: int,

    ):

        document = {

            "resume_id": resume_id,

            "upload_job_id": upload_job_id,

            "embedding": embedding,

            "embedding_model": embedding_model,

            "dimension": dimension,

            "created_at": datetime.utcnow(),

        }

        self.collection.insert_one(

            document

        )

    # =====================================================
    # Get Embedding
    # =====================================================

    def get_embedding(

        self,

        resume_id: str,

    ):

        return self.collection.find_one(

            {

                "resume_id": resume_id

            },

            {

                "_id": 0

            }

        )

    # =====================================================
    # Delete Embedding
    # =====================================================

    def delete_embedding(

        self,

        resume_id: str,

    ):

        self.collection.delete_one(

            {

                "resume_id": resume_id

            }

        )

    # =====================================================
    # Vector Search
    # =====================================================

    def search_similar_embeddings(

        self,

        embedding: list,

        top_n: int = 100,

    ):

        pipeline = [

            {

                "$vectorSearch": {

                    "index": "resume_vector_index",

                    "path": "embedding",

                    "queryVector": embedding,

                    "numCandidates": top_n * 5,

                    "limit": top_n,

                }

            },

            {

                "$project": {

                    "_id": 0,

                    "resume_id": 1,

                    "upload_job_id": 1,

                    "embedding_score": {

                        "$meta": "vectorSearchScore"

                    }

                }

            }

        ]

        return list(

            self.collection.aggregate(

                pipeline

            )

        )

    # =====================================================
    # Count Embeddings
    # =====================================================

    def count_embeddings(

        self,

    ):

        return self.collection.count_documents(

            {}

        )

    # =====================================================
    # Delete All Embeddings
    # =====================================================

    def delete_all_embeddings(

        self,

    ):

        self.collection.delete_many(

            {}

        )