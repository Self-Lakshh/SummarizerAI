"""
AI-Powered Flashcard Generation
Automatic question-answer pair creation for learning
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
import re

from openai import OpenAI

from config import model_config, api_config
from layout_ocr import ProcessedDocument
from chunking import SemanticChunker

logger = logging.getLogger(__name__)


@dataclass
class Flashcard:
    """Represents a single flashcard"""
    question: str
    answer: str
    difficulty: str  # easy, medium, hard
    topic: Optional[str] = None
    explanation: Optional[str] = None


class FlashcardGenerator:
    """
    Generate educational flashcards using AI
    
    Question Types:
    - Factual recall (who, what, when, where)
    - Conceptual understanding (why, how, explain)
    - Application (apply, use, implement)
    - Analysis (compare, contrast, analyze)
    
    Difficulty Levels:
    - Easy: Basic facts and definitions
    - Medium: Conceptual understanding
    - Hard: Application and analysis
    """
    
    def __init__(
        self,
        llm_model: Optional[str] = None,
        temperature: float = 0.8
    ):
        """
        Initialize flashcard generator
        
        Args:
            llm_model: LLM model name
            temperature: Generation temperature (higher = more creative)
        """
        self.llm_model = llm_model or model_config.llm_model
        self.temperature = temperature
        
        logger.info(f"Initializing FlashcardGenerator (model={self.llm_model})")
        
        # Initialize LLM client
        if api_config.openai_api_key:
            self.client = OpenAI(api_key=api_config.openai_api_key)
        else:
            logger.warning("OpenAI API key not set - using mock flashcards")
            self.client = None
    
    def generate_flashcards(
        self,
        document: ProcessedDocument,
        num_cards: int = 10,
        difficulty: Optional[str] = None,
        topics: Optional[List[str]] = None
    ) -> List[Flashcard]:
        """
        Generate flashcards from document
        
        Args:
            document: Processed document
            num_cards: Number of flashcards to generate
            difficulty: Target difficulty (easy, medium, hard)
            topics: Specific topics to focus on
            
        Returns:
            List of Flashcard objects
        """
        logger.info(
            f"Generating {num_cards} flashcards from: {document.filename}"
        )
        
        # Get document text
        text = document.full_text
        
        # Chunk document for better coverage
        chunker = SemanticChunker(chunk_size=500)
        chunks = chunker.chunk_document(text, document.document_id)
        
        # Generate flashcards
        flashcards = []
        
        if self.client:
            # Generate in batches
            batch_size = 5
            for i in range(0, num_cards, batch_size):
                batch_count = min(batch_size, num_cards - i)
                
                # Select relevant chunks for this batch
                chunk_text = self._select_chunks_for_batch(chunks, i, batch_size)
                
                # Generate batch
                batch_cards = self._generate_batch(
                    chunk_text,
                    batch_count,
                    difficulty,
                    topics
                )
                flashcards.extend(batch_cards)
                
                if len(flashcards) >= num_cards:
                    break
        else:
            # Fallback mock flashcards
            flashcards = self._generate_mock_flashcards(num_cards, difficulty)
        
        logger.info(f"Generated {len(flashcards)} flashcards")
        return flashcards[:num_cards]  # Ensure exact count
    
    def _select_chunks_for_batch(
        self,
        chunks: List,
        start_idx: int,
        batch_size: int
    ) -> str:
        """
        Select document chunks for flashcard generation batch
        
        Args:
            chunks: List of text chunks
            start_idx: Starting flashcard index
            batch_size: Number of cards in batch
            
        Returns:
            Combined chunk text
        """
        # Distribute chunks across batches
        chunks_per_card = max(1, len(chunks) // 10)  # Assume 10 cards total
        start_chunk = (start_idx // batch_size) * chunks_per_card
        end_chunk = start_chunk + chunks_per_card * 2  # Get extra chunks for variety
        
        selected_chunks = chunks[start_chunk:end_chunk]
        return "\n\n".join([c.text for c in selected_chunks])
    
    def _generate_batch(
        self,
        text: str,
        num_cards: int,
        difficulty: Optional[str],
        topics: Optional[List[str]]
    ) -> List[Flashcard]:
        """
        Generate a batch of flashcards
        
        Args:
            text: Source text
            num_cards: Number of cards to generate
            difficulty: Target difficulty
            topics: Specific topics
            
        Returns:
            List of Flashcard objects
        """
        # Build prompt
        system_prompt = """You are an expert educational content creator specializing in creating effective flashcards.

Create flashcards that:
1. Test key concepts and understanding
2. Are clear and unambiguous
3. Have concise but complete answers
4. Vary in question type (what, why, how, compare, etc.)
5. Are appropriate for the specified difficulty level

Format each flashcard as:
Q: [Question]
A: [Answer]
D: [easy/medium/hard]
T: [Topic]
---"""
        
        difficulty_guidance = {
            "easy": "Focus on basic facts, definitions, and simple recall",
            "medium": "Focus on conceptual understanding and explanation",
            "hard": "Focus on application, analysis, and synthesis"
        }
        
        user_prompt = f"""Generate {num_cards} educational flashcards from this content:

{text[:2000]}

Requirements:
- Number of flashcards: {num_cards}
{f"- Difficulty level: {difficulty} ({difficulty_guidance.get(difficulty, '')})" if difficulty else "- Mix of difficulty levels"}
{f"- Focus on topics: {', '.join(topics)}" if topics else "- Cover main topics from the text"}

Format each flashcard exactly as:
Q: [Question]
A: [Answer]
D: [easy/medium/hard]
T: [Topic]
---"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=1500
            )
            
            flashcard_text = response.choices[0].message.content
            
            # Parse flashcards
            flashcards = self._parse_flashcards(flashcard_text)
            
            logger.info(f"Generated batch of {len(flashcards)} flashcards")
            return flashcards
            
        except Exception as e:
            logger.error(f"Flashcard generation failed: {e}")
            return []
    
    def _parse_flashcards(self, text: str) -> List[Flashcard]:
        """
        Parse flashcards from generated text
        
        Args:
            text: Generated flashcard text
            
        Returns:
            List of Flashcard objects
        """
        flashcards = []
        
        # Split by separator
        card_texts = text.split("---")
        
        for card_text in card_texts:
            card_text = card_text.strip()
            if not card_text:
                continue
            
            # Extract fields
            question = self._extract_field(card_text, "Q:")
            answer = self._extract_field(card_text, "A:")
            difficulty = self._extract_field(card_text, "D:")
            topic = self._extract_field(card_text, "T:")
            
            if question and answer:
                # Validate difficulty
                if difficulty not in ["easy", "medium", "hard"]:
                    difficulty = "medium"
                
                flashcard = Flashcard(
                    question=question,
                    answer=answer,
                    difficulty=difficulty,
                    topic=topic or "General"
                )
                flashcards.append(flashcard)
        
        return flashcards
    
    def _extract_field(self, text: str, field_marker: str) -> str:
        """
        Extract field value from flashcard text
        
        Args:
            text: Card text
            field_marker: Field marker (e.g., "Q:", "A:")
            
        Returns:
            Field value
        """
        # Find field
        pattern = f"{re.escape(field_marker)}\\s*(.+?)(?=[QAD]:|$)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return ""
    
    def _generate_mock_flashcards(
        self,
        num_cards: int,
        difficulty: Optional[str]
    ) -> List[Flashcard]:
        """
        Generate mock flashcards for testing
        
        Args:
            num_cards: Number of cards
            difficulty: Target difficulty
            
        Returns:
            List of mock flashcards
        """
        logger.info("Generating mock flashcards (no API key)")
        
        diff = difficulty or "medium"
        
        templates = [
            ("What is the main concept discussed?", "The document discusses key concepts related to the topic."),
            ("Explain the methodology used.", "The methodology involves a systematic approach to the problem."),
            ("What are the key findings?", "The key findings include several important insights."),
            ("How can this be applied?", "This can be applied in various real-world scenarios."),
            ("Compare and contrast the approaches.", "Different approaches have their own advantages and limitations."),
        ]
        
        flashcards = []
        for i in range(num_cards):
            template_idx = i % len(templates)
            question, answer = templates[template_idx]
            
            flashcard = Flashcard(
                question=f"{question} (Card {i+1})",
                answer=answer,
                difficulty=diff,
                topic="General"
            )
            flashcards.append(flashcard)
        
        return flashcards
    
    def export_to_anki(
        self,
        flashcards: List[Flashcard],
        output_file: str
    ) -> None:
        """
        Export flashcards to Anki-compatible format
        
        Args:
            flashcards: List of flashcards
            output_file: Output CSV file path
        """
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            
            for card in flashcards:
                writer.writerow([
                    card.question,
                    card.answer,
                    card.topic or ""
                ])
        
        logger.info(f"Exported {len(flashcards)} flashcards to {output_file}")


def generate_flashcards(
    document: ProcessedDocument,
    num_cards: int = 10,
    **kwargs
) -> List[Dict]:
    """
    Convenience function to generate flashcards
    
    Args:
        document: Processed document
        num_cards: Number of cards
        **kwargs: Additional arguments
        
    Returns:
        List of flashcard dictionaries
    """
    generator = FlashcardGenerator()
    flashcards = generator.generate_flashcards(document, num_cards, **kwargs)
    
    # Convert to dictionaries
    return [
        {
            "question": card.question,
            "answer": card.answer,
            "difficulty": card.difficulty,
            "topic": card.topic
        }
        for card in flashcards
    ]
