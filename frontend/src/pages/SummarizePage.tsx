import { useState, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Label } from '../components/ui/label';
import { useToast } from '../hooks/use-toast';
import { useStore } from '../store/useStore';
import { apiService, SummarizeResponse } from '../services/api';
import { FileText, Loader2, GraduationCap, Briefcase, BookOpen } from 'lucide-react';

type Persona = 'student' | 'teacher' | 'expert';

const personaInfo = {
    student: {
        icon: GraduationCap,
        label: 'Student',
        description: 'Simple, learning-focused summaries',
    },
    teacher: {
        icon: Briefcase,
        label: 'Teacher',
        description: 'Pedagogical with teaching points',
    },
    expert: {
        icon: BookOpen,
        label: 'Expert',
        description: 'Technical and comprehensive',
    },
};

export default function SummarizePage() {
    const { toast } = useToast();
    const { currentDocument } = useStore();
    const [selectedPersona, setSelectedPersona] = useState<Persona>('student');
    const [summaries, setSummaries] = useState<Record<Persona, SummarizeResponse | null>>({
        student: null,
        teacher: null,
        expert: null,
    });
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (!currentDocument) {
            toast({
                title: 'No Document Selected',
                description: 'Please upload a document first',
                variant: 'destructive',
            });
        }
    }, [currentDocument, toast]);

    const generateSummary = async (persona: Persona) => {
        if (!currentDocument) return;

        setIsLoading(true);
        try {
            const result = await apiService.generateSummary({
                document_id: currentDocument.document_id,
                persona,
                max_length: 500,
                include_key_points: true,
            });

            setSummaries(prev => ({ ...prev, [persona]: result }));
            toast({
                title: 'Summary Generated',
                description: `${personaInfo[persona].label} summary created successfully`,
            });
        } catch (error) {
            toast({
                title: 'Generation Failed',
                description: 'Failed to generate summary',
                variant: 'destructive',
            });
        } finally {
            setIsLoading(false);
        }
    };

    const comparePersonas = async () => {
        if (!currentDocument) return;

        setIsLoading(true);
        try {
            const results = await apiService.comparePersonas(currentDocument.document_id);
            setSummaries({
                student: results.student,
                teacher: results.teacher,
                expert: results.expert,
            });
            toast({
                title: 'Comparison Complete',
                description: 'All persona summaries generated',
            });
        } catch (error) {
            toast({
                title: 'Comparison Failed',
                description: 'Failed to compare personas',
                variant: 'destructive',
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
                            Please upload a document to generate summaries
                        </CardDescription>
                    </CardHeader>
                </Card>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <div className="space-y-2">
                <h1 className="text-3xl font-bold">Summarize Document</h1>
                <p className="text-muted-foreground">
                    Generate persona-aware summaries tailored to your needs
                </p>
            </div>

            {/* Document Info */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <FileText className="h-5 w-5" />
                        {currentDocument.filename}
                    </CardTitle>
                    <CardDescription>
                        {(currentDocument.file_size / 1024).toFixed(2)} KB • Uploaded {new Date(currentDocument.upload_time).toLocaleDateString()}
                    </CardDescription>
                </CardHeader>
            </Card>

            {/* Persona Selection */}
            <Card>
                <CardHeader>
                    <CardTitle>Select Persona</CardTitle>
                    <CardDescription>
                        Choose the perspective for your summary
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid md:grid-cols-3 gap-4">
                        {(Object.keys(personaInfo) as Persona[]).map((persona) => {
                            const info = personaInfo[persona];
                            const Icon = info.icon;
                            return (
                                <div
                                    key={persona}
                                    onClick={() => setSelectedPersona(persona)}
                                    className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${selectedPersona === persona
                                            ? 'border-primary bg-primary/5'
                                            : 'border-muted hover:border-primary/50'
                                        }`}
                                >
                                    <div className="flex flex-col items-center text-center space-y-2">
                                        <Icon className="h-8 w-8 text-primary" />
                                        <Label className="cursor-pointer">{info.label}</Label>
                                        <p className="text-xs text-muted-foreground">
                                            {info.description}
                                        </p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    <div className="flex gap-2">
                        <Button
                            onClick={() => generateSummary(selectedPersona)}
                            disabled={isLoading}
                            className="flex-1"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Generating...
                                </>
                            ) : (
                                `Generate ${personaInfo[selectedPersona].label} Summary`
                            )}
                        </Button>
                        <Button
                            onClick={comparePersonas}
                            disabled={isLoading}
                            variant="outline"
                        >
                            Compare All
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Summaries */}
            <Tabs value={selectedPersona} onValueChange={(v) => setSelectedPersona(v as Persona)}>
                <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="student">Student</TabsTrigger>
                    <TabsTrigger value="teacher">Teacher</TabsTrigger>
                    <TabsTrigger value="expert">Expert</TabsTrigger>
                </TabsList>

                {(Object.keys(personaInfo) as Persona[]).map((persona) => (
                    <TabsContent key={persona} value={persona}>
                        {summaries[persona] ? (
                            <Card>
                                <CardHeader>
                                    <CardTitle>{personaInfo[persona].label} Summary</CardTitle>
                                    <CardDescription>
                                        {summaries[persona]!.word_count} words • Generated in {summaries[persona]!.generation_time.toFixed(2)}s
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="prose prose-sm max-w-none">
                                        <p className="text-foreground leading-relaxed whitespace-pre-wrap">
                                            {summaries[persona]!.summary}
                                        </p>
                                    </div>

                                    {summaries[persona]!.key_points && (
                                        <div>
                                            <h3 className="font-semibold mb-2">Key Points</h3>
                                            <ul className="space-y-1">
                                                {summaries[persona]!.key_points!.map((point, index) => (
                                                    <li key={index} className="text-sm text-muted-foreground flex items-start">
                                                        <span className="mr-2">•</span>
                                                        <span>{point}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        ) : (
                            <Card>
                                <CardContent className="py-12 text-center">
                                    <p className="text-muted-foreground">
                                        No summary generated yet. Click the button above to generate.
                                    </p>
                                </CardContent>
                            </Card>
                        )}
                    </TabsContent>
                ))}
            </Tabs>
        </div>
    );
}
