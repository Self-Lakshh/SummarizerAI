import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Upload, FileText, MessageSquare, GraduationCap, Sparkles, Brain, Zap } from 'lucide-react';

const features = [
    {
        title: 'Smart Document Processing',
        description: 'Advanced OCR and layout analysis for PDFs and PowerPoints',
        icon: Brain,
    },
    {
        title: 'Persona-Aware Summaries',
        description: 'Tailored summaries for students, teachers, and experts',
        icon: FileText,
    },
    {
        title: 'RAG-Powered Chat',
        description: 'Ask questions and get accurate answers from your documents',
        icon: MessageSquare,
    },
    {
        title: 'AI Flashcards',
        description: 'Auto-generate study flashcards with difficulty levels',
        icon: GraduationCap,
    },
];

export default function HomePage() {
    return (
        <div className="space-y-12">
            {/* Hero Section */}
            <section className="text-center space-y-6 py-12">
                <div className="flex justify-center">
                    <div className="relative">
                        <Sparkles className="h-16 w-16 text-primary animate-pulse" />
                        <Zap className="h-8 w-8 text-yellow-500 absolute -top-2 -right-2" />
                    </div>
                </div>
                <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
                    Transform Documents into
                    <span className="text-primary"> Knowledge</span>
                </h1>
                <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                    AI-powered document understanding with deep learning. Upload, analyze, chat, and learn from your documents.
                </p>
                <div className="flex justify-center gap-4">
                    <Link to="/upload">
                        <Button size="lg" className="gap-2">
                            <Upload className="h-5 w-5" />
                            Get Started
                        </Button>
                    </Link>
                    <Link to="/chat">
                        <Button size="lg" variant="outline" className="gap-2">
                            <MessageSquare className="h-5 w-5" />
                            Try Chat
                        </Button>
                    </Link>
                </div>
            </section>

            {/* Features Grid */}
            <section className="space-y-8">
                <div className="text-center space-y-2">
                    <h2 className="text-3xl font-bold">Powerful Features</h2>
                    <p className="text-muted-foreground">
                        Built with PyTorch, Transformers, and FAISS
                    </p>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {features.map((feature) => {
                        const Icon = feature.icon;
                        return (
                            <Card key={feature.title} className="hover:shadow-lg transition-shadow">
                                <CardHeader>
                                    <Icon className="h-10 w-10 text-primary mb-2" />
                                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <CardDescription>{feature.description}</CardDescription>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            </section>

            {/* How It Works */}
            <section className="space-y-8 py-12">
                <div className="text-center space-y-2">
                    <h2 className="text-3xl font-bold">How It Works</h2>
                    <p className="text-muted-foreground">Simple and powerful workflow</p>
                </div>
                <div className="grid md:grid-cols-3 gap-8">
                    <div className="text-center space-y-4">
                        <div className="flex justify-center">
                            <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                                <span className="text-xl font-bold text-primary">1</span>
                            </div>
                        </div>
                        <h3 className="text-xl font-semibold">Upload Documents</h3>
                        <p className="text-muted-foreground">
                            Upload PDFs or PowerPoint files. Our OCR handles scanned documents.
                        </p>
                    </div>
                    <div className="text-center space-y-4">
                        <div className="flex justify-center">
                            <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                                <span className="text-xl font-bold text-primary">2</span>
                            </div>
                        </div>
                        <h3 className="text-xl font-semibold">AI Processing</h3>
                        <p className="text-muted-foreground">
                            Semantic chunking, embeddings, and vector indexing with FAISS.
                        </p>
                    </div>
                    <div className="text-center space-y-4">
                        <div className="flex justify-center">
                            <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                                <span className="text-xl font-bold text-primary">3</span>
                            </div>
                        </div>
                        <h3 className="text-xl font-semibold">Interact & Learn</h3>
                        <p className="text-muted-foreground">
                            Summarize, chat, or generate flashcards from your documents.
                        </p>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="bg-primary/5 rounded-lg p-12 text-center space-y-6">
                <h2 className="text-3xl font-bold">Ready to get started?</h2>
                <p className="text-lg text-muted-foreground max-w-xl mx-auto">
                    Upload your first document and experience the power of AI-driven document understanding.
                </p>
                <Link to="/upload">
                    <Button size="lg" className="gap-2">
                        <Upload className="h-5 w-5" />
                        Upload Your Document
                    </Button>
                </Link>
            </section>
        </div>
    );
}
