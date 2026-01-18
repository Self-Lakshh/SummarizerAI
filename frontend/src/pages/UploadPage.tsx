import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { useToast } from '../hooks/use-toast';
import { useStore } from '../store/useStore';
import { apiService } from '../services/api';
import { Upload, FileText, CheckCircle, XCircle, Loader2 } from 'lucide-react';

export default function UploadPage() {
    const navigate = useNavigate();
    const { toast } = useToast();
    const { addUploadedDocument, setCurrentDocument } = useStore();
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadedFiles, setUploadedFiles] = useState<Array<{ name: string; status: 'success' | 'error' }>>([]);

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        setIsUploading(true);
        setUploadProgress(0);
        setUploadedFiles([]);

        for (let i = 0; i < acceptedFiles.length; i++) {
            const file = acceptedFiles[i];
            try {
                const result = await apiService.uploadDocument(file);
                addUploadedDocument(result);
                setCurrentDocument(result);
                setUploadedFiles(prev => [...prev, { name: file.name, status: 'success' }]);

                toast({
                    title: 'Upload Successful',
                    description: `${file.name} uploaded successfully!`,
                });

                setUploadProgress(((i + 1) / acceptedFiles.length) * 100);
            } catch (error) {
                setUploadedFiles(prev => [...prev, { name: file.name, status: 'error' }]);
                toast({
                    title: 'Upload Failed',
                    description: `Failed to upload ${file.name}`,
                    variant: 'destructive',
                });
            }
        }

        setIsUploading(false);
        if (uploadedFiles.some(f => f.status === 'success')) {
            setTimeout(() => navigate('/summarize'), 1500);
        }
    }, [addUploadedDocument, setCurrentDocument, toast, navigate, uploadedFiles]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
            'application/vnd.ms-powerpoint': ['.ppt'],
        },
        maxSize: 50 * 1024 * 1024, // 50MB
    });

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <div className="space-y-2">
                <h1 className="text-3xl font-bold">Upload Documents</h1>
                <p className="text-muted-foreground">
                    Upload PDF or PowerPoint files to get started. Maximum file size: 50MB.
                </p>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Document Upload</CardTitle>
                    <CardDescription>
                        Drag and drop files or click to browse
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div
                        {...getRootProps()}
                        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${isDragActive
                                ? 'border-primary bg-primary/5'
                                : 'border-muted-foreground/25 hover:border-primary/50'
                            }`}
                    >
                        <input {...getInputProps()} />
                        <div className="flex flex-col items-center space-y-4">
                            {isUploading ? (
                                <Loader2 className="h-12 w-12 text-primary animate-spin" />
                            ) : (
                                <Upload className="h-12 w-12 text-muted-foreground" />
                            )}
                            {isDragActive ? (
                                <p className="text-lg font-medium">Drop files here...</p>
                            ) : (
                                <>
                                    <p className="text-lg font-medium">
                                        Drag & drop files here, or click to select
                                    </p>
                                    <p className="text-sm text-muted-foreground">
                                        Supported formats: PDF, PPT, PPTX
                                    </p>
                                </>
                            )}
                        </div>
                    </div>

                    {isUploading && (
                        <div className="mt-6 space-y-2">
                            <div className="flex items-center justify-between text-sm">
                                <span>Uploading...</span>
                                <span>{Math.round(uploadProgress)}%</span>
                            </div>
                            <Progress value={uploadProgress} />
                        </div>
                    )}

                    {uploadedFiles.length > 0 && (
                        <div className="mt-6 space-y-2">
                            <h3 className="font-medium">Upload Results</h3>
                            {uploadedFiles.map((file, index) => (
                                <div
                                    key={index}
                                    className="flex items-center justify-between p-3 rounded-md bg-muted"
                                >
                                    <div className="flex items-center space-x-2">
                                        <FileText className="h-4 w-4" />
                                        <span className="text-sm">{file.name}</span>
                                    </div>
                                    {file.status === 'success' ? (
                                        <CheckCircle className="h-5 w-5 text-green-500" />
                                    ) : (
                                        <XCircle className="h-5 w-5 text-red-500" />
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Features</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                    <div className="flex items-start space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                        <div>
                            <p className="font-medium">OCR Support</p>
                            <p className="text-sm text-muted-foreground">
                                Automatically extracts text from scanned documents
                            </p>
                        </div>
                    </div>
                    <div className="flex items-start space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                        <div>
                            <p className="font-medium">Layout Preservation</p>
                            <p className="text-sm text-muted-foreground">
                                Maintains document structure and formatting
                            </p>
                        </div>
                    </div>
                    <div className="flex items-start space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                        <div>
                            <p className="font-medium">Multi-format Support</p>
                            <p className="text-sm text-muted-foreground">
                                Works with PDF, PowerPoint, and more
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
