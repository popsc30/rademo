import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import { Link } from "react-router-dom";
import { uploadFile } from "@/api/chatService";

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadMessage, setUploadMessage] = useState("");

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setFile(e.target.files[0]);
            setUploadMessage("");
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setIsUploading(true);
        setUploadMessage(`Uploading "${file.name}"...`);

        try {
            const responseMessage = await uploadFile(file);
            setUploadMessage(responseMessage);
        } catch (error) {
            setUploadMessage(error instanceof Error ? error.message : "An unknown error occurred.");
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center h-screen p-4 bg-background">
            <div className="w-full max-w-md p-8 space-y-6 border rounded-lg shadow-xl bg-card text-card-foreground">
                <div className="text-center">
                    <h1 className="text-2xl font-bold">Upload Knowledge Document</h1>
                    <p className="text-muted-foreground">Upload a PDF or DOCX file to update the knowledge base.</p>
                </div>

                <div
                    className="flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-lg cursor-pointer hover:border-primary"
                    onClick={() => document.getElementById('file-upload')?.click()}
                >
                    <Input id="file-upload" type="file" onChange={handleFileChange} accept=".pdf,.docx" className="hidden" />
                    <p className="text-muted-foreground">{file ? file.name : "Drag & drop or click to select a file"}</p>
                </div>

                <Button onClick={handleUpload} disabled={!file || isUploading} className="w-full">
                    {isUploading ? "Uploading..." : "Upload"}
                </Button>

                {uploadMessage && (
                    <div className="p-3 text-center rounded-lg bg-muted">
                        <p className="text-sm text-muted-foreground">{uploadMessage}</p>
                    </div>
                )}

                <div className="text-center">
                    <Link to="/" className="text-sm text-primary hover:underline">
                        Return to Chat
                    </Link>
                </div>
            </div>
        </div>
    );
} 