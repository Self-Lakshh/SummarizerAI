import { useState, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Label } from '../components/ui/label';
import { useToast } from '../hooks/use-toast';
import { useStore } from '../store/useStore';
import { apiService, Flashcard } from '../../services/api';
import { Loader2, Download, GraduationCap, FileText, Brain, Zap } from 'lucide-react';

const difficultyColors = {
    easy: 'bg-green-100 text-green-800 border-green-300',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    hard: 'bg-red-100 text-red-800 border-red-300',
};

export default function FlashcardsPage() {
    const { toast } = useToast();
    const { currentDocument } = useStore();
    const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedDifficulty, setSelectedDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
    const [numCards, setNumCards] = useState(10);
    const [flippedCards, setFlippedCards] = useState<Set<number>>(new Set());

    useEffect(() => {
        if (!currentDocument) {
            toast({
                title: 'No Document Selected',
                description: 'Please upload a document first',
                variant: 'destructive',
            });
        }
    }, [currentDocument, toast]);

    const generateFlashcards = async () => {
        if (!currentDocument) return;

        setIsLoading(true);
        try {
            const result = await apiService.generateFlashcards({
                document_id: currentDocument.document_id,
                num_cards: numCards,
                difficulty: selectedDifficulty,
            });

            setFlashcards(result.flashcards);
            setFlippedCards(new Set());
            toast({
                title: 'Flashcards Generated',
                description: `Created ${result.total_cards} flashcards`,
            });
        } catch (error) {
            toast({
                title: 'Generation Failed',
                description: 'Failed to generate flashcards',
                variant: 'destructive',
            });
        } finally {
            setIsLoading(false);
        }
    };

    const exportFlashcards = async (format: 'json' | 'anki' | 'csv') => {
        if (!currentDocument) return;

        try {
            const blob = await apiService.exportFlashcards(currentDocument.document_id, format);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `flashcards_${currentDocument.document_id}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            toast({
                title: 'Export Successful',
                description: `Flashcards exported as ${format.toUpperCase()}`,
            });
        } catch (error) {
            toast({
                title: 'Export Failed',
                description: 'Failed to export flashcards',
                variant: 'destructive',
            });
        }
    };

    const toggleCard = (index: number) => {
        setFlippedCards(prev => {
            const next = new Set(prev);
            if (next.has(index)) {
                next.delete(index);
            } else {
                next.add(index);
            }
            return next;
        });
    };

    if (!currentDocument) {
        return (
            <div className="max-w-4xl mx-auto">
                <Card>
                    <CardHeader>
                        <CardTitle>No Document Selected</CardTitle>
                        <CardDescription>
                            Please upload a document to generate flashcards
                        </CardDescription>
                    </CardHeader>
                </Card>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <div className="space-y-2">
                <h1 className="text-3xl font-bold">Generate Flashcards</h1>
                <p className="text-muted-foreground">
                    AI-powered flashcard generation for effective learning
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

            {/* Generation Settings */}
            <Card>
                <CardHeader>
                    <CardTitle>Flashcard Settings</CardTitle>
                    <CardDescription>
                        Customize your flashcard generation
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="space-y-2">
                        <Label>Number of Cards</Label>
                        <div className="flex gap-2">
                            {[5, 10, 15, 20].map((num) => (
                                <Button
                                    key={num}
                                    variant={numCards === num ? 'default' : 'outline'}
                                    onClick={() => setNumCards(num)}
                                    className="flex-1"
                                >
                                    {num}
                                </Button>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label>Difficulty Level</Label>
                        <div className="grid grid-cols-3 gap-2">
                            {(['easy', 'medium', 'hard'] as const).map((difficulty) => (
                                <Button
                                    key={difficulty}
                                    variant={selectedDifficulty === difficulty ? 'default' : 'outline'}
                                    onClick={() => setSelectedDifficulty(difficulty)}
                                    className="capitalize"
                                >
                                    {difficulty}
                                </Button>
                            ))}
                        </div>
                    </div>

                    <Button
                        onClick={generateFlashcards}
                        disabled={isLoading}
                        className="w-full"
                        size="lg"
                    >
                        {isLoading ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Generating Flashcards...
                            </>
                        ) : (
                            <>
                                <Brain className="mr-2 h-4 w-4" />
                                Generate Flashcards
                            </>
                        )}
                    </Button>
                </CardContent>
            </Card>

            {/* Flashcards Display */}
            {flashcards.length > 0 && (
                <>
                    <div className="flex items-center justify-between">
                        <h2 className="text-2xl font-bold">
                            Your Flashcards ({flashcards.length})
                        </h2>
                        <div className="flex gap-2">
                            <Button variant="outline" onClick={() => exportFlashcards('json')}>
                                <Download className="mr-2 h-4 w-4" />
                                JSON
                            </Button>
                            <Button variant="outline" onClick={() => exportFlashcards('anki')}>
                                <Download className="mr-2 h-4 w-4" />
                                Anki
                            </Button>
                            <Button variant="outline" onClick={() => exportFlashcards('csv')}>
                                <Download className="mr-2 h-4 w-4" />
                                CSV
                            </Button>
                        </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                        {flashcards.map((card, index) => (
                            <Card
                                key={index}
                                className="cursor-pointer hover:shadow-lg transition-shadow"
                                onClick={() => toggleCard(index)}
                            >
                                <CardHeader>
                                    <div className="flex items-center justify-between">
                                        <span
                                            className={`px-2 py-1 rounded text-xs font-medium border ${difficultyColors[card.difficulty as keyof typeof difficultyColors]
                                                }`}
                                        >
                                            {card.difficulty}
                                        </span>
                                        <span className="text-xs text-muted-foreground">
                                            {card.card_type}
                                        </span>
                                    </div>
                                    <CardTitle className="text-base mt-2">
                                        {card.topic}
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    {!flippedCards.has(index) ? (
                                        <div className="space-y-2">
                                            <Label className="text-xs text-muted-foreground">Question</Label>
                                            <p className="text-sm font-medium">{card.question}</p>
                                            <div className="flex items-center justify-center py-4">
                                                <Zap className="h-6 w-6 text-muted-foreground" />
                                                <span className="text-xs text-muted-foreground ml-2">
                                                    Click to reveal answer
                                                </span>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="space-y-2">
                                            <Label className="text-xs text-muted-foreground">Answer</Label>
                                            <p className="text-sm">{card.answer}</p>
                                            <div className="flex items-center justify-center py-2">
                                                <GraduationCap className="h-5 w-5 text-primary" />
                                                <span className="text-xs text-muted-foreground ml-2">
                                                    Click to see question
                                                </span>
                                            </div>
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}
