import React, { useState } from 'react';
import type { ReportViewProps } from '@/app/types';

export const ReportView: React.FC<ReportViewProps> = ({
	reportData,
	onDownload,
}) => {
	const [activeTab, setActiveTab] = useState<
		'summary' | 'details' | 'recommendations'
	>('summary');

	const getPriorityColor = (priority: string) => {
		switch (priority) {
			case 'high':
				return 'text-red-400 bg-red-400/10';
			case 'medium':
				return 'text-yellow-400 bg-yellow-400/10';
			case 'low':
				return 'text-green-400 bg-green-400/10';
			default:
				return 'text-gray-400 bg-gray-400/10';
		}
	};

	return (
		<div className='bg-white/10 backdrop-blur-md rounded-3xl p-8 border border-white/20 shadow-2xl'>
			{/* Header with download buttons */}
			<div className='flex justify-between items-center mb-8'>
				<h2 className='text-2xl font-bold text-white'>
					Szczegółowy Raport Dostępności
				</h2>
				<div className='flex gap-2'>
					<button
						onClick={() => onDownload('json')}
						className='px-4 py-2 bg-blue-600/20 text-blue-400 rounded-lg hover:bg-blue-600/30 transition-colors'
					>
						📥 JSON
					</button>
					<button
						onClick={() => onDownload('html')}
						className='px-4 py-2 bg-green-600/20 text-green-400 rounded-lg hover:bg-green-600/30 transition-colors'
					>
						📥 HTML
					</button>
				</div>
			</div>

			{/* Tabs */}
			<div className='flex gap-2 mb-6'>
				<button
					onClick={() => setActiveTab('summary')}
					className={`px-6 py-3 rounded-lg font-medium transition-all ${
						activeTab === 'summary'
							? 'bg-purple-600 text-white'
							: 'bg-white/10 text-gray-300 hover:bg-white/20'
					}`}
				>
					Podsumowanie
				</button>
				<button
					onClick={() => setActiveTab('details')}
					className={`px-6 py-3 rounded-lg font-medium transition-all ${
						activeTab === 'details'
							? 'bg-purple-600 text-white'
							: 'bg-white/10 text-gray-300 hover:bg-white/20'
					}`}
				>
					Szczegóły
				</button>
				<button
					onClick={() => setActiveTab('recommendations')}
					className={`px-6 py-3 rounded-lg font-medium transition-all ${
						activeTab === 'recommendations'
							? 'bg-purple-600 text-white'
							: 'bg-white/10 text-gray-300 hover:bg-white/20'
					}`}
				>
					Rekomendacje
				</button>
			</div>

			{/* Tab Content */}
			{activeTab === 'summary' && (
				<div className='space-y-6'>
					{/* Overall result */}
					<div className='bg-white/5 rounded-2xl p-6 text-center'>
						<div
							className={`text-6xl font-bold mb-2 ${
								reportData.accessibility_score.percentage >= 80
									? 'text-green-400'
									: reportData.accessibility_score.percentage >= 50
									? 'text-yellow-400'
									: 'text-red-400'
							}`}
						>
							{reportData.accessibility_score.percentage}%
						</div>
						<p className='text-white text-lg'>
							Poziom dostępności: {reportData.accessibility_score.level}
						</p>
					</div>

					{/* Metrics */}
					<div className='grid md:grid-cols-3 gap-4'>
						<div className='bg-white/5 rounded-xl p-4'>
							<p className='text-gray-400 text-sm'>Plik</p>
							<p className='text-white font-medium'>
								{reportData.metadata.filename}
							</p>
						</div>
						<div className='bg-white/5 rounded-xl p-4'>
							<p className='text-gray-400 text-sm'>Zgodność PDF/UA</p>
							<p
								className={`font-medium ${
									reportData.pdf_ua_validation.is_compliant
										? 'text-green-400'
										: 'text-red-400'
								}`}
							>
								{reportData.pdf_ua_validation.is_compliant ? 'Tak' : 'Nie'}
							</p>
						</div>
						<div className='bg-white/5 rounded-xl p-4'>
							<p className='text-gray-400 text-sm'>Błędy PDF/UA</p>
							<p className='text-white font-medium'>
								{reportData.pdf_ua_validation.failed_rules_count}
							</p>
						</div>
					</div>
				</div>
			)}

			{activeTab === 'details' && (
				<div className='space-y-6'>
					{/* Details of the scoring system */}
					<div className='bg-white/5 rounded-2xl p-6'>
						<h3 className='text-white font-semibold mb-4'>
							Szczegóły punktacji
						</h3>
						<div className='space-y-3'>
							{reportData.accessibility_score.details.map((detail, idx) => (
								<div key={idx} className='flex items-center justify-between'>
									<span className='text-gray-300'>{detail.criterion}</span>
									<div className='flex items-center gap-4'>
										<div className='text-white font-medium'>
											{detail.points}/{detail.max}
										</div>
										<div className='w-32 h-2 bg-white/10 rounded-full overflow-hidden'>
											<div
												className={`h-full transition-all ${
													detail.points === detail.max
														? 'bg-green-500'
														: detail.points > 0
														? 'bg-yellow-500'
														: 'bg-red-500'
												}`}
												style={{
													width: `${(detail.points / detail.max) * 100}%`,
												}}
											/>
										</div>
									</div>
								</div>
							))}
						</div>
					</div>

					{/* PDF/UA errors */}
					{reportData.pdf_ua_validation.failed_rules.length > 0 && (
						<div className='bg-white/5 rounded-2xl p-6'>
							<h3 className='text-white font-semibold mb-4'>
								Błędy zgodności PDF/UA
							</h3>
							<div className='space-y-2 max-h-60 overflow-y-auto'>
								{reportData.pdf_ua_validation.failed_rules.map((rule, idx) => (
									<div key={idx} className='bg-white/5 rounded-lg p-3'>
										<p className='text-xs text-gray-400'>
											Klauzula {rule.clause}
										</p>
										<p className='text-white text-sm'>{rule.description}</p>
									</div>
								))}
							</div>
						</div>
					)}
				</div>
			)}

			{activeTab === 'recommendations' && (
				<div className='space-y-4'>
					{reportData.recommendations.map((rec, idx) => (
						<div key={idx} className='bg-white/5 rounded-xl p-4'>
							<div className='flex items-start gap-3'>
								<span
									className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(
										rec.priority
									)}`}
								>
									{rec.priority.toUpperCase()}
								</span>
								<div className='flex-1'>
									<p className='text-white font-medium mb-1'>{rec.issue}</p>
									<p className='text-gray-300 text-sm'>{rec.recommendation}</p>
								</div>
							</div>
						</div>
					))}
				</div>
			)}
		</div>
	);
};
