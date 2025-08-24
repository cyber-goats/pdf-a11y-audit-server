'use client';

import React, { useState } from 'react';
import type { ReportViewProps, TabButtonProps, TabId } from '@/app/types';
import { ScoreCard } from './ScoreCard';
import { KeyMetrics } from './KeyMetrics';
import { ScoringDetails } from './ScoringDetails';
import { PdfUaValidationErrors } from './PdfUaValidationErrors';
import { RecommendationsList } from './RecommendationsList';
import { REPORT_TABS } from '@/app/utils/constants';

const TabButton: React.FC<TabButtonProps> = ({ tab, activeTab, onClick }) => (
	<button
		key={tab.id}
		onClick={() => onClick(tab.id)}
		className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all duration-200 ${
			activeTab === tab.id
				? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
				: 'text-gray-300 hover:bg-white/10'
		}`}
	>
		<span className='flex items-center justify-center gap-2'>
			<span className='text-lg'>{tab.icon}</span>
			<span className='hidden sm:inline'>{tab.label}</span>
		</span>
	</button>
);

export const ReportView: React.FC<ReportViewProps> = ({
	reportData,
	onDownload,
}) => {
	const [activeTab, setActiveTab] = useState<TabId>('summary');

	return (
		<div className='bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-3xl border border-white/20 shadow-2xl overflow-hidden'>
			<div className='bg-gradient-to-r from-purple-600/20 to-pink-600/20 p-8 border-b border-white/10'>
				<div className='flex flex-col sm:flex-row justify-between items-center gap-4'>
					<div>
						<h2 className='text-3xl font-bold text-white mb-2'>
							Raport Dostępności
						</h2>
						<p className='text-gray-300 text-sm'>
							Wygenerowano:{' '}
							{new Date(reportData.metadata.analysis_date).toLocaleString(
								'pl-PL'
							)}
						</p>
					</div>
					<div className='flex gap-2'>
						<button
							onClick={() => onDownload('json')}
							className='px-5 py-2.5 bg-blue-500/20 text-blue-300 rounded-xl hover:bg-blue-500/30 border border-blue-500/30'
						>
							JSON
						</button>
						<button
							onClick={() => onDownload('html')}
							className='px-5 py-2.5 bg-emerald-500/20 text-emerald-300 rounded-xl hover:bg-emerald-500/30 border border-emerald-500/30'
						>
							HTML
						</button>
						<button
							onClick={() => onDownload('pdf')}
							className='px-5 py-2.5 bg-red-500/20 text-red-300 rounded-xl hover:bg-red-500/30 border border-red-500/30'
						>
							PDF
						</button>
					</div>
				</div>
			</div>

			<div className='px-8 pt-6'>
				<div className='flex gap-1 p-1 bg-white/5 rounded-xl'>
					{REPORT_TABS.map((tab) => (
						<TabButton
							key={tab.id}
							tab={tab}
							activeTab={activeTab}
							onClick={setActiveTab}
						/>
					))}
				</div>
			</div>

			<div className='p-8'>
				{activeTab === 'summary' && (
					<div className='space-y-6 animate-fadeIn'>
						<ScoreCard
							score={reportData.accessibility_score}
							filename={reportData.metadata.filename}
						/>
						<KeyMetrics
							validation={reportData.pdf_ua_validation}
							metadata={reportData.metadata}
						/>
					</div>
				)}

				{activeTab === 'details' && (
					<div className='space-y-6 animate-fadeIn'>
						<ScoringDetails details={reportData.accessibility_score.details} />
						<PdfUaValidationErrors
							failedRules={reportData.pdf_ua_validation.failed_rules}
						/>
					</div>
				)}

				{activeTab === 'recommendations' && (
					<div className='animate-fadeIn'>
						<RecommendationsList recommendations={reportData.recommendations} />
					</div>
				)}
			</div>
		</div>
	);
};
