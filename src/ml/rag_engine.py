from src.data.models import LegalChunk
from qdrant_client import QdrantClient

class LegalRAG:
    def __init__(self, db_session, qdrant_client: QdrantClient, embedder, llm):
        self.db = db_session
        self.qdrant = qdrant_client
        self.embedder = embedder
        self.llm = llm

    def search_and_answer(self, query: str):
        # 1. Vector Search
        query_vector = self.embedder.encode(query)
        hits = self.qdrant.search(
            collection_name="bangla_legal",
            query_vector=query_vector,
            limit=3
        )
        
        # 2. Graph Expansion
        related_sections = set()
        context_texts = []
        
        for hit in hits:
            # Add the direct vector hit
            payload = hit.payload or {}
            if 'text' in payload:
                context_texts.append(payload['text'])
            
            # Extract hierarchy tags (nodes)
            if 'hierarchy' in payload and payload['hierarchy']:
                for section in payload['hierarchy']:
                    related_sections.add(section)

        # 3. SQL Graph Query
        if related_sections:
            # PG Array overlap query
            # SQLAlchemy: LegalChunk.hierarchy.overlap(list)
            # We need to make sure the dialect supports it or use correct syntax
            # For simplicity in this scaffold, we'll try basic approach or assume postgres
            graph_hits = self.db.query(LegalChunk).filter(
                LegalChunk.hierarchy.overlap(list(related_sections))
            ).limit(5).all()
            
            for chunk in graph_hits:
                context_texts.append(chunk.content)
        
        # 4. Generate Answer
        final_context = "\n---\n".join(list(set(context_texts)))
        return self.llm.generate_response(final_context, query)
