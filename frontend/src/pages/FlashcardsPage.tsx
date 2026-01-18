import { useState, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { useToast } from '../hooks/use-toast';
import { useStore } from '../store/useStore';
import { apiService } from '../services/api';
import type { Flashcard } from '../services/api';
import { 
    Loader2, 
    Download, 
    GraduationCap, 
    FileText, 
    Brain, 
    Zap, 
    Play, 
    Check, 
    Plus,
    RotateCcw,
    Award,
    BookOpen
} from 'lucide-react';

const difficultyColors = {
    easy: 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900/30 dark:text-green-300 dark:border-green-800',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-900/30 dark:text-yellow-300 dark:border-yellow-800',
    hard: 'bg-red-100 text-red-800 border-red-300 dark:bg-red-900/30 dark:text-red-300 dark:border-red-800',
};

export default function FlashcardsPage() {
    const { toast } = useToast();
    const { currentDocument } = useStore();
    const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedDifficulty, setSelectedDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
    const [numCards, setNumCards] = useState(10);
    const [flippedCards, setFlippedCards] = useState<Set<number>>(new Set());

    // Interactive Study Mode states
    const [isStudyMode, setIsStudyMode] = useState(false);
    const [currentStudyIndex, setCurrentStudyIndex] = useState(0);
    const [masteredCards, setMasteredCards] = useState<Set<number>>(new Set());
    const [practiceCards, setPracticeCards] = useState<Set<number>>(new Set());

    // Custom card form states
    const [showCustomForm, setShowCustomForm] = useState(false);
    const [customQuestion, setCustomQuestion] = useState('');
    const [customAnswer, setCustomAnswer] = useState('');
    const [customTopic, setCustomTopic] = useState('Custom');
    const [isSubmittingCustom, setIsSubmittingCustom] = useState(false);

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
            setMasteredCards(new Set());
            setPracticeCards(new Set());
            setCurrentStudyIndex(0);
            setIsStudyMode(false);
            
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

    const handleCreateCustomCard = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!currentDocument || !customQuestion.trim() || !customAnswer.trim()) return;

        setIsSubmittingCustom(true);
        try {
            const newCard = await apiService.createCustomFlashcard(
                currentDocument.document_id,
                customQuestion,
                customAnswer,
                selectedDifficulty,
                customTopic
            );

            setFlashcards(prev => [newCard, ...prev]);
            setCustomQuestion('');
            setCustomAnswer('');
            setShowCustomForm(false);
            toast({
                title: 'Custom Card Added',
                description: 'Your card was added successfully',
            });
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to add custom card',
                variant: 'destructive',
            });
        } finally {
            setIsSubmittingCustom(false);
        }
    };

    const exportFlashcards = async (format: 'json' | 'anki' | 'csv') => {
        if (!currentDocument) return;

        try {
            const blob = await apiService.exportFlashcards(currentDocument.document_id, format);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `flashcards_${currentDocument.document_id}.${format === 'anki' ? 'txt' : format}`;
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

    const handleMasterCard = (index: number) => {
        setMasteredCards(prev => new Set(prev).add(index));
        setPracticeCards(prev => {
            const next = new Set(prev);
            next.delete(index);
            return next;
        });
        toast({
            title: 'Mastered!',
            description: 'Card marked as mastered.',
        });
        handleNextCard();
    };

    const handlePracticeCard = (index: number) => {
        setPracticeCards(prev => new Set(prev).add(index));
        setMasteredCards(prev => {
            const next = new Set(prev);
            next.delete(index);
            return next;
        });
        toast({
            title: 'Practice Needed',
            description: 'Added to review list.',
        });
        handleNextCard();
    };

    const handleNextCard = () => {
        if (currentStudyIndex < flashcards.length - 1) {
            setCurrentStudyIndex(prev => prev + 1);
        }
    };

    const handlePrevCard = () => {
        if (currentStudyIndex > 0) {
            setCurrentStudyIndex(prev => prev - 1);
        }
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
        <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
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
                        <FileText className="h-4 w-4 text-primary" />
                        {currentDocument.filename}
                    </CardTitle>
                </CardHeader>
            </Card>

            {/* Main view splits if not in Study Mode */}
            {!isStudyMode ? (
                <>
                    {/* Settings & Create Card */}
                    <div className="grid md:grid-cols-3 gap-6">
                        <Card className="md:col-span-2">
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

                        {/* Custom Card Drawer/Box */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg flex items-center justify-between">
                                    <span>Custom Card</span>
                                    <Button 
                                        variant="ghost" 
                                        size="icon" 
                                        className="h-8 w-8"
                                        onClick={() => setShowCustomForm(!showCustomForm)}
                                    >
                                        <Plus className="h-4 w-4" />
                                    </Button>
                                </CardTitle>
                                <CardDescription>Add a custom study card manually</CardDescription>
                            </CardHeader>
                            <CardContent>
                                {showCustomForm ? (
                                    <form onSubmit={handleCreateCustomCard} className="space-y-3">
                                        <div className="space-y-1">
                                            <Label htmlFor="q" className="text-xs">Question</Label>
                                            <Input id="q" placeholder="Enter question..." value={customQuestion} onChange={e => setCustomQuestion(e.target.value)} required />
                                        </div>
                                        <div className="space-y-1">
                                            <Label htmlFor="a" className="text-xs">Answer</Label>
                                            <Input id="a" placeholder="Enter answer..." value={customAnswer} onChange={e => setCustomAnswer(e.target.value)} required />
                                        </div>
                                        <div className="space-y-1">
                                            <Label htmlFor="t" className="text-xs">Topic</Label>
                                            <Input id="t" placeholder="Topic..." value={customTopic} onChange={e => setCustomTopic(e.target.value)} />
                                        </div>
                                        <Button type="submit" disabled={isSubmittingCustom} className="w-full text-xs h-9">
                                            {isSubmittingCustom ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : null}
                                            Save Card
                                        </Button>
                                    </form>
                                ) : (
                                    <div className="text-center py-6 text-muted-foreground text-sm">
                                        Click the <Plus className="inline h-3.5 w-3.5 mx-0.5" /> button to create your own question.
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>

                    {/* Flashcards Grid View */}
                    {flashcards.length > 0 && (
                        <div className="space-y-6">
                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                                <div className="space-y-1">
                                    <h2 className="text-2xl font-bold">
                                        Your Flashcards ({flashcards.length})
                                    </h2>
                                    <p className="text-sm text-muted-foreground">Click a card to reveal the answer</p>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    <Button onClick={() => setIsStudyMode(true)} className="gap-2 bg-gradient-to-r from-primary to-violet-600">
                                        <Play className="h-4 w-4" />
                                        Start Study Session
                                    </Button>
                                    <Button variant="outline" onClick={() => exportFlashcards('json')} title="Export as JSON">
                                        <Download className="h-4 w-4 mr-1" />
                                        JSON
                                    </Button>
                                    <Button variant="outline" onClick={() => exportFlashcards('csv')} title="Export as CSV">
                                        <Download className="h-4 w-4 mr-1" />
                                        CSV
                                    </Button>
                                    <Button variant="outline" onClick={() => exportFlashcards('anki')} title="Export for Anki">
                                        <Download className="h-4 w-4 mr-1" />
                                        Anki
                                    </Button>
                                </div>
                            </div>

                            <div className="grid sm:grid-cols-2 gap-4">
                                {flashcards.map((card, index) => (
                                    <Card
                                        key={index}
                                        className="cursor-pointer hover:shadow-md border border-muted-foreground/10 hover:border-primary/30 transition-all duration-300"
                                        onClick={() => toggleCard(index)}
                                    >
                                        <CardHeader className="pb-2">
                                            <div className="flex items-center justify-between">
                                                <span
                                                    className={`px-2 py-0.5 rounded text-[10px] font-bold border capitalize ${difficultyColors[card.difficulty as keyof typeof difficultyColors]
                                                        }`}
                                                >
                                                    {card.difficulty}
                                                </span>
                                                <span className="text-[10px] text-muted-foreground font-medium">
                                                    {card.card_type || 'Q&A'}
                                                </span>
                                            </div>
                                            <CardTitle className="text-sm font-semibold text-primary mt-2">
                                                {card.topic || 'General'}
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent className="min-h-24 flex flex-col justify-between">
                                            {!flippedCards.has(index) ? (
                                                <div className="space-y-2">
                                                    <Label className="text-[10px] text-muted-foreground">QUESTION</Label>
                                                    <p className="text-sm font-medium leading-relaxed">{card.question}</p>
                                                    <div className="flex items-center justify-center pt-2 text-[10px] text-muted-foreground">
                                                        <Zap className="h-3 w-3 mr-1" />
                                                        <span>Click to reveal answer</span>
                                                    </div>
                                                </div>
                                            ) : (
                                                <div className="space-y-2">
                                                    <Label className="text-[10px] text-primary">ANSWER</Label>
                                                    <p className="text-sm leading-relaxed">{card.answer}</p>
                                                    <div className="flex items-center justify-center pt-2 text-[10px] text-primary">
                                                        <GraduationCap className="h-3.5 w-3.5 mr-1" />
                                                        <span>Click to flip back</span>
                                                    </div>
                                                </div>
                                            )}
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        </div>
                    )}
                </>
            ) : (
                /* Interactive Study Mode Card Carousel */
                <Card className="max-w-xl mx-auto shadow-md border-2 border-primary/20">
                    <CardHeader className="pb-2 border-b">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-bold text-muted-foreground">
                                Card {currentStudyIndex + 1} of {flashcards.length}
                            </span>
                            <Button variant="ghost" size="sm" onClick={() => setIsStudyMode(false)} className="h-8 text-xs text-muted-foreground hover:text-foreground">
                                Exit Session
                            </Button>
                        </div>
                        {/* Session Progress Bar */}
                        <div className="w-full bg-muted h-2 rounded-full overflow-hidden mt-3">
                            <div 
                                className="bg-gradient-to-r from-primary to-violet-600 h-full transition-all duration-500" 
                                style={{ width: `${((masteredCards.size) / flashcards.length) * 100}%` }}
                            />
                        </div>
                        <div className="flex items-center justify-between text-xs text-muted-foreground pt-1.5 font-medium">
                            <span className="flex items-center"><Award className="h-3.5 w-3.5 text-green-500 mr-1" /> {masteredCards.size} Mastered</span>
                            <span className="flex items-center"><BookOpen className="h-3.5 w-3.5 text-yellow-500 mr-1" /> {practiceCards.size} Reviewing</span>
                        </div>
                    </CardHeader>

                    {/* Active Study Card */}
                    <CardContent className="py-12 px-8 min-h-64 flex flex-col justify-center items-center text-center cursor-pointer select-none" onClick={() => toggleCard(currentStudyIndex)}>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border capitalize mb-4 ${
                            difficultyColors[flashcards[currentStudyIndex].difficulty as keyof typeof difficultyColors]
                        }`}>
                            {flashcards[currentStudyIndex].difficulty}
                        </span>
                        
                        {!flippedCards.has(currentStudyIndex) ? (
                            <div className="space-y-4">
                                <span className="text-[10px] tracking-widest text-muted-foreground font-bold uppercase">Question</span>
                                <h3 className="text-lg font-semibold leading-relaxed px-4">
                                    {flashcards[currentStudyIndex].question}
                                </h3>
                                <p className="text-xs text-muted-foreground animate-pulse pt-2">Click card to reveal answer</p>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <span className="text-[10px] tracking-widest text-primary font-bold uppercase">Answer</span>
                                <p className="text-base leading-relaxed text-foreground px-4 font-medium">
                                    {flashcards[currentStudyIndex].answer}
                                </p>
                                <p className="text-xs text-primary pt-2">Click card to see question</p>
                            </div>
                        )}
                    </CardContent>

                    {/* Card Actions */}
                    <CardContent className="pt-2 pb-6 border-t flex flex-col items-center gap-4">
                        <div className="flex gap-3 w-full">
                            <Button 
                                variant="outline" 
                                className="flex-1 border-yellow-400 hover:bg-yellow-50 dark:hover:bg-yellow-950/20 text-yellow-600 gap-1.5 h-11"
                                onClick={() => handlePracticeCard(currentStudyIndex)}
                            >
                                <RotateCcw className="h-4 w-4" />
                                Needs Practice
                            </Button>
                            <Button 
                                className="flex-1 bg-green-600 hover:bg-green-700 text-white gap-1.5 h-11"
                                onClick={() => handleMasterCard(currentStudyIndex)}
                            >
                                <Check className="h-4 w-4" />
                                Got It!
                            </Button>
                        </div>

                        {/* Navigation controls */}
                        <div className="flex items-center justify-between w-full text-sm">
                            <Button variant="ghost" disabled={currentStudyIndex === 0} onClick={handlePrevCard}>
                                Previous Card
                            </Button>
                            <Button variant="ghost" disabled={currentStudyIndex === flashcards.length - 1} onClick={handleNextCard}>
                                Next Card
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}


/* Fix: use import type for Flashcard and FlashcardsResponse */