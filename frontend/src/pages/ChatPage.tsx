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
    const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set());
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

    const toggleSources = (msgId: string) => {
        setExpandedSources(prev => {
            const next = new Set(prev);
            if (next.has(msgId)) {
                next.delete(msgId);
            } else {
                next.add(msgId);
            }
            return next;
        });
    };

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

            addChatMessage({ 
                role: 'assistant', 
                content: result.answer,
                sources: result.sources
            });
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
        <div className="max-w-4xl mx-auto space-y-4 animate-fadeIn">
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
                        <FileText className="h-4 w-4 text-primary" />
                        {currentDocument.filename}
                    </CardTitle>
                </CardHeader>
            </Card>

            {/* Chat Messages */}
            <Card className="flex flex-col h-[600px] shadow-sm">
                <CardHeader className="pb-3 border-b">
                    <CardTitle className="text-lg">Conversation</CardTitle>
                    <CardDescription>
                        Powered by RAG with semantic search
                    </CardDescription>
                </CardHeader>
                <CardContent className="flex-1 overflow-y-auto space-y-4 p-6 bg-card/10">
                    {chatMessages.length === 0 ? (
                        <div className="text-center py-20 text-muted-foreground">
                            <Bot className="h-12 w-12 mx-auto mb-4 opacity-40 text-primary" />
                            <p className="font-semibold">No messages yet</p>
                            <p className="text-sm mt-1 max-w-sm mx-auto">
                                Start by asking a question about the document!
                            </p>
                            <p className="text-xs mt-3 bg-muted border rounded-full px-4 py-1.5 inline-block text-muted-foreground font-medium">
                                Try: "What is this document about?"
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
                                            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center border">
                                                <Bot className="h-5 w-5 text-primary" />
                                            </div>
                                        </div>
                                    )}
                                    <div
                                        className={`max-w-[80%] rounded-lg px-4 py-2 border relative group transition-all duration-300 hover:shadow-sm ${message.role === 'user'
                                                ? 'bg-primary text-primary-foreground border-primary-foreground/10'
                                                : 'bg-card text-foreground border-muted-foreground/10'
                                            }`}
                                    >
                                        <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                                        
                                        {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
                                            <div className="mt-2 pt-2 border-t border-muted-foreground/10 space-y-1">
                                                <Button 
                                                    variant="ghost" 
                                                    size="sm" 
                                                    onClick={() => toggleSources(message.id)}
                                                    className="h-6 px-1.5 text-xs text-primary hover:bg-primary/5 flex items-center gap-1 font-semibold"
                                                >
                                                    <span>
                                                        {expandedSources.has(message.id) ? 'Hide Sources' : 'View Citations'}
                                                    </span>
                                                    <span>({message.sources.length})</span>
                                                </Button>
                                                
                                                {expandedSources.has(message.id) && (
                                                    <div className="mt-2 space-y-2 max-h-48 overflow-y-auto text-xs pr-1 border-l-2 border-primary/20 pl-2">
                                                        {message.sources.map((src, sIdx) => (
                                                            <div key={sIdx} className="bg-muted/50 border border-muted-foreground/10 rounded p-2 text-foreground space-y-1">
                                                                <div className="flex items-center justify-between text-[10px] text-muted-foreground font-semibold">
                                                                    <span>{src.chunk_id}</span>
                                                                    <span className="text-primary">{(src.relevance_score * 100).toFixed(1)}% match</span>
                                                                </div>
                                                                <p className="leading-relaxed italic text-muted-foreground">"{src.text}"</p>
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                        
                                        <p className="text-[10px] opacity-75 mt-1 font-mono text-right">
                                            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </p>
                                    </div>
                                    {message.role === 'user' && (
                                        <div className="flex-shrink-0">
                                            <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center border shadow-sm">
                                                <User className="h-5 w-5 text-primary-foreground" />
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                            {isLoading && (
                                <div className="flex gap-3 justify-start">
                                    <div className="flex-shrink-0">
                                        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center border">
                                            <Bot className="h-5 w-5 text-primary" />
                                        </div>
                                    </div>
                                    <div className="bg-card text-foreground border border-muted-foreground/10 rounded-lg px-4 py-3 flex items-center space-x-1">
                                        <span className="h-2 w-2 bg-primary rounded-full animate-bounce" />
                                        <span className="h-2 w-2 bg-primary rounded-full animate-bounce [animation-delay:0.2s]" />
                                        <span className="h-2 w-2 bg-primary rounded-full animate-bounce [animation-delay:0.4s]" />
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </>
                    )}
                </CardContent>
                <CardContent className="pt-3 border-t">
                    <form onSubmit={handleSubmit} className="flex gap-2">
                        <Input
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            placeholder="Ask a question about the document..."
                            disabled={isLoading}
                            className="flex-1 bg-card/30 border-muted-foreground/20"
                        />
                        <Button type="submit" disabled={isLoading || !question.trim()} className="shadow-sm">
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

/* Enhancement: add source citation panel for each assistant message */
/* Enhancement: add 'Copy' action on assistant messages */