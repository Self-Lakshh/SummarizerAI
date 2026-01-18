"""
Persona-Aware Summarization
Adaptive document summarization for different user personas
"""

import logging
from typing import List, Dict, Optional
from enum import Enum

from openai import OpenAI

from config import model_config, api_config
from layout_ocr import ProcessedDocument
from chunking import SemanticChunker

logger = logging.getLogger(__name__)


class Persona(str, Enum):
    """User persona types"""
    STUDENT = "student"
    TEACHER = "teacher"
    EXPERT = "expert"


class PersonaSummarizer:
    """
    Generate summaries tailored to different user personas
    
    Persona Characteristics:
    
    STUDENT:
    - Clear, simple language
    - Step-by-step explanations
    - Real-world examples
    - Learning objectives
    - Key takeaways highlighted
    
    TEACHER:
    - Pedagogical insights
    - Teaching strategies
    - Discussion points
    - Assessment ideas
    - Classroom applications
    
    EXPERT:
    - Technical depth
    - Research methodologies
    - Critical analysis
    - Advanced concepts
    - Domain-specific terminology
    """
    
    def __init__(
        self,
        llm_model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """
        Initialize persona summarizer
        
        Args:
            llm_model: LLM model name
            temperature: Generation temperature
            max_tokens: Maximum summary length
        """
        self.llm_model = llm_model or model_config.llm_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        logger.info(f"Initializing PersonaSummarizer (model={self.llm_model})")
        
        # Initialize LLM client
        if api_config.openai_api_key:
            self.client = OpenAI(api_key=api_config.openai_api_key)
        else:
            logger.warning("OpenAI API key not set - using mock responses")
            self.client = None
    
    def summarize(
        self,
        document: ProcessedDocument,
        persona: Persona,
        max_length: int = 500,
        include_key_points: bool = True
    ) -> Dict:
        """
        Generate persona-specific summary
        
        Args:
            document: Processed document
            persona: Target persona
            max_length: Maximum summary length in words
            include_key_points: Whether to extract key points
            
        Returns:
            Dictionary with summary and key points
        """
        logger.info(f"Generating {persona} summary for: {document.filename}")
        
        # Get document text
        text = document.full_text
        
        # Truncate if too long (to fit in context window)
        if len(text.split()) > 3000:
            logger.info("Document too long, truncating...")
            chunker = SemanticChunker(chunk_size=500)
            chunks = chunker.chunk_document(text, document.document_id)
            text = " ".join([chunk.text for chunk in chunks[:6]])  # First ~3000 words
        
        # Generate summary
        summary = self._generate_summary(text, persona, max_length)
        
        # Extract key points if requested
        key_points = []
        if include_key_points:
            key_points = self._extract_key_points(text, persona)
        
        word_count = len(summary.split())
        
        return {
            "summary": summary,
            "key_points": key_points,
            "word_count": word_count,
            "persona": persona.value
        }
    
    def _generate_summary(
        self,
        text: str,
        persona: Persona,
        max_length: int
    ) -> str:
        """
        Generate summary using LLM
        
        Args:
            text: Document text
            persona: Target persona
            max_length: Maximum length in words
            
        Returns:
            Generated summary
        """
        # Build persona-specific prompt
        system_prompt = self._get_system_prompt(persona)
        
        user_prompt = f"""Please summarize the following document in approximately {max_length} words:

{text}

Remember to:
1. Tailor the summary for a {persona.value}
2. Keep it around {max_length} words
3. Focus on the most important information
4. Use appropriate language and style for the target audience"""
        
        # Generate summary
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                summary = response.choices[0].message.content
                logger.info(f"Generated {persona} summary ({len(summary.split())} words)")
                return summary
                
            except Exception as e:
                logger.error(f"Summary generation failed: {e}")
                return self._fallback_summary(text, persona, max_length)
        else:
            return self._fallback_summary(text, persona, max_length)
    
    def _extract_key_points(
        self,
        text: str,
        persona: Persona
    ) -> List[str]:
        """
        Extract key points from document
        
        Args:
            text: Document text
            persona: Target persona
            
        Returns:
            List of key points
        """
        system_prompt = self._get_system_prompt(persona)
        
        user_prompt = f"""Extract 3-5 key points from this document. Format as a bullet list.
Each point should be concise (1-2 sentences) and tailored for a {persona.value}.

Document:
{text[:2000]}..."""  # Truncate for efficiency
        
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.5,  # Lower temperature for extraction
                    max_tokens=300
                )
                
                key_points_text = response.choices[0].message.content
                
                # Parse bullet points
                key_points = [
                    line.strip("- •*").strip()
                    for line in key_points_text.split("\n")
                    if line.strip() and (line.strip().startswith("-") or line.strip().startswith("•") or line.strip().startswith("*"))
                ]
                
                logger.info(f"Extracted {len(key_points)} key points")
                return key_points[:5]  # Limit to 5
                
            except Exception as e:
                logger.error(f"Key point extraction failed: {e}")
                return self._fallback_key_points(persona)
        else:
            return self._fallback_key_points(persona)
    
    def _get_system_prompt(self, persona: Persona) -> str:
        """
        Get persona-specific system prompt
        
        Args:
            persona: Target persona
            
        Returns:
            System prompt string
        """
        prompts = {
            Persona.STUDENT: """You are an expert educator creating summaries for students.

Your summaries should:
- Use clear, accessible language
- Break down complex concepts
- Include relevant examples
- Highlight learning objectives
- Focus on understanding and retention
- Avoid jargon or explain it when necessary
- Be engaging and encouraging""",
            
            Persona.TEACHER: """You are a pedagogical expert creating summaries for teachers.

Your summaries should:
- Highlight teaching opportunities
- Suggest discussion points
- Include assessment ideas
- Note prerequisite knowledge
- Provide classroom application ideas
- Focus on learning outcomes
- Consider diverse learning styles""",
            
            Persona.EXPERT: """You are a domain expert creating summaries for fellow experts.

Your summaries should:
- Use technical terminology appropriately
- Focus on methodologies and findings
- Provide critical analysis
- Highlight novel contributions
- Discuss implications
- Maintain academic rigor
- Reference advanced concepts"""
        }
        
        return prompts.get(persona, prompts[Persona.STUDENT])
    
    def _fallback_summary(
        self,
        text: str,
        persona: Persona,
        max_length: int
    ) -> str:
        """
        Fallback summary generation without LLM
        
        Simple extractive approach
        """
        logger.info("Using fallback summary generation")
        
        # Extract first N words
        words = text.split()[:max_length]
        summary = " ".join(words)
        
        # Add persona-specific prefix
        prefixes = {
            Persona.STUDENT: "This document covers: ",
            Persona.TEACHER: "Teaching points from this document: ",
            Persona.EXPERT: "Key findings: "
        }
        
        return prefixes.get(persona, "") + summary + "..."
    
    def _fallback_key_points(self, persona: Persona) -> List[str]:
        """Fallback key points"""
        defaults = {
            Persona.STUDENT: [
                "Introduction to main concepts",
                "Key definitions and explanations",
                "Practical applications"
            ],
            Persona.TEACHER: [
                "Core teaching objectives",
                "Discussion opportunities",
                "Assessment strategies"
            ],
            Persona.EXPERT: [
                "Methodological approach",
                "Research findings",
                "Implications and future work"
            ]
        }
        
        return defaults.get(persona, [])


def generate_summary(
    document: ProcessedDocument,
    persona: str,
    **kwargs
) -> Dict:
    """
    Convenience function to generate summary
    
    Args:
        document: Processed document
        persona: Persona type (string)
        **kwargs: Additional arguments
        
    Returns:
        Summary dictionary
    """
    summarizer = PersonaSummarizer()
    persona_enum = Persona(persona.lower())
    return summarizer.summarize(document, persona_enum, **kwargs)
