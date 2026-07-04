# RAG Knowledge Intelligence Layer

The `KnowledgeService` RAG framework ingests enterprise standard operating procedures, guidelines, compliance files, and contracts.

It slices text content into indexable chunks, generates deterministic vector embeddings, and executes cosine similarity searches.

## Architecture

```mermaid
flowchart TD
    Doc[Source Document] --> Load[DocumentLoader]
    Load --> Chunk[ChunkManager: Sliding Win]
    Chunk --> Embed[EmbeddingGenerator: Hash seeds]
    Embed --> Store[(InMemoryVectorStore)]
    
    Query[Text Search query] --> Store
    Store -->|Cosine Similarity| Retriever[RankingEngine]
    Retriever --> Output[RetrievalResult]
```

## Retrieval Output Format
Query matches return:
- **`relevant_chunks`**: Matched slices of raw texts.
- **`metadata`**: Origin filename, type, and creation date.
- **`confidence` & `similarity_score`**: Normalized cosine coefficients.
