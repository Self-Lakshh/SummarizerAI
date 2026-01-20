import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { apiService } from '../services/api';
import type { UploadResponse } from '../services/api';
import { useToast } from '../hooks/use-toast';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
    FileText, 
    Trash2, 
    ExternalLink, 
    Search, 
    Folder, 
    RefreshCw,
    Loader2,
    Calendar,
    HardDrive
} from 'lucide-react';

export default function LibraryPage() {
    const navigate = useNavigate();
    const { toast } = useToast();
    const { 
        uploadedDocuments, 
        setUploadedDocuments, 
        setCurrentDocument, 
        currentDocument,
        removeDocument
    } = useStore();
    
    const [searchQuery, setSearchQuery] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // Fetch documents on mount
    const fetchDocuments = async (silent = false) => {
        if (!silent) setIsLoading(true);
        try {
            const docs = await apiService.listDocuments();
            setUploadedDocuments(docs);
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to fetch documents from library',
                variant: 'destructive',
            });
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchDocuments();
    }, []);

    // Handle document selection
    const handleSelectDocument = (doc: UploadResponse) => {
        setCurrentDocument(doc);
        toast({
            title: 'Document Selected',
            description: `Active document set to: ${doc.filename}`,
        });
        navigate('/summarize');
    };

    // Handle document deletion
    const handleDeleteDocument = async (e: React.MouseEvent, docId: string) => {
        e.stopPropagation(); // Prevent selection trigger
        if (!confirm('Are you sure you want to delete this document and all its data?')) return;

        try {
            await apiService.deleteDocument(docId);
            removeDocument(docId);
            toast({
                title: 'Success',
                description: 'Document deleted successfully',
            });
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to delete document',
                variant: 'destructive',
            });
        }
    };

    // Format file size
    const formatBytes = (bytes: number) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // Filter documents based on search query
    const filteredDocs = uploadedDocuments.filter(doc => 
        doc.filename.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="max-w-6xl mx-auto space-y-8 animate-fadeIn">
            {/* Page Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="space-y-2">
                    <h1 className="text-3xl font-bold tracking-tight">Document Library</h1>
                    <p className="text-muted-foreground">
                        Manage and explore your uploaded knowledge base. Select a document to summarize or chat with it.
                    </p>
                </div>
                <div className="flex gap-2">
                    <Button 
                        variant="outline" 
                        size="icon" 
                        onClick={() => fetchDocuments(false)}
                        disabled={isLoading}
                        title="Refresh Library"
                    >
                        <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                    </Button>
                    <Button onClick={() => navigate('/upload')}>
                        Upload New
                    </Button>
                </div>
            </div>

            {/* Search Bar */}
            <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                    placeholder="Search documents by filename..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 h-11 bg-card border-muted-foreground/20 focus-visible:ring-primary"
                />
            </div>

            {/* Loading State */}
            {isLoading ? (
                <div className="flex flex-col items-center justify-center py-24 space-y-4">
                    <Loader2 className="h-12 w-12 text-primary animate-spin" />
                    <p className="text-muted-foreground">Loading your library...</p>
                </div>
            ) : filteredDocs.length === 0 ? (
                /* Empty State */
                <Card className="border-dashed border-2 p-12 text-center bg-card/50">
                    <CardContent className="flex flex-col items-center justify-center space-y-4">
                        <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                            <Folder className="h-8 w-8 text-primary" />
                        </div>
                        <h3 className="text-xl font-semibold">No Documents Found</h3>
                        <p className="text-muted-foreground max-w-md mx-auto">
                            {searchQuery 
                                ? "We couldn't find any documents matching your search term."
                                : "Your library is empty. Upload PDFs or presentations to start extracting key insights."
                            }
                        </p>
                        {!searchQuery && (
                            <Button onClick={() => navigate('/upload')} className="mt-2">
                                Upload Your First File
                            </Button>
                        )}
                    </CardContent>
                </Card>
            ) : (
                /* Grid View */
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredDocs.map((doc) => {
                        const isActive = currentDocument?.document_id === doc.document_id;
                        const isPPT = doc.filename.endsWith('.ppt') || doc.filename.endsWith('.pptx');

                        return (
                            <Card 
                                key={doc.document_id}
                                onClick={() => handleSelectDocument(doc)}
                                className={`group cursor-pointer border-2 transition-all duration-300 hover:shadow-lg hover:border-primary/50 relative overflow-hidden bg-card ${
                                    isActive ? 'border-primary shadow-md' : 'border-muted-foreground/10'
                                }`}
                            >
                                {/* Highlight ribbon for active doc */}
                                {isActive && (
                                    <div className="absolute top-0 right-0 bg-primary text-primary-foreground text-[10px] font-bold px-2 py-0.5 rounded-bl">
                                        ACTIVE
                                    </div>
                                )}
                                
                                <CardHeader className="pb-3">
                                    <div className="flex items-start space-x-3">
                                        <div className={`p-2 rounded-lg ${isPPT ? 'bg-orange-500/10 text-orange-600' : 'bg-red-500/10 text-red-600'}`}>
                                            <FileText className="h-6 w-6" />
                                        </div>
                                        <div className="space-y-1 pr-6 flex-1 min-w-0">
                                            <CardTitle className="text-base font-semibold leading-tight truncate group-hover:text-primary transition-colors">
                                                {doc.filename}
                                            </CardTitle>
                                            <CardDescription className="text-xs font-mono uppercase tracking-wider">
                                                {doc.file_type || (isPPT ? '.ppt' : '.pdf')}
                                            </CardDescription>
                                        </div>
                                    </div>
                                </CardHeader>

                                <CardContent className="pb-4 space-y-4">
                                    {/* Stats grid */}
                                    <div className="grid grid-cols-2 gap-2 text-xs border-t border-b py-3 text-muted-foreground">
                                        <div className="flex items-center gap-1.5">
                                            <HardDrive className="h-3.5 w-3.5" />
                                            <span>{formatBytes(doc.file_size)}</span>
                                        </div>
                                        <div className="flex items-center gap-1.5 justify-end">
                                            <Calendar className="h-3.5 w-3.5" />
                                            <span>{doc.upload_time ? new Date(doc.upload_time).toLocaleDateString() : 'N/A'}</span>
                                        </div>
                                    </div>

                                    {/* Status Indicator */}
                                    <div className="flex items-center justify-between text-xs pt-1">
                                        <div className="flex items-center space-x-1.5">
                                            <div className={`h-2.5 w-2.5 rounded-full ${
                                                doc.status === 'processing' 
                                                    ? 'bg-yellow-500 animate-pulse' 
                                                    : doc.status === 'failed' 
                                                        ? 'bg-red-500' 
                                                        : 'bg-green-500'
                                            }`} />
                                            <span className="capitalize font-medium">
                                                {doc.status || 'completed'}
                                            </span>
                                        </div>

                                        {/* Action buttons */}
                                        <div className="flex items-center space-x-1 opacity-80 group-hover:opacity-100 transition-opacity">
                                            <Button 
                                                variant="ghost" 
                                                size="icon" 
                                                className="h-8 w-8 hover:text-primary hover:bg-primary/5"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleSelectDocument(doc);
                                                }}
                                                title="Open Document"
                                            >
                                                <ExternalLink className="h-4 w-4" />
                                            </Button>
                                            <Button 
                                                variant="ghost" 
                                                size="icon" 
                                                className="h-8 w-8 hover:text-destructive hover:bg-destructive/5 text-muted-foreground"
                                                onClick={(e) => handleDeleteDocument(e, doc.document_id)}
                                                title="Delete Document"
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            )}
        </div>
    );
}

/* Enhancement: filter documents by type (PDF/PPTX) */