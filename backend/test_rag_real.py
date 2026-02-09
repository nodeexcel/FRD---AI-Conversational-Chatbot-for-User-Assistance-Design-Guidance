"""Test RAG with real PostgreSQL data."""
import asyncio
import sys
sys.path.insert(0, '.')

from app.agents.knowledge.rag_agent import knowledge_agent


async def test_rag_real():
    """Test RAG loading real products from PostgreSQL."""
    print("Testing RAG with real PostgreSQL data...")
    
    try:
        # Initialize RAG agent
        await knowledge_agent.initialize()
        
        print(f"✅ RAG initialized")
        print(f"📊 Document count: {knowledge_agent.document_count}")
        print(f"📊 Data source: {'PostgreSQL' if knowledge_agent.pool else 'Sample/Fallback'}")
        
        # Test a query
        results = await knowledge_agent.query("summer dresses")
        print(f"\n✅ Query returned {results['total_results']} results")
        print(f"Answer: {results['answer'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_rag_real())
    sys.exit(0 if success else 1)
