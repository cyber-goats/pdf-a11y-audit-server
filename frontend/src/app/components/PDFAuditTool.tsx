'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Header } from './audit/Header';
import { FileUpload } from './audit/FileUpload';
import { AnalysisResults } from './audit/AnalysisResults';
import { ErrorMessage } from './audit/ErrorMessage';
import { ReportView } from './audit/ReportView';

import type { Results, ReportData } from '@/app/types';

const PDFAuditTool = () => {
	const [file, setFile] = useState<File | null>(null);
	const [isLoading, setIsLoading] = useState(false);
	const [results, setResults] = useState<Results | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [isDragging, setIsDragging] = useState(false);
	const [progress, setProgress] = useState(0);

	// states for reports
	const [reportData, setReportData] = useState<ReportData | null>(null);
	const [showReport, setShowReport] = useState(false);
	const [isGeneratingReport, setIsGeneratingReport] = useState(false);

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
			setReportData(null); // Reset report
			setShowReport(false);
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
		setReportData(null); // Reset report
		setShowReport(false);
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

	// report generation function
	const generateReport = async () => {
		if (!file) {
			setError('Brak pliku do wygenerowania raportu');
			return;
		}

		setIsGeneratingReport(true);
		setError(null);
		const formData = new FormData();
		formData.append('file', file);

		try {
			const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
			const response = await fetch(`${apiUrl}/generate-report/`, {
				method: 'POST',
				body: formData,
			});

			if (!response.ok) {
				throw new Error('Błąd podczas generowania raportu');
			}

			const data = await response.json();
			setReportData(data);
			setShowReport(true);

			setTimeout(() => {
				document.getElementById('report-section')?.scrollIntoView({
					behavior: 'smooth',
					block: 'start',
				});
			}, 100);
		} catch (err) {
			setError((err as Error).message || 'Nie udało się wygenerować raportu');
		} finally {
			setIsGeneratingReport(false);
		}
	};

	// report download function
	const downloadReport = async (format: string) => {
		if (!reportData) {
			setError('Brak danych raportu do pobrania');
			return;
		}

		try {
			const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
			const response = await fetch(`${apiUrl}/download-report/${format}`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(reportData),
			});

			if (!response.ok) {
				throw new Error('Błąd podczas pobierania raportu');
			}

			const blob = await response.blob();
			const url = window.URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = `raport_dostepnosci_${
				new Date().toISOString().split('T')[0]
			}.${format}`;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			window.URL.revokeObjectURL(url);
		} catch (err) {
			setError((err as Error).message || 'Nie udało się pobrać raportu');
		}
	};

	const handleReset = () => {
		setFile(null);
		setResults(null);
		setError(null);
		setProgress(0);
		setReportData(null);
		setShowReport(false);
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
							<>
								<AnalysisResults
									results={results}
									getAccessibilityScore={getAccessibilityScore}
									getScoreColor={getScoreColor}
								/>

								{/* report generation button */}
								{!showReport && (
									<div className='flex justify-center'>
										<button
											onClick={generateReport}
											disabled={isGeneratingReport}
											className='inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-200'
										>
											{isGeneratingReport ? (
												<>
													<svg
														className='w-5 h-5 animate-spin'
														fill='none'
														viewBox='0 0 24 24'
													>
														<circle
															className='opacity-25'
															cx='12'
															cy='12'
															r='10'
															stroke='currentColor'
															strokeWidth='4'
														></circle>
														<path
															className='opacity-75'
															fill='currentColor'
															d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'
														></path>
													</svg>
													Generowanie raportu...
												</>
											) : (
												<>
													<svg
														className='w-5 h-5'
														fill='none'
														stroke='currentColor'
														viewBox='0 0 24 24'
													>
														<path
															strokeLinecap='round'
															strokeLinejoin='round'
															strokeWidth={2}
															d='M9 17v1a1 1 0 001 1h4a1 1 0 001-1v-1m3-2V8a2 2 0 00-2-2H8a2 2 0 00-2 2v8m5-5h4'
														/>
													</svg>
													Generuj szczegółowy raport
												</>
											)}
										</button>
									</div>
								)}
							</>
						)}

						{/* report display */}
						{showReport && reportData && (
							<div id='report-section'>
								<ReportView
									reportData={reportData}
									onDownload={downloadReport}
								/>

								{/* Button to hide report */}
								<div className='flex justify-center mt-4'>
									<button
										onClick={() => setShowReport(false)}
										className='px-6 py-3 bg-white/10 backdrop-blur-sm text-white font-medium rounded-xl border border-white/20 hover:bg-white/20 transition-all duration-200'
									>
										Ukryj raport
									</button>
								</div>
							</div>
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
