"use client";
import { useCallback, useState } from "react";
import { CircularProgress } from "@heroui/progress";
import { Textarea } from "@heroui/input";
import { useDropzone } from "react-dropzone";
import { MdUploadFile } from "react-icons/md";
// Local
import { API_URL } from "@/app/constants";
import { Button } from "@heroui/react";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [userQuery, setUserQuery] = useState("");

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    setIsLoading(true); // Disable button and show loading state

    const formData = new FormData();
    formData.append("file", acceptedFiles[0]); // Send the first file

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      const presentationLink = result["presentation_link"];

      // Download file from presentationLink
      const link = document.createElement("a");
      link.href = presentationLink;
      link.download = "presentation.pptx";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Error uploading file:", error);
    } finally {
      setIsLoading(false); // Enable button after API response
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  async function onAnalyzeTextButtonPress() {
    try {
      const response = await fetch(
        `${API_URL}/analyze_text/?query=${userQuery.trim()}`
      );

      const result = await response.json();
      const presentationLink = result["presentation_link"];

      // Download file from presentationLink
      const link = document.createElement("a");
      link.href = presentationLink;
      link.download = "presentation.pptx";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Error uploading file:", error);
    } finally {
      setIsLoading(false); // Enable button after API response
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <h1 className="text-4xl font-bold text-gray-800 mb-6">
        ProSights MarketMap to PPT 🚀
      </h1>
      {!isLoading && (
        <div
          {...getRootProps()}
          className={`mt-4 flex flex-col items-center justify-center w-80 sm:w-96 h-40 sm:h-48 p-4 border-2 border-dashed rounded-lg cursor-pointer 
          ${isDragActive ? "bg-gray-200" : "bg-gray-100"}`}
        >
          <MdUploadFile size={48} className="text-slate-500 mb-2" />
          <input {...getInputProps()} />
          {isDragActive ? (
            <p className="text-lg font-medium text-gray-700">Drop image here</p>
          ) : (
            <p className="text-lg font-medium text-gray-700 text-center">
              Drag and drop a picture of a market map here or click to select
              image.
            </p>
          )}
        </div>
      )}

      {!isLoading && <h4 className="mt-4">or</h4>}
      {!isLoading && (
        <Textarea
          className="max-w-sm mt-4"
          label="Enter list of companies"
          placeholder="Bain Capital, a16z..."
          onChange={(e) => setUserQuery(e.target.value)}
        />
      )}

      {!isLoading && (
        <Button
          variant="shadow"
          className="mt-4 text-lg"
          color="primary"
          onPress={onAnalyzeTextButtonPress}
        >
          Analyze Text
        </Button>
      )}

      {isLoading && <CircularProgress aria-label="loading" />}
    </div>
  );
}
