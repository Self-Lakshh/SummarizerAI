import { useState, useRef, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { useToast } from '../hooks/use-toast';
import { useStore } from '../store/useStore';
import { apiService } from '../services/api';
import { Send, Loader2, User, Bot, FileText } from 'lucide-react';

export default function ChatPage() {
    const { toast } = useToast();
    const { currentDocument, chatMessages, addChatMessage } = useStore();
    const [question, setQuestion] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [chatMessages]);

    useEffect(() => {
        if (!currentDocument) {
            toast({
                title: 'No Document Selected',
                description: 'Please upload a document first',
                variant: 'destructive',
            });
        }
    }, [currentDocument, toast]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!question.trim() || !currentDocument) return;

        const userMessage = question;
        setQuestion('');
        addChatMessage({ role: 'user', content: userMessage });
        setIsLoading(true);

        try {
            const conversationHistory = chatMessages.map(msg => ({
                role: msg.role,
                content: msg.content,
            }));

            const result = await apiService.chatWithDocument({
                document_id: currentDocument.document_id,
                question: userMessage,
                conversation_history: conversationHistory,
            });

            addChatMessage({ role: 'assistant', content: result.answer });
        } catch (error) {
            toast({
                title: 'Chat Failed',
                description: 'Failed to get response',
                variant: 'destructive',
            });
            addChatMessage({
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
            });
        } finally {
            setIsLoading(false);
        }
    };

    if (!currentDocument) {
        return (
            <div className="max-w-4xl mx-auto">
                <Card>
                    <CardHeader>
                        <CardTitle>No Document Selected</CardTitle>
                        <CardDescription>
                            Please upload a document to start chatting
                        </CardDescription>
                    </CardHeader>
                </Card>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-4">
            <div className="space-y-2">
                <h1 className="text-3xl font-bold">Chat with Document</h1>
                <p className="text-muted-foreground">
                    Ask questions and get answers from your document using RAG
                </p>
            </div>

            {/* Document Info */}
            <Card>
                <CardHeader className="py-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                        <FileText className="h-4 w-4" />
                        {currentDocument.filename}
                    </CardTitle>
                </CardHeader>
            </Card>

            {/* Chat Messages */}
            <Card className="flex flex-col h-[600px]">
                <CardHeader>
                    <CardTitle>Conversation</CardTitle>
                    <CardDescription>
                        Powered by RAG with semantic search
                    </CardDescription>
                </CardHeader>
                <CardContent className="flex-1 overflow-y-auto space-y-4">
                    {chatMessages.length === 0 ? (
                        <div className="text-center py-12 text-muted-foreground">
                            <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                            <p>No messages yet. Start by asking a question!</p>
                            <p className="text-sm mt-2">
                                Try: "What is this document about?" or "Summarize the key points"
                            </p>
                        </div>
                    ) : (
                        <>
                            {chatMessages.map((message) => (
                                <div
                                    key={message.id}
                                    className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'
                                        }`}
                                >
                                    {message.role === 'assistant' && (
                                        <div className="flex-shrink-0">
                                            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                                                <Bot className="h-5 w-5 text-primary" />
                                            </div>
                                        </div>
                                    )}
                                    <div
                                        className={`max-w-[80%] rounded-lg px-4 py-2 ${message.role === 'user'
                                                ? 'bg-primary text-primary-foreground'
                                                : 'bg-muted'
                                            }`}
                                    >
                                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                                        <p className="text-xs opacity-70 mt-1">
                                            {new Date(message.timestamp).toLocaleTimeString()}
                                        </p>
                                    </div>
                                    {message.role === 'user' && (
                                        <div className="flex-shrink-0">
                                            <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                                                <User className="h-5 w-5 text-primary-foreground" />
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                            {isLoading && (
                                <div className="flex gap-3 justify-start">
                                    <div className="flex-shrink-0">
                                        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                                            <Bot className="h-5 w-5 text-primary" />
                                        </div>
                                    </div>
                                    <div className="bg-muted rounded-lg px-4 py-2">
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </>
                    )}
                </CardContent>
                <CardContent className="pt-0">
                    <form onSubmit={handleSubmit} className="flex gap-2">
                        <Input
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            placeholder="Ask a question about the document..."
                            disabled={isLoading}
                            className="flex-1"
                        />
                        <Button type="submit" disabled={isLoading || !question.trim()}>
                            {isLoading ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                                <Send className="h-4 w-4" />
                            )}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
