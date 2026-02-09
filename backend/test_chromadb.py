"""Test ChromaDB connection and functionality."""
import asyncio
import sys
sys.path.insert(0, '.')

from app.agents.knowledge.vector_store import vector_store, Document


async def test_chromadb():
    """Test ChromaDB connection and operations."""
    print("Testing ChromaDB connection...")
    
    try:
        # Initialize vector store
        await vector_store.initialize()
        print("✅ Connected to ChromaDB")
        
        # Check document count
        count = await vector_store.count()
        print(f"📊 Current document count: {count}")
        
        # Add test documents
        test_docs = [
            Document(
                id="test_001",
                content="Blue Cotton Summer Dress - A breezy summer dress made from organic cotton.",
                metadata={"title": "Blue Cotton Summer Dress", "color": "blue", "category": "summer_dress"}
            ),
            Document(
                id="test_002",
                content="Red Silk Evening Gown - Elegant floor-length evening gown made from pure silk.",
                metadata={"title": "Red Silk Evening Gown", "color": "red", "category": "evening_gown"}
            )
        ]
        
        await vector_store.add_documents(test_docs)
        print(f"✅ Added {len(test_docs)} test documents")
        
        # Search for documents
        results = await vector_store.search(query="summer dresses", n_results=5)
        print(f"✅ Search returned {results.total_count} results")
        
        for doc, distance in zip(results.documents, results.distances):
            print(f"  - {doc.metadata.get('title', 'Unknown')}: distance={distance:.4f}")
        
        # Final count
        count = await vector_store.count()
        print(f"📊 Final document count: {count}")
        
        # Close connection
        await vector_store.close()
        print("\n✅ ChromaDB test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_chromadb())
    sys.exit(0 if success else 1)
