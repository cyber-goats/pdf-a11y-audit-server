'use client';

import React, { useState, useRef } from 'react';

const PDFAuditTool = () => {
	const [file, setFile] = useState<File | null>(null);
	const [isLoading, setIsLoading] = useState(false);
	const [results, setResults] = useState<{
		filename: string;
		page_count: number;
		is_tagged: boolean;
		contains_text: boolean;
		extracted_text_preview?: string;
	} | null>(null);
	const [error, setError] = useState<string | null>(null);
	const fileInputRef = useRef<HTMLInputElement>(null);

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

	const handleSubmit = async (event: React.MouseEvent<HTMLButtonElement>) => {
		event.preventDefault();

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
			console.log('API URL:', apiUrl); // ← DODAJ TO
			console.log('Environment:', process.env.NEXT_PUBLIC_API_URL); // ← I TO

			const response = await fetch(`${apiUrl}/upload/pdf/`, {
				method: 'POST',
				body: formData,
			});

			if (!response.ok) {
				throw new Error('Błąd podczas przetwarzania pliku');
			}

			const data = await response.json();
			setResults(data);
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
		if (fileInputRef.current) {
			fileInputRef.current.value = '';
		}
	};

	return (
		<div className='min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100'>
			<a
				href='#main-content'
				className='sr-only focus:not-sr-only focus:absolute focus:top-6 focus:left-6 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg font-medium shadow-lg transform transition-all duration-200 hover:scale-105 focus:ring-4 focus:ring-blue-300 z-50'
			>
				Przejdź do głównej treści
			</a>

			<div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12'>
				<header className='text-center mb-16'>
					<div className='inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl mb-8 shadow-lg'>
						<svg
							className='w-10 h-10 text-white'
							fill='none'
							stroke='currentColor'
							viewBox='0 0 24 24'
						>
							<path
								strokeLinecap='round'
								strokeLinejoin='round'
								strokeWidth={2}
								d='M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
							/>
						</svg>
					</div>
					<h1 className='text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-indigo-900 bg-clip-text text-transparent mb-6 leading-tight px-4'>
						Audytor Dostępności PDF
					</h1>
					<p className='text-lg sm:text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed px-4'>
						Profesjonalne narzędzie do analizy dostępności dokumentów PDF.
						Sprawdź zgodność z standardami WCAG i otrzymaj szczegółową analizę.
					</p>
				</header>

				<main id='main-content' className='space-y-8'>
					<div className='bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 transform transition-all duration-300 hover:shadow-2xl hover:scale-[1.02]'>
						<div className='flex items-center gap-4 mb-6'>
							<div className='w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center'>
								<svg
									className='w-6 h-6 text-white'
									fill='none'
									stroke='currentColor'
									viewBox='0 0 24 24'
								>
									<path
										strokeLinecap='round'
										strokeLinejoin='round'
										strokeWidth={2}
										d='M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12'
									/>
								</svg>
							</div>
							<h2 className='text-2xl font-bold text-gray-900'>
								Wybierz plik PDF
							</h2>
						</div>

						<div className='space-y-6'>
							<div>
								<label
									htmlFor='pdf-upload'
									className='block text-lg font-semibold text-gray-800 mb-4'
								>
									Prześlij dokument do analizy
								</label>
								<div className='relative'>
									<input
										ref={fileInputRef}
										type='file'
										id='pdf-upload'
										accept='application/pdf,.pdf'
										onChange={handleFileSelect}
										disabled={isLoading}
										className='block w-full text-lg text-gray-700 border-2 border-gray-200 rounded-xl cursor-pointer bg-gray-50 transition-all duration-200 file:mr-6 file:py-4 file:px-8 file:rounded-l-xl file:border-0 file:text-lg file:font-semibold file:bg-gradient-to-r file:from-blue-600 file:to-indigo-600 file:text-white file:cursor-pointer hover:file:from-blue-700 hover:file:to-indigo-700 hover:border-blue-300 focus:outline-none focus:ring-4 focus:ring-blue-200 focus:border-blue-400 disabled:opacity-50 disabled:cursor-not-allowed file:transition-all file:duration-200 file:hover:shadow-lg'
										aria-describedby='file-help'
									/>
								</div>
								<p
									id='file-help'
									className='mt-3 text-gray-500 flex items-center gap-2'
								>
									<svg
										className='w-4 h-4'
										fill='none'
										stroke='currentColor'
										viewBox='0 0 24 24'
									>
										<path
											strokeLinecap='round'
											strokeLinejoin='round'
											strokeWidth={2}
											d='M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
										/>
									</svg>
									Obsługiwane formaty: PDF • Maksymalny rozmiar: 10MB
								</p>
							</div>

							{file && (
								<div className='p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200 transform transition-all duration-300'>
									<div className='flex items-center gap-4'>
										<div className='w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center'>
											<svg
												className='w-6 h-6 text-blue-600'
												fill='none'
												stroke='currentColor'
												viewBox='0 0 24 24'
											>
												<path
													strokeLinecap='round'
													strokeLinejoin='round'
													strokeWidth={2}
													d='M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
												/>
											</svg>
										</div>
										<div>
											<p className='font-semibold text-blue-900'>{file.name}</p>
											<p className='text-sm text-blue-600'>
												{(file.size / 1024 / 1024).toFixed(2)} MB
											</p>
										</div>
									</div>
								</div>
							)}

							<div className='flex gap-4'>
								<button
									type='button'
									onClick={handleSubmit}
									disabled={!file || isLoading}
									className='flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-lg font-semibold py-4 px-8 rounded-xl shadow-lg hover:from-blue-700 hover:to-indigo-700 hover:shadow-xl hover:scale-[1.02] focus:outline-none focus:ring-4 focus:ring-blue-300 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed disabled:transform-none transition-all duration-200 transform'
								>
									{isLoading ? (
										<span className='flex items-center justify-center gap-3'>
											<svg
												className='animate-spin h-5 w-5'
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
											Analizuję dokument...
										</span>
									) : (
										'Rozpocznij analizę'
									)}
								</button>

								{(file || results) && (
									<button
										type='button'
										onClick={handleReset}
										disabled={isLoading}
										className='px-8 py-4 text-gray-700 border-2 border-gray-300 rounded-xl font-semibold hover:bg-gray-50 hover:border-gray-400 hover:shadow-md hover:scale-[1.02] focus:outline-none focus:ring-4 focus:ring-gray-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none transition-all duration-200 transform'
									>
										Resetuj
									</button>
								)}
							</div>
						</div>
					</div>

					{isLoading && (
						<div
							className='bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-12 text-center transform transition-all duration-300'
							role='status'
							aria-live='polite'
						>
							<div className='inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl mb-6'>
								<svg
									className='animate-spin h-8 w-8 text-white'
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
							</div>
							<h3 className='text-xl font-semibold text-gray-900 mb-2'>
								Trwa analiza dokumentu
							</h3>
							<p className='text-gray-600'>
								Sprawdzamy dostępność i wyodrębniamy treść...
							</p>
						</div>
					)}

					{error && (
						<div
							className='bg-gradient-to-r from-red-50 to-pink-50 border-l-4 border-red-500 rounded-xl p-6 shadow-lg transform transition-all duration-300'
							role='alert'
						>
							<div className='flex items-center gap-4'>
								<div className='w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center'>
									<svg
										className='w-6 h-6 text-red-600'
										fill='none'
										stroke='currentColor'
										viewBox='0 0 24 24'
									>
										<path
											strokeLinecap='round'
											strokeLinejoin='round'
											strokeWidth={2}
											d='M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
										/>
									</svg>
								</div>
								<div>
									<h3 className='text-lg font-semibold text-red-800 mb-1'>
										Wystąpił błąd
									</h3>
									<p className='text-red-700'>{error}</p>
								</div>
							</div>
						</div>
					)}

					{results && (
						<div
							className='bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 transform transition-all duration-500'
							aria-live='polite'
						>
							<div className='flex items-center gap-4 mb-8'>
								<div className='w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center'>
									<svg
										className='w-6 h-6 text-white'
										fill='none'
										stroke='currentColor'
										viewBox='0 0 24 24'
									>
										<path
											strokeLinecap='round'
											strokeLinejoin='round'
											strokeWidth={2}
											d='M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z'
										/>
									</svg>
								</div>
								<h2 className='text-2xl font-bold text-gray-900'>
									Wyniki analizy dostępności
								</h2>
							</div>

							<div className='grid md:grid-cols-3 gap-6 mb-8'>
								<div className='bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200 transform transition-all duration-200 hover:shadow-lg hover:scale-[1.02]'>
									<h3 className='font-semibold text-blue-900 mb-3'>
										Informacje podstawowe
									</h3>
									<dl className='space-y-2'>
										<div>
											<dt className='text-sm font-medium text-blue-800'>
												Nazwa pliku:
											</dt>
											<dd className='text-blue-900 font-semibold'>
												{results.filename}
											</dd>
										</div>
										<div>
											<dt className='text-sm font-medium text-blue-800'>
												Liczba stron:
											</dt>
											<dd className='text-blue-900 font-semibold'>
												{results.page_count}
											</dd>
										</div>
									</dl>
								</div>

								<div className='bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-xl border border-purple-200 transform transition-all duration-200 hover:shadow-lg hover:scale-[1.02]'>
									<h3 className='font-semibold text-purple-900 mb-4'>
										Status dostępności
									</h3>
									<div className='space-y-4'>
										<div className='flex items-center gap-3'>
											<div
												className={`w-3 h-3 rounded-full flex-shrink-0 ${
													results.is_tagged ? 'bg-green-500' : 'bg-red-500'
												}`}
											></div>
											<span
												className={`font-medium ${
													results.is_tagged ? 'text-green-800' : 'text-red-800'
												}`}
											>
												{results.is_tagged
													? 'Dokument jest otagowany'
													: 'Dokument nie jest otagowany'}
											</span>
										</div>

										<div className='flex items-center gap-3'>
											<div
												className={`w-3 h-3 rounded-full flex-shrink-0 ${
													results.contains_text ? 'bg-green-500' : 'bg-red-500'
												}`}
											></div>
											<span
												className={`font-medium ${
													results.contains_text
														? 'text-green-800'
														: 'text-red-800'
												}`}
											>
												{results.contains_text
													? 'Zawiera tekst do odczytu'
													: 'Nie zawiera tekstu do odczytu'}
											</span>
										</div>
									</div>
								</div>

								<div className='bg-gradient-to-br from-emerald-50 to-green-50 p-6 rounded-xl border border-emerald-200 transform transition-all duration-200 hover:shadow-lg hover:scale-[1.02]'>
									<h3 className='font-semibold text-emerald-900 mb-4'>
										Ocena ogólna
									</h3>
									<div className='text-center'>
										<div
											className={`text-3xl font-bold mb-2 ${
												results.is_tagged && results.contains_text
													? 'text-green-600'
													: results.is_tagged || results.contains_text
													? 'text-yellow-600'
													: 'text-red-600'
											}`}
										>
											{results.is_tagged && results.contains_text
												? '✓'
												: results.is_tagged || results.contains_text
												? '⚠'
												: '✗'}
										</div>
										<p className='text-sm font-medium text-emerald-800'>
											{results.is_tagged && results.contains_text
												? 'Dostępny'
												: results.is_tagged || results.contains_text
												? 'Częściowo dostępny'
												: 'Wymaga poprawek'}
										</p>
									</div>
								</div>
							</div>

							{results.extracted_text_preview && (
								<div className='bg-gradient-to-r from-gray-50 to-slate-50 p-6 rounded-xl border border-gray-200 mb-8'>
									<h3 className='font-semibold text-gray-900 mb-4'>
										Podgląd wyodrębnionego tekstu
									</h3>
									<div className='bg-white p-4 rounded-lg border text-sm leading-relaxed max-h-64 overflow-y-auto shadow-inner'>
										<pre className='whitespace-pre-wrap font-mono text-gray-700'>
											{results.extracted_text_preview}
										</pre>
									</div>
									<p className='text-sm text-gray-500 mt-3'>
										Wyświetlane są pierwsze 500 znaków wyodrębnionego tekstu
									</p>
								</div>
							)}

							<div className='bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200'>
								<h3 className='font-semibold text-blue-900 mb-4'>
									Rekomendacje
								</h3>
								<ul className='space-y-3 text-blue-800'>
									{!results.is_tagged && (
										<li className='flex items-start gap-3'>
											<span className='w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0'></span>
											<span>
												Dokument powinien zostać otagowany dla lepszej
												dostępności
											</span>
										</li>
									)}
									{!results.contains_text && (
										<li className='flex items-start gap-3'>
											<span className='w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0'></span>
											<span>
												Dokument powinien zawierać tekst alternatywny lub być
												przetworzony przez OCR
											</span>
										</li>
									)}
									{results.is_tagged && results.contains_text && (
										<li className='flex items-start gap-3'>
											<span className='w-2 h-2 bg-green-600 rounded-full mt-2 flex-shrink-0'></span>
											<span className='text-green-800'>
												Dokument spełnia podstawowe kryteria dostępności
											</span>
										</li>
									)}
								</ul>
							</div>
						</div>
					)}
				</main>

				<footer className='text-center mt-20 pt-8 border-t border-gray-200'>
					<p className='text-gray-500 mb-2'>
						Narzędzie do audytu dostępności dokumentów PDF
					</p>
					<p className='text-sm text-gray-400'>Wspiera standardy WCAG 2.1 AA</p>
				</footer>
			</div>
		</div>
	);
};

export default PDFAuditTool;
