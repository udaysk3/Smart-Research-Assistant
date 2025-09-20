import chromadb
import os
from typing import List, Dict, Any
import uuid
import numpy as np

class VectorStore:
    def __init__(self):
        # Initialize ChromaDB with new API
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="research_documents"
        )
    
    async def add_document(self, doc_data: Dict[str, Any], user_id: str):
        """Add a processed document to the vector store"""
        try:
            pages = doc_data.get("pages", [])
            if not pages:
                return
            
            # Prepare data for ChromaDB
            ids = []
            documents = []
            metadatas = []
            
            for i, page in enumerate(pages):
                page_id = f"{user_id}_{doc_data['filename']}_page_{i}"
                ids.append(page_id)
                documents.append(page.get("content", ""))
                metadatas.append({
                    "user_id": user_id,
                    "filename": doc_data["filename"],
                    "page_number": i,
                    "source": doc_data["filename"],
                    "document_type": doc_data.get("type", "unknown")
                })
                print(documents)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            print(f"Added {len(pages)} pages from {doc_data['filename']} to vector store")
            
        except Exception as e:
            print(f"Error adding document to vector store: {e}")
            raise
    
    async def search(self, query: str, user_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents based on query"""
        try:
            # Search in ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where={"user_id": user_id}  # Filter by user
            )
            
            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "content": doc,
                        "source": results["metadatas"][0][i].get("source", "Unknown"),
                        "page_number": results["metadatas"][0][i].get("page_number", 0),
                        "similarity": results["distances"][0][i] if results["distances"] else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []
    
    async def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a specific user"""
        try:
            results = self.collection.get(
                where={"user_id": user_id}
            )
            
            # Group by filename
            documents = {}
            if results["metadatas"]:
                for i, metadata in enumerate(results["metadatas"]):
                    filename = metadata.get("filename", "Unknown")
                    if filename not in documents:
                        documents[filename] = {
                            "filename": filename,
                            "pages": 0,
                            "type": metadata.get("document_type", "unknown")
                        }
                    documents[filename]["pages"] += 1
            
            return list(documents.values())
            
        except Exception as e:
            print(f"Error getting user documents: {e}")
            return []
    
    async def delete_user_documents(self, user_id: str):
        """Delete all documents for a specific user"""
        try:
            # Get all document IDs for the user
            results = self.collection.get(
                where={"user_id": user_id}
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                print(f"Deleted {len(results['ids'])} documents for user {user_id}")
            
        except Exception as e:
            print(f"Error deleting user documents: {e}")
            raise

