"""
Retrieval-Augmented Generation (RAG) Pipeline
Question-answering system using document retrieval and LLM generation
"""

import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from openai import OpenAI

from config import model_config, api_config
from embeddings import EmbeddingGenerator
from faiss_store import VectorStore

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Complete RAG pipeline for document Q&A
    
    Architecture:
    1. Query Understanding - Encode user question
    2. Retrieval - Find relevant document chunks (FAISS)
    3. Context Assembly - Combine retrieved chunks
    4. Generation - LLM generates answer grounded in context
    5. Post-processing - Format and validate response
    
    Features:
    - Semantic search with FAISS
    - Context-aware answer generation
    - Source attribution
    - Conversation history support
    - Confidence scoring
    """
    
    def __init__(
        self,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        llm_model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """
        Initialize RAG pipeline
        
        Args:
            embedding_generator: EmbeddingGenerator instance
            llm_model: LLM model name
            temperature: Generation temperature
            max_tokens: Maximum tokens in response
        """
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
        self.llm_model = llm_model or model_config.llm_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        logger.info(f"Initializing RAG Pipeline (model={self.llm_model})")
        
        # Initialize LLM client
        if api_config.openai_api_key:
            self.client = OpenAI(api_key=api_config.openai_api_key)
        else:
            logger.warning("OpenAI API key not set - using mock responses")
            self.client = None
    
    def answer_question(
        self,
        question: str,
        vector_store: VectorStore,
        document_id: str,
        top_k: int = 5,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict:
        """
        Answer a question using RAG
        
        Args:
            question: User's question
            vector_store: Vector store containing document
            document_id: Document to search
            top_k: Number of chunks to retrieve
            conversation_history: Previous conversation turns
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        logger.info(f"RAG query: {question[:50]}...")
        
        # Step 1: Retrieve relevant chunks
        retrieved_chunks, distances = vector_store.search_by_text(
            query_text=question,
            embedding_generator=self.embedding_generator,
            top_k=top_k,
            document_id=document_id
        )
        
        if not retrieved_chunks:
            logger.warning("No relevant chunks found")
            return {
                "answer": "I couldn't find relevant information in the document to answer your question.",
                "relevant_chunks": [],
                "sources": [],
                "confidence_score": 0.0
            }
        
        # Step 2: Assemble context
        context = self._assemble_context(retrieved_chunks)
        
        # Step 3: Generate answer
        answer = self._generate_answer(
            question,
            context,
            conversation_history
        )
        
        # Step 4: Calculate confidence
        confidence = self._calculate_confidence(distances)
        
        # Step 5: Format response
        return {
            "answer": answer,
            "relevant_chunks": [chunk["text"] for chunk in retrieved_chunks],
            "sources": [chunk["chunk_index"] for chunk in retrieved_chunks],
            "confidence_score": confidence,
            "num_chunks_used": len(retrieved_chunks)
        }
    
    def _assemble_context(self, chunks: List[Dict]) -> str:
        """
        Assemble context from retrieved chunks
        
        Args:
            chunks: List of chunk metadata
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Context {i}]:\n{chunk['text']}\n"
            )
        
        return "\n".join(context_parts)
    
    def _generate_answer(
        self,
        question: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]]
    ) -> str:
        """
        Generate answer using LLM
        
        Args:
            question: User's question
            context: Retrieved context
            conversation_history: Previous conversation
            
        Returns:
            Generated answer
        """
        # Build prompt
        system_prompt = """You are a helpful AI assistant that answers questions based on provided context.

Instructions:
1. Answer the question using ONLY information from the provided context
2. If the context doesn't contain enough information, say so
3. Be concise but comprehensive
4. Cite specific parts of the context when possible
5. If asked about something not in the context, politely state that

Be accurate and helpful."""

        user_prompt = f"""Context from document:
{context}

Question: {question}

Please provide a detailed answer based on the context above."""
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if present
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Last 3 turns (6 messages)
        
        # Add current question
        messages.append({"role": "user", "content": user_prompt})
        
        # Generate response
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.llm_model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                answer = response.choices[0].message.content
                logger.info("Generated answer using OpenAI")
                return answer
                
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                return self._fallback_answer(question, context)
        else:
            # Mock response
            return self._fallback_answer(question, context)
    
    def _fallback_answer(self, question: str, context: str) -> str:
        """
        Fallback answer generation without LLM
        
        Simple extractive approach: return most relevant context
        """
        logger.info("Using fallback answer generation")
        
        # Simple heuristic: return first context chunk
        context_parts = context.split("[Context")
        if len(context_parts) > 1:
            first_context = context_parts[1].split("]:")[1].strip()
            return f"Based on the document: {first_context[:500]}..."
        
        return "I found relevant information but couldn't generate a complete answer. Please check the source chunks."
    
    def _calculate_confidence(self, distances: List[float]) -> float:
        """
        Calculate confidence score based on retrieval distances
        
        Args:
            distances: List of distances from FAISS
            
        Returns:
            Confidence score (0-1)
        """
        if not distances:
            return 0.0
        
        # Lower distance = higher confidence
        # Convert L2 distance to confidence score
        avg_distance = sum(distances) / len(distances)
        
        # Heuristic: inverse relationship with distance
        # Normalize to 0-1 range
        confidence = max(0.0, min(1.0, 1.0 - (avg_distance / 10.0)))
        
        return round(confidence, 2)


def create_rag_pipeline(**kwargs) -> RAGPipeline:
    """
    Convenience function to create RAG pipeline
    
    Args:
        **kwargs: Arguments for RAGPipeline
        
    Returns:
        RAGPipeline instance
    """
    return RAGPipeline(**kwargs)
