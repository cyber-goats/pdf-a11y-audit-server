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
import { analyzePdfAction, downloadReportAction, setAnalysisLevelAction } from '../context/actions';

const PDFAuditTool = () => {
	const state = usePdfAuditState();
	const dispatch = usePdfAuditDispatch();
	const { status, file, results, reportData, error, progress, analysisLevel } =
		state;

	const fileInputRef = useRef<HTMLInputElement>(null);
	const dropZoneRef = useRef<HTMLDivElement>(null);

	const stateRef = useRef(state);
	stateRef.current = state;
	const getState = () => stateRef.current;

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

	const handleLevelChange = (level: AnalysisLevel) => {
		setAnalysisLevelAction(dispatch, level);
	};

	const currentAccessibilityScore = getAccessibilityScore(results);
	const isLoading = status === 'analyzing' || status === 'generating_report';

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
				<a
					href='#main-content'
					className='sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold focus:ring-4 focus:ring-indigo-400 z-50 transition-all'
				>
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
						{/* SEKCJA: Selektor poziomu analizy */}
						{!results && !reportData && (
							<AnalysisLevelSelector
								selectedLevel={analysisLevel}
								onLevelChange={handleLevelChange}
								disabled={isLoading}
							/>
						)}

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

						{/* SEKCJA: Informacja o poziomie podczas ładowania */}
						{isLoading && (
							<div className='bg-slate-800 rounded-xl p-4 border border-slate-700'>
								<div className='flex items-center gap-3'>
									<div className='animate-spin'>
										<svg
											className='w-5 h-5 text-indigo-400'
											fill='none'
											viewBox='0 0 24 24'
											stroke='currentColor'
										>
											<path
												strokeLinecap='round'
												strokeLinejoin='round'
												strokeWidth='2'
												d='M12 6v6m0 0v6m0-6h6m-6 0H6'
											></path>
										</svg>
									</div>
									<div>
										<p className='text-white font-semibold'>
											Analizuję dokument...
										</p>
										<p className='text-slate-400 text-sm'>
											Poziom:{' '}
											{analysisLevel === 'quick'
												? 'Szybki skan'
												: analysisLevel === 'standard'
												? 'Analiza standardowa'
												: 'Audyt profesjonalny'}
										</p>
									</div>
								</div>
							</div>
						)}

						<ErrorMessage error={error} />

						{/* SEKCJA: Wyniki z informacją o poziomie */}
						{results && (
							<>
								<div className='flex justify-end'>
									<span
										className={`
                                        px-4 py-2 rounded-full text-sm font-semibold
                                        ${
																					analysisLevel === 'quick'
																						? 'bg-indigo-600 text-white'
																						: analysisLevel === 'standard'
																						? 'bg-emerald-600 text-white'
																						: 'bg-purple-600 text-white'
																				}
                                    `}
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

								{/* SEKCJA: Opcja ponownej analizy */}
								{analysisLevel !== 'professional' && (
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
												onClick={() => {
													handleLevelChange(
														analysisLevel === 'quick'
															? 'standard'
															: 'professional'
													);
													handleSubmit();
												}}
												className='px-6 py-3 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 transition-all duration-200'
											>
												{analysisLevel === 'quick'
													? 'Analiza standardowa'
													: 'Audyt profesjonalny'}
											</button>
										</div>
									</div>
								)}
							</>
						)}

						{/* SEKCJA: Raport z informacją o poziomie */}
						{reportData && (
							<div id='report-section'>
								<div className='mb-4 flex justify-center'>
									<div className='bg-slate-800 rounded-full px-6 py-3 border border-slate-700'>
										<p className='text-sm text-slate-300'>
											Raport wygenerowany na podstawie:{' '}
											<span className='font-semibold text-white'>
												{reportData.analysis_level === 'quick'
													? 'Szybkiego skanu'
													: reportData.analysis_level === 'standard'
													? 'Analizy standardowej'
													: 'Audytu profesjonalnego'}
											</span>
										</p>
									</div>
								</div>

								<ReportView
									reportData={reportData}
									onDownload={handleDownloadReport}
								/>

								<div className='flex justify-center mt-4'>
									<button
										onClick={handleReset}
										className='px-6 py-3 bg-slate-700 text-white font-medium rounded-xl hover:bg-slate-600 transition-all duration-200 focus:ring-4 focus:ring-slate-400'
									>
										Analizuj kolejny plik
									</button>
								</div>
							</div>
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
