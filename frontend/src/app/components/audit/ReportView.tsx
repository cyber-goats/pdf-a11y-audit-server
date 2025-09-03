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
				? 'bg-indigo-600 text-white shadow-lg'
				: 'text-slate-300 hover:bg-slate-700 hover:text-white'
		}`}
		aria-current={activeTab === tab.id ? 'page' : undefined}
		role='tab'
		aria-selected={activeTab === tab.id}
	>
		<span className='flex items-center justify-center gap-2'>
			<span className='text-lg' aria-hidden='true'>
				{tab.icon}
			</span>
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
		<section className='bg-slate-800 rounded-2xl shadow-xl border border-slate-700 overflow-hidden'>
			<div className='bg-slate-900 p-8 border-b border-slate-700'>
				<div className='flex flex-col sm:flex-row justify-between items-center gap-4'>
					<div>
						<h2 className='text-3xl font-bold text-white mb-2'>
							Raport Dostępności
						</h2>
						<p className='text-slate-300 text-sm'>
							Wygenerowano:{' '}
							{new Date(reportData.metadata.analysis_date).toLocaleString(
								'pl-PL'
							)}
						</p>
					</div>
					<div className='flex gap-2'>
						<button
							onClick={() => onDownload('json')}
							aria-label='Pobierz raport w formacie JSON'
							className='px-5 py-2.5 bg-blue-900/50 text-blue-300 rounded-xl hover:bg-blue-900/70 border border-blue-700 transition-colors focus:ring-4 focus:ring-blue-400'
						>
							JSON
						</button>
						<button
							onClick={() => onDownload('html')}
							aria-label='Pobierz raport w formacie HTML'
							className='px-5 py-2.5 bg-emerald-900/50 text-emerald-300 rounded-xl hover:bg-emerald-900/70 border border-emerald-700 transition-colors focus:ring-4 focus:ring-emerald-400'
						>
							HTML
						</button>
						<button
							onClick={() => onDownload('pdf')}
							aria-label='Pobierz raport w formacie PDF'
							className='px-5 py-2.5 bg-red-900/50 text-red-300 rounded-xl hover:bg-red-900/70 border border-red-700 transition-colors focus:ring-4 focus:ring-red-400'
						>
							PDF
						</button>
					</div>
				</div>
			</div>

			<div className='px-8 pt-6'>
				<div
					className='flex gap-1 p-1 bg-slate-900 rounded-xl'
					role='tablist'
					aria-label='Sekcje raportu'
				>
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

			<div className='p-8' role='tabpanel' aria-labelledby={`tab-${activeTab}`}>
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
		</section>
	);
};
