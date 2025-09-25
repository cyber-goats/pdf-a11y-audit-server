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
import {
	formatFileSize,
	getAccessibilityScore,
	getScoreColor,
} from '@/app/utils/helpers';
import {
	AnalysisLevelSelector,
	type AnalysisLevel,
} from './audit/AnalysisLevelSelector';
import {
	analyzePdfAction,
	downloadReportAction,
	setAnalysisLevelAction,
} from '../context/actions';
import { useDragAndDrop } from '../hooks/useDragAndDrop';

const PDFAuditTool = () => {
	const state = usePdfAuditState();
	const dispatch = usePdfAuditDispatch();
	const { status, file, results, reportData, error, progress, analysisLevel } =
		state;

	const fileInputRef = useRef<HTMLInputElement>(null);
	const stateRef = useRef(state);
	stateRef.current = state;
	const getState = () => stateRef.current;

	const { dropZoneRef, isDragging, ...dragHandlers } = useDragAndDrop(
		(droppedFile) => dispatch({ type: 'SELECT_FILE', payload: droppedFile }),
		(errorMessage) => dispatch({ type: 'SET_ERROR', payload: errorMessage })
	);

	const isLoading = status === 'analyzing' || status === 'generating_report';
	const currentAccessibilityScore = getAccessibilityScore(results);

	// Ta funkcja upraszcza logikę ponownej analizy
	const handleReanalyze = (newLevel: AnalysisLevel) => {
		setAnalysisLevelAction(dispatch, newLevel);
		if (file) {
			analyzePdfAction(dispatch, file, getState);
		}
	};

	return (
		<div className='min-h-screen bg-slate-900'>
			<div
				className='fixed inset-0 overflow-hidden pointer-events-none opacity-30'
				aria-hidden='true'
			>
				<div className='absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl'></div>
				<div className='absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl'></div>
			</div>

			<div className='relative z-10'>
				<a href='#main-content' className='sr-only focus:not-sr-only ...'>
					Przejdź do głównej treści
				</a>
				<div
					role='status'
					aria-live='polite'
					aria-atomic='true'
					className='sr-only'
				>
					{status === 'analyzing' && 'Analizuję dokument PDF'}
					{status === 'success' && 'Analiza zakończona pomyślnie'}
					{error && `Błąd: ${error}`}
				</div>

				<div className='max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12'>
					<Header />

					<main id='main-content' className='space-y-8'>
						{!results && !reportData && (
							<AnalysisLevelSelector
								selectedLevel={analysisLevel}
								onLevelChange={(level) =>
									setAnalysisLevelAction(dispatch, level)
								}
								disabled={isLoading}
							/>
						)}

						<FileUpload
							file={file}
							isLoading={isLoading}
							isDragging={isDragging}
							progress={progress}
							results={results}
							dropZoneRef={dropZoneRef}
							fileInputRef={fileInputRef}
							{...dragHandlers}
							handleFileSelect={(e) => {
								const selectedFile = e.target.files?.[0];
								if (selectedFile) {
									dispatch({ type: 'SELECT_FILE', payload: selectedFile });
								}
							}}
							handleSubmit={() => {
								if (file) {
									analyzePdfAction(dispatch, file, getState);
								}
							}}
							handleReset={() => {
								dispatch({ type: 'HARD_RESET' });
								if (fileInputRef.current) fileInputRef.current.value = '';
							}}
							formatFileSize={formatFileSize}
						/>

						<ErrorMessage error={error} />

						{/* Blok z wynikami i raportem został uproszczony */}
						{results && (
							<>
								<div className='flex justify-end'>
									<span
										className={`px-4 py-2 rounded-full text-sm font-semibold ${
											analysisLevel === 'quick'
												? 'bg-indigo-600 text-white'
												: analysisLevel === 'standard'
												? 'bg-emerald-600 text-white'
												: 'bg-purple-600 text-white'
										}`}
									>
										Analiza:{' '}
										{analysisLevel === 'quick'
											? 'Szybki skan'
											: analysisLevel === 'standard'
											? 'Standardowa'
											: 'Profesjonalna'}
									</span>
								</div>

								<AnalysisResults
									results={results}
									getAccessibilityScore={() => currentAccessibilityScore}
									getScoreColor={() => getScoreColor(currentAccessibilityScore)}
								/>

								{analysisLevel !== 'professional' && !reportData && (
									<div className='bg-slate-800 rounded-xl p-6 border border-slate-700'>
										<div className='flex items-center justify-between'>
											<div>
												<h3 className='text-white font-semibold mb-1'>
													Potrzebujesz więcej szczegółów?
												</h3>
												<p className='text-slate-400 text-sm'>
													Możesz przeprowadzić głębszą analizę tego dokumentu
												</p>
											</div>
											<button
												onClick={() =>
													handleReanalyze(
														analysisLevel === 'quick'
															? 'standard'
															: 'professional'
													)
												}
												className='px-6 py-3 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 transition-all duration-200'
											>
												{analysisLevel === 'quick'
													? 'Analiza standardowa'
													: 'Audyt profesjonalny'}
											</button>
										</div>
									</div>
								)}

								{reportData && (
									<div id='report-section' className='mt-8'>
										<ReportView
											reportData={reportData}
											onDownload={(format) =>
												downloadReportAction(dispatch, format, reportData)
											}
										/>
										<div className='flex justify-center mt-4'>
											<button
												onClick={() => {
													dispatch({ type: 'HARD_RESET' });
													if (fileInputRef.current)
														fileInputRef.current.value = '';
												}}
												className='px-6 py-3 bg-slate-700 text-white font-medium rounded-xl hover:bg-slate-600 transition-all'
											>
												Analizuj kolejny plik
											</button>
										</div>
									</div>
								)}
							</>
						)}
					</main>

					<footer className='text-center mt-20 pt-8 border-t border-slate-700'>
						<p className='text-slate-300 mb-2'>
							© 2024 PDF Audytor • Narzędzie do audytu dostępności dokumentów
						</p>
						<p className='text-sm text-slate-400'>
							Zgodne ze standardami WCAG 2.1 AA • PDF/UA
						</p>
					</footer>
				</div>
			</div>
		</div>
	);
};

export default PDFAuditTool;
