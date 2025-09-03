import React from 'react';
import type { FileUploadProps } from '@/app/types';
import { UploadIcon, FileIcon, LoaderIcon, SparklesIcon } from './Icons';

export const FileUpload: React.FC<FileUploadProps> = ({
	file,
	isLoading,
	isDragging,
	progress,
	results,
	dropZoneRef,
	fileInputRef,
	handleDragEnter,
	handleDragOver,
	handleDragLeave,
	handleDrop,
	handleFileSelect,
	handleSubmit,
	handleReset,
	formatFileSize,
}) => (
	<section className='bg-slate-800 rounded-2xl p-8 shadow-xl border border-slate-700'>
		<h2 className='sr-only'>Wybór pliku do analizy</h2>
		<div
			ref={dropZoneRef}
			onDragEnter={handleDragEnter}
			onDragOver={handleDragOver}
			onDragLeave={handleDragLeave}
			onDrop={handleDrop}
			className={`relative border-2 border-dashed rounded-xl p-12 transition-all duration-300 ${
				isDragging
					? 'border-indigo-400 bg-indigo-950/30'
					: file
					? 'border-green-500 bg-green-950/20'
					: 'border-slate-600 hover:border-slate-500 bg-slate-900/50'
			}`}
		>
			<input
				ref={fileInputRef}
				type='file'
				id='pdf-upload'
				accept='application/pdf,.pdf'
				onChange={handleFileSelect}
				disabled={isLoading}
				className='sr-only'
				aria-describedby='upload-help'
			/>
			{!file ? (
				<div className='flex flex-col items-center justify-center'>
					<div className='mb-6'>
						<div className='inline-flex items-center justify-center w-20 h-20 bg-indigo-600 rounded-2xl shadow-lg'>
							<UploadIcon />
						</div>
					</div>

					<label
						htmlFor='pdf-upload'
						className='inline-flex items-center justify-center gap-2 px-12 py-4 bg-indigo-600 text-white font-semibold rounded-xl shadow-lg hover:bg-indigo-700 transform hover:scale-105 transition-all duration-200 cursor-pointer focus:ring-4 focus:ring-indigo-400'
						style={{ minWidth: 'fit-content' }}
					>
						<svg
							className='w-5 h-5 flex-shrink-0'
							fill='none'
							stroke='currentColor'
							viewBox='0 0 24 24'
							aria-hidden='true'
						>
							<path
								strokeLinecap='round'
								strokeLinejoin='round'
								strokeWidth={2}
								d='M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12'
							/>
						</svg>
						<span>Wybierz plik PDF</span>
					</label>

					<p className='mt-4 text-slate-200 font-medium text-center'>
						lub przeciągnij i upuść plik tutaj
					</p>
					<p
						id='upload-help'
						className='mt-2 text-sm text-slate-400 text-center'
					>
						Maksymalny rozmiar: 10MB • Format: PDF
					</p>
				</div>
			) : (
				<div className='flex flex-col items-center justify-center'>
					<div className='mb-4'>
						<div className='inline-flex items-center justify-center w-20 h-20 bg-green-600 rounded-2xl shadow-lg'>
							<FileIcon />
						</div>
					</div>

					<div className='bg-slate-700 rounded-xl p-4 max-w-md mx-auto text-center'>
						<p className='font-semibold text-white text-lg'>{file.name}</p>
						<p className='text-slate-300 text-sm mt-1'>
							{formatFileSize(file.size)}
						</p>
					</div>

					<button
						onClick={() =>
							(
								fileInputRef as React.RefObject<HTMLInputElement>
							).current?.click()
						}
						className='mt-4 text-indigo-400 hover:text-indigo-300 text-sm font-medium transition-colors underline focus:ring-2 focus:ring-indigo-400 focus:ring-offset-2 focus:ring-offset-slate-800 rounded px-2 py-1'
					>
						Zmień plik
					</button>
				</div>
			)}
		</div>

		<div className='flex gap-4 mt-8'>
			<button
				onClick={handleSubmit}
				disabled={!file || isLoading}
				aria-busy={isLoading}
				className='flex-1 inline-flex items-center justify-center gap-2 px-8 py-4 bg-indigo-600 text-white font-semibold rounded-xl shadow-lg hover:bg-indigo-700 disabled:bg-slate-700 disabled:text-slate-500 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-200 focus:ring-4 focus:ring-indigo-400'
			>
				{isLoading ? (
					<>
						<LoaderIcon />
						<span>Analizuję...</span>
					</>
				) : (
					<>
						<SparklesIcon />
						<span>Rozpocznij analizę</span>
					</>
				)}
			</button>

			{(file || results) && (
				<button
					onClick={handleReset}
					disabled={isLoading}
					className='inline-flex items-center justify-center px-8 py-4 bg-slate-700 text-white font-semibold rounded-xl hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-200 focus:ring-4 focus:ring-slate-400'
				>
					<svg
						className='w-5 h-5'
						fill='none'
						stroke='currentColor'
						viewBox='0 0 24 24'
						aria-label='Resetuj'
					>
						<path
							strokeLinecap='round'
							strokeLinejoin='round'
							strokeWidth={2}
							d='M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15'
						/>
					</svg>
				</button>
			)}
		</div>

		{isLoading && (
			<div className='mt-6'>
				<div
					className='h-2 bg-slate-700 rounded-full overflow-hidden'
					role='progressbar'
					aria-valuenow={progress}
					aria-valuemin={0}
					aria-valuemax={100}
					aria-label='Postęp analizy dokumentu'
				>
					<div
						className='h-full bg-indigo-600 transition-all duration-300 ease-out'
						style={{ width: `${progress}%` }}
					/>
				</div>
				<p className='text-center text-sm text-slate-300 mt-2'>
					Analizuję dokument... {progress}%
				</p>
			</div>
		)}
	</section>
);
