import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Types
export interface UploadResponse {
    document_id: string;
    filename: string;
    file_size: number;
    upload_time: string;
    status: string;
}

export interface SummarizeRequest {
    document_id: string;
    persona: 'student' | 'teacher' | 'expert';
    max_length?: number;
    include_key_points?: boolean;
}

export interface SummarizeResponse {
    document_id: string;
    persona: string;
    summary: string;
    key_points?: string[];
    word_count: number;
    generation_time: number;
}

export interface ChatRequest {
    document_id: string;
    question: string;
    conversation_history?: Array<{ role: string; content: string }>;
}

export interface ChatResponse {
    document_id: string;
    question: string;
    answer: string;
    sources: Array<{ chunk_id: string; relevance_score: number }>;
    confidence_score: number;
}

export interface FlashcardsRequest {
    document_id: string;
    num_cards?: number;
    difficulty?: 'easy' | 'medium' | 'hard';
    topics?: string[];
}

export interface Flashcard {
    question: string;
    answer: string;
    difficulty: string;
    topic: string;
    card_type: string;
}

export interface FlashcardsResponse {
    document_id: string;
    flashcards: Flashcard[];
    total_cards: number;
}

export interface PersonaInfo {
    type: string;
    name: string;
    description: string;
    features: string[];
    best_for: string;
}

export interface PersonasResponse {
    personas: PersonaInfo[];
}

export interface ComparePersonasResponse {
    document_id: string;
    summaries: Record<string, {
        summary: string;
        key_points: string[];
        word_count: number;
    }>;
}

export interface ChatHistoryResponse {
    document_id: string;
    conversations: Array<{ role: string; content: string }>;
    message: string;
}

export interface TopicPreview {
    name: string;
    key_concepts: string[];
    estimated_cards: number;
}

export interface TopicsPreviewResponse {
    document_id: string;
    topics: TopicPreview[];
    total_estimated_cards: number;
}

export interface MultiTurnChatRequest {
    document_id: string;
    questions: string[];
    top_k?: number;
}

// API Service
export const apiService = {
    // Upload document
    async uploadDocument(file: File): Promise<UploadResponse> {
        const formData = new FormData();
        formData.append('file', file);

        const response = await api.post<UploadResponse>('/upload/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    // Upload multiple documents
    async uploadMultipleDocuments(files: File[]): Promise<UploadResponse[]> {
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));

        const response = await api.post<UploadResponse[]>('/upload/batch', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    // Get upload status
    async getUploadStatus(documentId: string): Promise<UploadResponse> {
        const response = await api.get<UploadResponse>(`/upload/status/${documentId}`);
        return response.data;
    },

    // Delete document
    async deleteDocument(documentId: string): Promise<{ message: string }> {
        const response = await api.delete(`/upload/${documentId}`);
        return response.data;
    },

    // Generate summary
    async generateSummary(request: SummarizeRequest): Promise<SummarizeResponse> {
        const response = await api.post<SummarizeResponse>('/summarize/', request);
        return response.data;
    },

    // Get available personas
    async getPersonas(): Promise<PersonasResponse> {
        const response = await api.get<PersonasResponse>('/summarize/personas');
        return response.data;
    },

    // Compare personas
    async comparePersonas(documentId: string, maxLength: number = 500): Promise<ComparePersonasResponse> {
        const response = await api.post<ComparePersonasResponse>('/summarize/compare', {
            document_id: documentId,
            max_length: maxLength
        });
        return response.data;
    },

    // Chat with document
    async chatWithDocument(request: ChatRequest): Promise<ChatResponse> {
        const response = await api.post<ChatResponse>('/chat/', request);
        return response.data;
    },

    // Multi-turn chat
    async multiTurnChat(request: MultiTurnChatRequest): Promise<ChatResponse[]> {
        const response = await api.post<ChatResponse[]>('/chat/multi-turn', {
            document_id: request.document_id,
            questions: request.questions,
            top_k: request.top_k || 5
        });
        return response.data;
    },

    // Get chat history
    async getChatHistory(documentId: string): Promise<ChatHistoryResponse> {
        const response = await api.get<ChatHistoryResponse>(`/chat/history/${documentId}`);
        return response.data;
    },

    // Clear chat history
    async clearChatHistory(documentId: string): Promise<void> {
        await api.delete(`/chat/history/${documentId}`);
    },

    // Generate flashcards
    async generateFlashcards(request: FlashcardsRequest): Promise<FlashcardsResponse> {
        const response = await api.post<FlashcardsResponse>('/flashcards/', request);
        return response.data;
    },

    // Preview flashcard topics
    async previewFlashcardTopics(documentId: string): Promise<TopicsPreviewResponse> {
        const response = await api.get<TopicsPreviewResponse>(`/flashcards/preview/${documentId}`);
        return response.data;
    },

    // Create custom flashcard
    async createCustomFlashcard(
        documentId: string,
        question: string,
        answer: string,
        difficulty?: string,
        topic?: string
    ): Promise<Flashcard> {
        const response = await api.post<Flashcard>('/flashcards/custom', {
            document_id: documentId,
            question,
            answer,
            difficulty,
            topic
        });
        return response.data;
    },

    // Export flashcards
    async exportFlashcards(
        documentId: string,
        format: 'json' | 'anki' | 'csv'
    ): Promise<Blob> {
        const response = await api.get(`/flashcards/export/${documentId}`, {
            params: { format },
            responseType: 'blob',
        });
        return response.data;
    },
};

export default apiService;
