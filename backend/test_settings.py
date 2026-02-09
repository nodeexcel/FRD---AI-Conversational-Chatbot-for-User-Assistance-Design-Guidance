#!/usr/bin/env python3
"""Quick test to verify ChromaDB settings."""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force reload settings
import importlib
import app.config
importlib.reload(app.config)

from app.config import Settings, get_settings

print("=" * 60)
print("Testing ChromaDB Settings")
print("=" * 60)

# Test 1: Load settings
print("\n[Test 1] Loading settings...")
settings = get_settings()
print(f"✓ Settings loaded")

# Test 2: Check VectorStoreConfig
print(f"\n[Test 2] VectorStoreConfig:")
print(f"  - type: {settings.vector_store.type}")
print(f"  - host: {settings.vector_store.host}")
print(f"  - port: {settings.vector_store.port}")
print(f"  - persist_directory: {settings.vector_store.persist_directory}")
print(f"  - collection_name: {settings.vector_store.collection_name}")
print(f"  - url: {settings.vector_store.url}")

# Test 3: Check direct properties
print(f"\n[Test 3] Direct properties:")
print(f"  - chromadb_host: {settings.chromadb_host}")
print(f"  - chromadb_port: {settings.chromadb_port}")
print(f"  - chromadb_url: {settings.chromadb_url}")
print(f"  - chromadb_collection: {settings.chromadb_collection}")

print("\n" + "=" * 60)
print("Settings Test Complete")
print("=" * 60)
