import { create } from 'zustand';
import { UploadResponse } from '../services/api';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

interface AppState {
    // Document state
    currentDocument: UploadResponse | null;
    uploadedDocuments: UploadResponse[];
    setCurrentDocument: (doc: UploadResponse | null) => void;
    addUploadedDocument: (doc: UploadResponse) => void;
    removeDocument: (documentId: string) => void;

    // Chat state
    chatMessages: Message[];
    addChatMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
    clearChatMessages: () => void;

    // UI state
    isLoading: boolean;
    setIsLoading: (loading: boolean) => void;
    error: string | null;
    setError: (error: string | null) => void;
}

export const useStore = create<AppState>((set) => ({
    // Document state
    currentDocument: null,
    uploadedDocuments: [],
    setCurrentDocument: (doc) => set({ currentDocument: doc }),
    addUploadedDocument: (doc) =>
        set((state) => ({
            uploadedDocuments: [...state.uploadedDocuments, doc],
        })),
    removeDocument: (documentId) =>
        set((state) => ({
            uploadedDocuments: state.uploadedDocuments.filter(
                (doc) => doc.document_id !== documentId
            ),
            currentDocument:
                state.currentDocument?.document_id === documentId
                    ? null
                    : state.currentDocument,
        })),

    // Chat state
    chatMessages: [],
    addChatMessage: (message) =>
        set((state) => ({
            chatMessages: [
                ...state.chatMessages,
                {
                    ...message,
                    id: Math.random().toString(36).substring(7),
                    timestamp: new Date(),
                },
            ],
        })),
    clearChatMessages: () => set({ chatMessages: [] }),

    // UI state
    isLoading: false,
    setIsLoading: (loading) => set({ isLoading: loading }),
    error: null,
    setError: (error) => set({ error }),
}));
