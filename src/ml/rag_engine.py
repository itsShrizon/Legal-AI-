from src.data.models import LegalChunk, LegalDocument
from sqlalchemy import or_
from qdrant_client import QdrantClient

class LegalRAG:
    def __init__(self, db_session, qdrant_client: QdrantClient, embedder, llm):
        self.db = db_session
        self.qdrant = qdrant_client
        self.embedder = embedder
        self.llm = llm

    def _vector_search(self, query: str, limit: int = 10):
        """Returns list of dicts: {'content': str, 'source': str, 'score': float, 'payload': dict}"""
        query_vector = self.embedder.encode(query)
        hits = self.qdrant.query_points(
            collection_name="bangla_legal",
            query=query_vector,
            limit=limit
        ).points
        
        results = []
        for hit in hits:
            payload = hit.payload or {}
            source = payload.get('source_file', 'Unknown')
            content = payload.get('text', '')
            results.append({
                'content': content,
                'source': source,
                'score': hit.score,
                'payload': payload,
                'id': payload.get('chunk_id') # critical for dedup
            })
        return results

    def _keyword_search(self, query: str, limit: int = 10):
        """Sparse search using SQL ILIKE"""
        # 1. Try phrase match first (High precision)
        results = self.db.query(LegalChunk).join(LegalDocument).filter(
            LegalChunk.content.ilike(f"%{query}%")
        ).limit(limit).all()
        
        # 2. If not enough, try word match (High recall)
        if len(results) < limit:
            words = [w for w in query.split() if len(w) > 4] # Filter stopwords roughly
            if words:
                conditions = [LegalChunk.content.ilike(f"%{w}%") for w in words]
                more_results = self.db.query(LegalChunk).join(LegalDocument).filter(
                    or_(*conditions)
                ).limit(limit).all()
                
                # Merge uniqueness
                existing_ids = {r.id for r in results}
                for r in more_results:
                    if r.id not in existing_ids:
                        results.append(r)
        
        # Format
        formatted = []
        for r in results[:limit]:
            source = r.document.filename if r.document else "Unknown"
            formatted.append({
                'content': r.content,
                'source': source,
                'score': 1.0, # Keyword matches don't have granularity in ILIKE without TSVector
                'payload': {'chunk_id': r.chunk_id, 'hierarchy': r.hierarchy, 'source_file': source, 'text': r.content},
                'id': r.chunk_id
            })
        return formatted

    def hybrid_search(self, query: str, k: int = 60):
        """Reciprocal Rank Fusion (RRF)"""
        limit = 10
        vec_results = self._vector_search(query, limit)
        kw_results = self._keyword_search(query, limit)
        
        # Map: chunk_id -> score
        rrf_score = {}
        
        # 1. Process Vector Ranks
        for rank, res in enumerate(vec_results):
            cid = res['id']
            if cid not in rrf_score:
                rrf_score[cid] = {'data': res, 'score': 0}
            rrf_score[cid]['score'] += 1 / (k + rank + 1)
            
        # 2. Process Keyword Ranks
        for rank, res in enumerate(kw_results):
            cid = res['id']
            if cid not in rrf_score:
                rrf_score[cid] = {'data': res, 'score': 0}
            rrf_score[cid]['score'] += 1 / (k + rank + 1)
        
        # Sort by RRF score
        sorted_docs = sorted(rrf_score.values(), key=lambda x: x['score'], reverse=True)
        
        return [item['data'] for item in sorted_docs[:5]] # Top 5 fused

    def search_and_answer(self, query: str):
        # 1. Hybrid Retrieval
        hits = self.hybrid_search(query)
        
        # 2. Graph Expansion
        related_sections = set()
        context_texts = []
        sources = set()
        
        for hit in hits:
            # Add the direct hit
            payload = hit['payload']
            source = payload.get('source_file', 'Unknown')
            context_texts.append(f"Source: {source}\nContent: {payload['text']}")
            
            # Extract hierarchy tags (nodes)
            if 'hierarchy' in payload and payload['hierarchy']:
                val = payload['hierarchy']
                # Sometimes it's a string in SQL/Postgres return, list in Qdrant
                if isinstance(val, list):
                     for section in val: related_sections.add(section)
                elif isinstance(val, str):
                     # naive parse if needed or just skip
                     pass

        # 3. SQL Graph Query
        if related_sections:
            graph_hits = self.db.query(LegalChunk).filter(
                LegalChunk.hierarchy.op("&&")(list(related_sections))
            ).limit(5).all()
            
            for chunk in graph_hits:
                source = chunk.document.filename if chunk.document else "Unknown"
                context_texts.append(f"Source: {source}\nContent: {chunk.content}")
        
        # 4. Generate Answer
        print("\n" + "="*50)
        print(f"🔍 HYBRID RETRIEVAL DEBUG INFO for query: '{query}'")
        print("="*50)
        
        unique_contexts = list(set(context_texts))
        for i, ctx in enumerate(unique_contexts):
            lines = ctx.split('\n')
            source_line = lines[0] if lines else "Unknown Source"
            content_snippet = lines[1][:100] + "..." if len(lines) > 1 else "No content"
            print(f"[{i+1}] {source_line} | Snippet: {content_snippet}")
            
        print("="*50 + "\n")

        final_context = "\n\n".join(unique_contexts)
        return self.llm.generate_response(final_context, query)
