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
			const response = await fetch('http://localhost:8000/upload/pdf/', {
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
		<div className='min-h-screen bg-white'>
			{/* Skip to main content link - for keyboard users */}
			<a
				href='#main-content'
				className='sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-blue-600 text-white px-4 py-2 rounded-md z-50'
			>
				Przejdź do głównej treści
			</a>

			<div className='max-w-4xl mx-auto px-4 py-8'>
				{/* Header */}
				<header className='text-center mb-12'>
					<h1 className='text-4xl font-bold text-gray-900 mb-4'>
						Audytor Dostępności PDF
					</h1>
					<p className='text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed'>
						Narzędzie do analizy dostępności dokumentów PDF. Sprawdź czy Twój
						dokument zawiera odpowiednie znaczniki i treść tekstową.
					</p>
				</header>

				{/* Main content */}
				<main id='main-content'>
					{/* Upload Form */}
					<section className='bg-gray-50 rounded-lg p-8 mb-8 border-2 border-gray-200'>
						<div className='space-y-6'>
							<div>
								<label
									htmlFor='pdf-upload'
									className='block text-lg font-semibold text-gray-900 mb-3'
								>
									Wybierz plik PDF do analizy
								</label>
								<input
									ref={fileInputRef}
									type='file'
									id='pdf-upload'
									accept='application/pdf,.pdf'
									onChange={handleFileSelect}
									disabled={isLoading}
									className='block w-full text-lg text-gray-900 border-2 border-gray-300 rounded-lg cursor-pointer bg-white
                           file:mr-4 file:py-3 file:px-6 file:rounded-l-lg file:border-0 file:text-lg file:font-semibold
                           file:bg-blue-600 file:text-white file:cursor-pointer
                           hover:file:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300
                           disabled:opacity-50 disabled:cursor-not-allowed'
									aria-describedby='file-help'
								/>
								<p id='file-help' className='mt-2 text-gray-600'>
									Obsługiwane formaty: PDF. Maksymalny rozmiar pliku: 10MB.
								</p>
							</div>

							{file && (
								<div className='p-4 bg-blue-50 rounded-lg border border-blue-200'>
									<p className='text-blue-800'>
										<strong>Wybrany plik:</strong> {file.name}
										<span className='ml-2 text-sm'>
											({(file.size / 1024 / 1024).toFixed(2)} MB)
										</span>
									</p>
								</div>
							)}

							<div className='flex gap-4'>
								<button
									type='button'
									onClick={handleSubmit}
									disabled={!file || isLoading}
									className='flex-1 bg-blue-600 text-white text-lg font-semibold py-4 px-8 rounded-lg
                           hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300
                           disabled:bg-gray-400 disabled:cursor-not-allowed
                           transition-colors duration-200'
									aria-describedby='submit-help'
								>
									{isLoading ? 'Analizuję dokument...' : 'Rozpocznij analizę'}
								</button>

								{(file || results) && (
									<button
										type='button'
										onClick={handleReset}
										disabled={isLoading}
										className='px-6 py-4 text-gray-700 border-2 border-gray-300 rounded-lg
                             hover:bg-gray-50 focus:outline-none focus:ring-4 focus:ring-gray-300
                             disabled:opacity-50 disabled:cursor-not-allowed
                             transition-colors duration-200'
									>
										Resetuj
									</button>
								)}
							</div>
							<p id='submit-help' className='text-sm text-gray-600'>
								Analiza może potrwać kilka sekund, w zależności od rozmiaru
								dokumentu.
							</p>
						</div>
					</section>

					{/* Loading State */}
					{isLoading && (
						<div className='text-center py-12' role='status' aria-live='polite'>
							<div className='inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4'></div>
							<p className='text-lg text-gray-600'>Trwa analiza dokumentu...</p>
						</div>
					)}

					{/* Error Display */}
					{error && (
						<div
							className='bg-red-50 border-2 border-red-200 rounded-lg p-6 mb-8'
							role='alert'
						>
							<h2 className='text-lg font-semibold text-red-800 mb-2'>
								Wystąpił błąd
							</h2>
							<p className='text-red-700'>{error}</p>
						</div>
					)}

					{/* Results Display */}
					{results && (
						<section
							className='bg-white border-2 border-gray-200 rounded-lg p-8'
							aria-live='polite'
						>
							<h2 className='text-2xl font-bold text-gray-900 mb-6'>
								Wyniki analizy dostępności
							</h2>

							{/* Basic Info */}
							<div className='grid md:grid-cols-2 gap-6 mb-8'>
								<div className='bg-gray-50 p-4 rounded-lg'>
									<h3 className='font-semibold text-gray-900 mb-2'>
										Informacje podstawowe
									</h3>
									<dl className='space-y-1'>
										<div>
											<dt className='inline font-medium'>Nazwa pliku:</dt>
											<dd className='inline ml-2'>{results.filename}</dd>
										</div>
										<div>
											<dt className='inline font-medium'>Liczba stron:</dt>
											<dd className='inline ml-2'>{results.page_count}</dd>
										</div>
									</dl>
								</div>

								{/* Accessibility Status */}
								<div className='bg-gray-50 p-4 rounded-lg'>
									<h3 className='font-semibold text-gray-900 mb-2'>
										Status dostępności
									</h3>
									<div className='space-y-3'>
										<div className='flex items-center gap-3'>
											<div
												className={`w-4 h-4 rounded-full flex-shrink-0 ${
													results.is_tagged ? 'bg-green-500' : 'bg-red-500'
												}`}
												aria-hidden='true'
											></div>
											<span
												className={
													results.is_tagged ? 'text-green-800' : 'text-red-800'
												}
											>
												{results.is_tagged
													? 'Dokument jest otagowany'
													: 'Dokument nie jest otagowany'}
											</span>
										</div>

										<div className='flex items-center gap-3'>
											<div
												className={`w-4 h-4 rounded-full flex-shrink-0 ${
													results.contains_text ? 'bg-green-500' : 'bg-red-500'
												}`}
												aria-hidden='true'
											></div>
											<span
												className={
													results.contains_text
														? 'text-green-800'
														: 'text-red-800'
												}
											>
												{results.contains_text
													? 'Zawiera tekst do odczytu'
													: 'Nie zawiera tekstu do odczytu'}
											</span>
										</div>
									</div>
								</div>
							</div>

							{/* Text Preview */}
							{results.extracted_text_preview && (
								<div className='bg-gray-50 p-6 rounded-lg'>
									<h3 className='font-semibold text-gray-900 mb-3'>
										Podgląd wyodrębnionego tekstu
									</h3>
									<div className='bg-white p-4 rounded border text-sm leading-relaxed max-h-64 overflow-y-auto'>
										<pre className='whitespace-pre-wrap font-mono'>
											{results.extracted_text_preview}
										</pre>
									</div>
									<p className='text-sm text-gray-600 mt-2'>
										Wyświetlane są pierwsze 500 znaków wyodrębnionego tekstu.
									</p>
								</div>
							)}

							{/* Recommendations */}
							<div className='mt-8 p-6 bg-blue-50 rounded-lg border border-blue-200'>
								<h3 className='font-semibold text-blue-900 mb-3'>
									Rekomendacje
								</h3>
								<ul className='space-y-2 text-blue-800'>
									{!results.is_tagged && (
										<li>
											• Dokument powinien zostać otagowany dla lepszej
											dostępności
										</li>
									)}
									{!results.contains_text && (
										<li>
											• Dokument powinien zawierać tekst alternatywny lub być
											przetworzony przez OCR
										</li>
									)}
									{results.is_tagged && results.contains_text && (
										<li>• Dokument spełnia podstawowe kryteria dostępności</li>
									)}
								</ul>
							</div>
						</section>
					)}
				</main>

				{/* Footer */}
				<footer className='text-center mt-16 pt-8 border-t border-gray-200'>
					<p className='text-gray-600'>
						Narzędzie do audytu dostępności dokumentów PDF
					</p>
				</footer>
			</div>
		</div>
	);
};

export default PDFAuditTool;
