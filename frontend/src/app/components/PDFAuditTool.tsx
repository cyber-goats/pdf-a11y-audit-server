'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Header } from './audit/Header';
import { FileUpload } from './audit/FileUpload';
import { AnalysisResults } from './audit/AnalysisResults';
import { ErrorMessage } from './audit/ErrorMessage';

import type { Results } from './audit/AnalysisResults';

const PDFAuditTool = () => {
	const [file, setFile] = useState<File | null>(null);
	const [isLoading, setIsLoading] = useState(false);
	const [results, setResults] = useState<Results | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [isDragging, setIsDragging] = useState(false);
	const [progress, setProgress] = useState(0);
	const fileInputRef = useRef<HTMLInputElement>(null);
	const dropZoneRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		if (isLoading) {
			const interval = setInterval(() => {
				setProgress((prev) => Math.min(prev + 10, 90));
			}, 200);
			return () => clearInterval(interval);
		} else {
			setProgress(0);
		}
	}, [isLoading]);

	const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		e.stopPropagation();
		setIsDragging(true);
	};
	const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		e.stopPropagation();
		if (
			dropZoneRef.current &&
			!dropZoneRef.current.contains(e.relatedTarget as Node)
		) {
			setIsDragging(false);
		}
	};
	const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		e.stopPropagation();
	};
	const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		e.stopPropagation();
		setIsDragging(false);
		const droppedFile = e.dataTransfer.files[0];
		if (droppedFile && droppedFile.type === 'application/pdf') {
			setFile(droppedFile);
			setError(null);
			setResults(null);
		} else {
			setError('Proszę upuścić plik PDF');
		}
	};

	const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
		const selectedFile = event.target.files?.[0] || null;
		if (selectedFile && !selectedFile.type.includes('pdf')) {
			setError('Proszę wybrać plik PDF. Wybrany plik nie jest obsługiwany.');
			setFile(null);
			if (fileInputRef.current) {
				fileInputRef.current.value = '';
			}
			return;
		}
		setFile(selectedFile);
		setError(null);
		setResults(null);
	};

	const handleSubmit = async () => {
		if (!file) {
			setError('Proszę wybrać plik PDF do analizy.');
			return;
		}
		setIsLoading(true);
		setError(null);
		const formData = new FormData();
		formData.append('file', file);
		try {
			const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
			const response = await fetch(`${apiUrl}/upload/pdf/`, {
				method: 'POST',
				body: formData,
			});
			if (!response.ok) {
				throw new Error('Błąd podczas przetwarzania pliku');
			}
			const data = await response.json();
			setResults(data);
			setProgress(100);
		} catch (err) {
			setError((err as Error).message || 'Wystąpił nieoczekiwany błąd');
		} finally {
			setIsLoading(false);
		}
	};

	const handleReset = () => {
		setFile(null);
		setResults(null);
		setError(null);
		setProgress(0);
		if (fileInputRef.current) {
			fileInputRef.current.value = '';
		}
	};

	const formatFileSize = (bytes: number) => {
		if (bytes === 0) return '0 Bytes';
		const k = 1024;
		const sizes = ['Bytes', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
	};

	const getAccessibilityScore = () => {
		if (!results) return 0;
		let score = 0;
		if (results.is_tagged) score += 40;
		if (results.contains_text) score += 40;
		if (
			results.image_info &&
			results.image_info.images_with_alt === results.image_info.image_count
		)
			score += 20;
		else if (results.image_info && results.image_info.images_with_alt > 0)
			score += 10;
		return score;
	};

	const getScoreColor = (score: number) => {
		if (score >= 80) return 'text-green-600';
		if (score >= 50) return 'text-yellow-600';
		return 'text-red-600';
	};

	return (
		<div className='min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900'>
			<div className='fixed inset-0 overflow-hidden pointer-events-none'>
				<div className='absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse'></div>
				<div
					className='absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse'
					style={{ animationDelay: '2s' }}
				></div>
				<div
					className='absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse'
					style={{ animationDelay: '4s' }}
				></div>
			</div>
			<div className='relative z-10'>
				<a
					href='#main-content'
					className='sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-white text-purple-900 px-6 py-3 rounded-lg font-semibold shadow-xl focus:ring-4 focus:ring-purple-400 z-50 transition-all'
				>
					Przejdź do głównej treści
				</a>
				<div className='max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12'>
					<Header />
					<main id='main-content' className='space-y-8'>
						<FileUpload
							file={file}
							isLoading={isLoading}
							isDragging={isDragging}
							progress={progress}
							results={results}
							dropZoneRef={dropZoneRef}
							fileInputRef={fileInputRef}
							handleDragEnter={handleDragEnter}
							handleDragOver={handleDragOver}
							handleDragLeave={handleDragLeave}
							handleDrop={handleDrop}
							handleFileSelect={handleFileSelect}
							handleSubmit={handleSubmit}
							handleReset={handleReset}
							formatFileSize={formatFileSize}
						/>
						<ErrorMessage error={error} />
						{results && (
							<AnalysisResults
								results={results}
								getAccessibilityScore={getAccessibilityScore}
								getScoreColor={getScoreColor}
							/>
						)}
					</main>
					<footer className='text-center mt-20 pt-8 border-t border-white/10'>
						<p className='text-gray-400 mb-2'>
							© 2024 PDF Audytor • Narzędzie do audytu dostępności dokumentów
						</p>
						<p className='text-sm text-gray-500'>
							Zgodne ze standardami WCAG 2.1 AA • PDF/UA
						</p>
					</footer>
				</div>
			</div>
		</div>
	);
};

export default PDFAuditTool;
