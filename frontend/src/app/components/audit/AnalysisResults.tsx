import React from 'react';
import { CheckIcon, XIcon } from './Icons';
import type { AnalysisResultsProps } from '@/app/types';


export const AnalysisResults: React.FC<AnalysisResultsProps> = ({
	results,
	getAccessibilityScore,
	getScoreColor,
}) => (
	<div className='bg-white/10 backdrop-blur-md rounded-3xl p-8 border border-white/20 shadow-2xl'>
		<div className='flex items-center justify-between mb-8'>
			<h2 className='text-2xl font-bold text-white flex items-center gap-3'>
				<svg
					className='w-8 h-8 text-purple-400'
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
				Wyniki analizy
			</h2>
			<div
				className={`text-5xl font-bold ${getScoreColor(
					getAccessibilityScore()
				)}`}
			>
				{getAccessibilityScore()}%
			</div>
		</div>
		<div className='grid md:grid-cols-3 gap-6 mb-8'>
			<div className='bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10'>
				<h3 className='font-semibold text-white mb-4'>Dokument</h3>
				<dl className='space-y-3'>
					<div>
						<dt className='text-sm text-gray-400'>Nazwa</dt>
						<dd className='text-white font-medium truncate'>
							{results.filename}
						</dd>
					</div>
					<div>
						<dt className='text-sm text-gray-400'>Strony</dt>
						<dd className='text-white font-medium'>{results.page_count}</dd>
					</div>
				</dl>
			</div>
			<div className='bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10'>
				<h3 className='font-semibold text-white mb-4'>Struktura</h3>
				<div className='space-y-3'>
					<div className='flex items-center justify-between'>
						<span className='text-gray-300'>Tagi</span>
						{results.is_tagged ? <CheckIcon /> : <XIcon />}
					</div>
					<div className='flex items-center justify-between'>
						<span className='text-gray-300'>Tekst</span>
						{results.contains_text ? <CheckIcon /> : <XIcon />}
					</div>
				</div>
			</div>
			<div className='bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10'>
				<h3 className='font-semibold text-white mb-4'>Multimedia</h3>
				<div className='space-y-3'>
					<div className='flex items-center justify-between'>
						<span className='text-gray-300'>Obrazy</span>
						<span className='text-white font-medium'>
							{results.image_info?.image_count || 0}
						</span>
					</div>
					<div className='flex items-center justify-between'>
						<span className='text-gray-300'>Z ALT</span>
						<span className='text-green-400 font-medium'>
							{results.image_info?.images_with_alt || 0}
						</span>
					</div>
				</div>
			</div>
		</div>
		<div className='bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10'>
			<div className='flex items-center justify-between mb-3'>
				<span className='text-white font-semibold'>Poziom dostępności</span>
				<span className={`font-bold ${getScoreColor(getAccessibilityScore())}`}>
					{getAccessibilityScore() >= 80
						? 'Wysoki'
						: getAccessibilityScore() >= 50
						? 'Średni'
						: 'Niski'}
				</span>
			</div>
			<div className='h-4 bg-white/10 rounded-full overflow-hidden'>
				<div
					className={`h-full transition-all duration-1000 ease-out ${
						getAccessibilityScore() >= 80
							? 'bg-gradient-to-r from-green-500 to-emerald-500'
							: getAccessibilityScore() >= 50
							? 'bg-gradient-to-r from-yellow-500 to-amber-500'
							: 'bg-gradient-to-r from-red-500 to-rose-500'
					}`}
					style={{ width: `${getAccessibilityScore()}%` }}
				/>
			</div>
		</div>
	</div>
);
