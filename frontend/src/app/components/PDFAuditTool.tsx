'use client';

import React, { useRef } from 'react';
import { Header } from './audit/Header';
import { FileUpload } from './audit/FileUpload';
import { AnalysisResults } from './audit/AnalysisResults';
import { ErrorMessage } from './audit/ErrorMessage';
import { ReportView } from './audit/ReportView';
import {
	usePdfAuditState,
	usePdfAuditDispatch,
} from '@/app/context/PdfAuditContext';
import { analyzePdfAction, downloadReportAction } from '@/app/context/actions';
import {
	formatFileSize,
	getAccessibilityScore,
	getScoreColor,
} from '@/app/utils/helpers';

const PDFAuditTool = () => {
	// Krok 1: Pobieramy stan i dispatch z globalnego kontekstu
	const state = usePdfAuditState();
	const dispatch = usePdfAuditDispatch();
	const { status, file, results, reportData, error, progress } = state;

	const fileInputRef = useRef<HTMLInputElement>(null);
	const dropZoneRef = useRef<HTMLDivElement>(null);

	const stateRef = useRef(state);
	stateRef.current = state;
	const getState = () => stateRef.current;

	// Krok 2: Definiujemy funkcje obsługi, które wywołują kreatory akcji
	const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
		const selectedFile = event.target.files?.[0];
		if (selectedFile) {
			if (!selectedFile.type.includes('pdf')) {
				dispatch({
					type: 'SET_ERROR',
					payload: 'Nieprawidłowy typ pliku. Proszę wybrać plik PDF.',
				});
				return;
			}
			dispatch({ type: 'SELECT_FILE', payload: selectedFile });
		}
	};

	const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
		event.preventDefault();
		event.stopPropagation();
		dispatch({ type: 'END_DRAG' });
		const droppedFile = event.dataTransfer.files[0];
		if (droppedFile && droppedFile.type === 'application/pdf') {
			dispatch({ type: 'SELECT_FILE', payload: droppedFile });
		} else {
			dispatch({
				type: 'SET_ERROR',
				payload: 'Nieprawidłowy typ pliku. Proszę upuścić plik PDF.',
			});
		}
	};

	const handleSubmit = () => {
		if (file) {
			analyzePdfAction(dispatch, file, getState);
		}
	};

	const handleDownloadReport = (format: string) => {
		if (reportData) {
			downloadReportAction(dispatch, format, reportData);
		}
	};

	const handleReset = () => {
		dispatch({ type: 'HARD_RESET' });
		if (fileInputRef.current) fileInputRef.current.value = '';
	};

	const currentAccessibilityScore = getAccessibilityScore(results);
	const isLoading = status === 'analyzing' || status === 'generating_report';

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
							isDragging={status === 'dragging'}
							progress={progress}
							results={results}
							dropZoneRef={dropZoneRef}
							fileInputRef={fileInputRef}
							handleDragEnter={() => dispatch({ type: 'START_DRAG' })}
							handleDragOver={(e) => e.preventDefault()}
							handleDragLeave={() => dispatch({ type: 'END_DRAG' })}
							handleDrop={handleDrop}
							handleFileSelect={handleFileSelect}
							handleSubmit={handleSubmit}
							handleReset={handleReset}
							formatFileSize={formatFileSize}
						/>
						<ErrorMessage error={error} />

						{/* Ten blok pokazuje WSTĘPNE wyniki, gdy tylko są dostępne */}
						{results && (
							<AnalysisResults
								results={results}
								getAccessibilityScore={() => currentAccessibilityScore}
								getScoreColor={() => getScoreColor(currentAccessibilityScore)}
							/>
						)}

						{/* Ten blok pokazuje PEŁNY raport, gdy tylko jest dostępny */}
						{reportData && (
							<div id='report-section'>
								<ReportView
									reportData={reportData}
									onDownload={handleDownloadReport}
								/>
								<div className='flex justify-center mt-4'>
									<button
										onClick={handleReset} // Zmieniliśmy funkcję na resetowanie
										className='px-6 py-3 bg-white/10 backdrop-blur-sm text-white font-medium rounded-xl border border-white/20 hover:bg-white/20 transition-all duration-200'
									>
										Analizuj kolejny plik
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
