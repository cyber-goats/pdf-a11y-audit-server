import React from 'react';
import type { Results } from './AnalysisResults';
import { UploadIcon, FileIcon, LoaderIcon, SparklesIcon } from './Icons';

interface FileUploadProps {
	file: File | null;
	isLoading: boolean;
	isDragging: boolean;
	progress: number;
	results: Results | null;
	dropZoneRef: React.Ref<HTMLDivElement>;
	fileInputRef: React.Ref<HTMLInputElement>;
	handleDragEnter: (e: React.DragEvent<HTMLDivElement>) => void;
	handleDragOver: (e: React.DragEvent<HTMLDivElement>) => void;
	handleDragLeave: (e: React.DragEvent<HTMLDivElement>) => void;
	handleDrop: (e: React.DragEvent<HTMLDivElement>) => void;
	handleFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
	handleSubmit: () => void;
	handleReset: () => void;
	formatFileSize: (bytes: number) => string;
}

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
	<div className='bg-white/10 backdrop-blur-md rounded-3xl p-8 border border-white/20 shadow-2xl'>
		<div
			ref={dropZoneRef}
			onDragEnter={handleDragEnter}
			onDragOver={handleDragOver}
			onDragLeave={handleDragLeave}
			onDrop={handleDrop}
			className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
				isDragging
					? 'border-purple-400 bg-purple-50/10'
					: file
					? 'border-green-400 bg-green-50/10'
					: 'border-gray-400 hover:border-purple-400 bg-white/5'
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
				<>
					<div className='mb-6'>
						<div className='inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-purple-600 to-pink-600 rounded-2xl shadow-lg mb-4'>
							<UploadIcon />
						</div>
					</div>
					<label
						htmlFor='pdf-upload'
						className='inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 cursor-pointer'
					>
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
								d='M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12'
							/>
						</svg>
						Wybierz plik PDF
					</label>
					<p className='mt-4 text-gray-300'>
						lub przeciągnij i upuść plik tutaj
					</p>
					<p id='upload-help' className='mt-2 text-sm text-gray-400'>
						Maksymalny rozmiar: 10MB • Format: PDF
					</p>
				</>
			) : (
				<div className='space-y-4'>
					<div className='inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl shadow-lg'>
						<FileIcon />
					</div>
					<div className='bg-white/10 backdrop-blur-sm rounded-xl p-4 max-w-md mx-auto'>
						<p className='font-semibold text-white text-lg'>{file.name}</p>
						<p className='text-gray-300 text-sm mt-1'>
							{formatFileSize(file.size)}
						</p>
					</div>
					<button
						onClick={() =>
							(
								fileInputRef as React.RefObject<HTMLInputElement>
							).current?.click()
						}
						className='text-purple-400 hover:text-purple-300 text-sm font-medium transition-colors'
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
				className='flex-1 inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-200'
			>
				{isLoading ? (
					<>
						<LoaderIcon /> Analizuję...
					</>
				) : (
					<>
						<SparklesIcon /> Rozpocznij analizę
					</>
				)}
			</button>
			{(file || results) && (
				<button
					onClick={handleReset}
					disabled={isLoading}
					className='px-8 py-4 bg-white/10 backdrop-blur-sm text-white font-semibold rounded-xl border border-white/20 hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-200'
				>
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
							d='M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15'
						/>
					</svg>
				</button>
			)}
		</div>
		{isLoading && (
			<div className='mt-6'>
				<div className='h-2 bg-white/10 rounded-full overflow-hidden'>
					<div
						className='h-full bg-gradient-to-r from-purple-600 to-pink-600 transition-all duration-300 ease-out'
						style={{ width: `${progress}%` }}
					/>
				</div>
				<p className='text-center text-sm text-gray-300 mt-2'>
					Analizuję dokument... {progress}%
				</p>
			</div>
		)}
	</div>
);
