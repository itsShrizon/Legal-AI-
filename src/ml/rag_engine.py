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
        # Use query_points for search (modern Qdrant API)
        hits = self.qdrant.query_points(
            collection_name="bangla_legal",
            query=query_vector,
            limit=5
        ).points
        
        # 2. Graph Expansion
        related_sections = set()
        context_texts = []
        sources = set()
        
        for hit in hits:
            # Add the direct vector hit
            payload = hit.payload or {}
            if 'text' in payload:
                source = payload.get('source_file', 'Unknown')
                context_texts.append(f"Source: {source}\nContent: {payload['text']}")
            
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
                LegalChunk.hierarchy.op("&&")(list(related_sections))
            ).limit(5).all()
            
            for chunk in graph_hits:
                # Access filename via relationship (lazy load might trigger here, implicit join preferred for perf but ok for now)
                source = chunk.document.filename if chunk.document else "Unknown"
                context_texts.append(f"Source: {source}\nContent: {chunk.content}")
        
        # 4. Generate Answer
        print("\n" + "="*50)
        print(f"🔍 RETRIEVAL DEBUG INFO for query: '{query}'")
        print("="*50)
        
        unique_contexts = list(set(context_texts))
        for i, ctx in enumerate(unique_contexts):
            # context text format: "Source: ...\nContent: ..."
            lines = ctx.split('\n')
            source_line = lines[0] if lines else "Unknown Source"
            content_snippet = lines[1][:100] + "..." if len(lines) > 1 else "No content"
            print(f"[{i+1}] {source_line} | Snippet: {content_snippet}")
            
        print("="*50 + "\n")

        final_context = "\n\n".join(unique_contexts)
        return self.llm.generate_response(final_context, query)
