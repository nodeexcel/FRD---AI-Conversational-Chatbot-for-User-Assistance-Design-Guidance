#!/usr/bin/env python3
"""Test script for RAG with ChromaDB."""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_rag():
    """Test RAG agent with ChromaDB."""
    from app.agents.knowledge.vector_store import VectorStore
    from app.agents.knowledge.rag_agent import RAGAgent
    from app.config import settings

    print("=" * 60)
    print("RAG + ChromaDB Integration Test")
    print("=" * 60)

    # Test 1: Direct ChromaDB connection
    print("\n[TEST 1] Connecting to ChromaDB...")
    vs = VectorStore(host=settings.chromadb_host, port=settings.chromadb_port)
    
    try:
        await vs.initialize()
        print(f"✓ ChromaDB connected at {settings.chromadb_host}:{settings.chromadb_port}")
        
        # Check heartbeat
        if vs.client:
            heartbeat = await vs.client.heartbeat()
            print(f"✓ ChromaDB heartbeat: {'OK' if heartbeat else 'FAILED'}")
            
            # List collections
            collections = await vs.client.list_collections()
            print(f"✓ Existing collections: {collections}")
            
            # Get collection info
            collection = await vs.client.get_or_create_collection(
                name="dress_products",
                metadata={"description": "Dress product knowledge base"}
            )
            print(f"✓ Collection 'dress_products' ready")
            print(f"  - Collection ID: {collection.get('id', 'N/A')[:8]}...")
            
    except Exception as e:
        print(f"✗ ChromaDB connection failed: {e}")
        return False

    # Test 2: Initialize RAG Agent
    print("\n[TEST 2] Initializing RAG Agent...")
    try:
        rag = RAGAgent()
        await rag.initialize()
        print("✓ RAG Agent initialized")
        
        # Check document count
        count = await rag.vector_store.count()
        print(f"✓ Vector store document count: {count}")
        
    except Exception as e:
        print(f"✗ RAG Agent initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 3: Search test
    print("\n[TEST 3] Testing search...")
    try:
        results = await rag.vector_store.search(
            query="blue cotton summer dress",
            n_results=5
        )
        print(f"✓ Search returned {results.total_count} results")
        
        for i, (doc, dist) in enumerate(zip(results.documents, results.distances)):
            similarity = 1.0 - dist if dist <= 1.0 else 0.0
            print(f"  [{i+1}] {doc.metadata.get('name', doc.id)} (similarity: {similarity:.3f})")
            
    except Exception as e:
        print(f"✗ Search failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 4: Full RAG process
    print("\n[TEST 4] Testing full RAG process...")
    try:
        result = await rag.process({
            "query": "Show me blue dresses for summer",
            "filters": {}
        })
        print(f"✓ RAG process completed")
        print(f"  - Success: {result['success']}")
        print(f"  - Retrieved: {result['retrieved_count']} products")
        print(f"  - Sources: {result.get('sources', [])}")
        if result['success']:
            response = result['response'][:200] + "..." if len(result['response']) > 200 else result['response']
            print(f"  - Response: {response}")
        else:
            # If no OpenAI key, that's expected
            if "API key" in str(result.get('response', '')):
                print(f"  - Note: OpenAI API key required for full response generation")
        
    except Exception as e:
        print(f"✗ RAG process failed: {e}")
        import traceback
        traceback.print_exc()

    # Cleanup
    print("\n[Cleanup]")
    await rag.close()
    print("✓ Resources cleaned up")

    print("\n" + "=" * 60)
    print("RAG + ChromaDB Test Complete")
    print("=" * 60)
    return True


if __name__ == "__main__":
    print("Starting RAG + ChromaDB test...")
    success = asyncio.run(test_rag())
    sys.exit(0 if success else 1)
