import React, { useState } from 'react';
import type { ReportViewProps, TabId } from '@/app/types';

export const ReportView: React.FC<ReportViewProps> = ({
	reportData,
	onDownload,
}) => {
	const [activeTab, setActiveTab] = useState<TabId>('summary');

	const getPriorityColor = (priority: string) => {
		switch (priority) {
			case 'high':
				return 'text-red-400 bg-red-500/10 border-red-500/30';
			case 'medium':
				return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
			case 'low':
				return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
			default:
				return 'text-gray-400 bg-gray-500/10 border-gray-500/30';
		}
	};

	const getPriorityIcon = (priority: string) => {
		switch (priority) {
			case 'high':
				return '⚠️';
			case 'medium':
				return '⚡';
			case 'low':
				return 'ℹ️';
			default:
				return '📌';
		}
	};

	const getScoreGradient = (percentage: number) => {
		if (percentage >= 80) return 'from-emerald-400 to-green-500';
		if (percentage >= 50) return 'from-amber-400 to-yellow-500';
		return 'from-red-400 to-rose-500';
	};

	const tabs: { id: TabId; label: string; icon: string }[] = [
		{ id: 'summary', label: 'Podsumowanie', icon: '📊' },
		{ id: 'details', label: 'Szczegóły', icon: '🔍' },
		{ id: 'recommendations', label: 'Rekomendacje', icon: '💡' },
	];

	return (
		<div className='bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-3xl border border-white/20 shadow-2xl overflow-hidden'>
			{/* Professional Header */}
			<div className='bg-gradient-to-r from-purple-600/20 to-pink-600/20 backdrop-blur-sm p-8 border-b border-white/10'>
				<div className='flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4'>
					<div>
						<h2 className='text-3xl font-bold text-white mb-2 flex items-center gap-3'>
							<span className='p-2 bg-white/10 rounded-lg'>
								<svg
									className='w-6 h-6'
									fill='none'
									stroke='currentColor'
									viewBox='0 0 24 24'
								>
									<path
										strokeLinecap='round'
										strokeLinejoin='round'
										strokeWidth={2}
										d='M9 17v1a1 1 0 001 1h4a1 1 0 001-1v-1m3-2V8a2 2 0 00-2-2H8a2 2 0 00-2 2v8m5-5h4'
									/>
								</svg>
							</span>
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
							className='group px-5 py-2.5 bg-blue-500/20 text-blue-300 rounded-xl hover:bg-blue-500/30 transition-all duration-200 border border-blue-500/30 hover:scale-105'
							aria-label='Pobierz raport w formacie JSON'
						>
							<span className='flex items-center gap-2'>
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
										d='M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4'
									/>
								</svg>
								JSON
							</span>
						</button>
						<button
							onClick={() => onDownload('html')}
							className='group px-5 py-2.5 bg-emerald-500/20 text-emerald-300 rounded-xl hover:bg-emerald-500/30 transition-all duration-200 border border-emerald-500/30 hover:scale-105'
							aria-label='Pobierz raport w formacie HTML'
						>
							<span className='flex items-center gap-2'>
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
										d='M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4'
									/>
								</svg>
								HTML
							</span>
						</button>
                            <button        onClick={() => onDownload('pdf')}
       className='group px-5 py-2.5 bg-red-500/20 text-red-300 rounded-xl hover:bg-red-500/30 transition-all duration-200 border border-red-500/30 hover:scale-105'
        aria-label='Pobierz raport w formacie PDF'
    >
        <span className='flex items-center gap-2'>
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
                    d='M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4'
                />
            </svg>
            PDF
        </span>
    </button>
					</div>
				</div>
			</div>

			{/* Enhanced Tabs */}
			<div className='px-8 pt-6'>
				<div className='flex gap-1 p-1 bg-white/5 rounded-xl backdrop-blur-sm'>
					{tabs.map((tab) => (
						<button
							key={tab.id}
							onClick={() => setActiveTab(tab.id)}
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
					))}
				</div>
			</div>

			{/* Tab Content with padding */}
			<div className='p-8'>
				{activeTab === 'summary' && (
					<div className='space-y-6 animate-fadeIn'>
						{/* Score Card with gradient background */}
						<div className='relative bg-gradient-to-br from-white/10 to-white/5 rounded-2xl p-8 overflow-hidden'>
							<div className='absolute inset-0 bg-gradient-to-br from-purple-600/10 to-pink-600/10'></div>
							<div className='relative text-center'>
								<div className='inline-flex items-center justify-center w-32 h-32 mx-auto mb-4'>
									<svg className='absolute inset-0 w-full h-full'>
										<circle
											cx='64'
											cy='64'
											r='60'
											fill='none'
											stroke='currentColor'
											strokeWidth='8'
											className='text-white/10'
										/>
										<circle
											cx='64'
											cy='64'
											r='60'
											fill='none'
											stroke='url(#scoreGradient)'
											strokeWidth='8'
											strokeLinecap='round'
											strokeDasharray={`${
												(reportData.accessibility_score.percentage / 100) * 377
											} 377`}
											transform='rotate(-90 64 64)'
											className='transition-all duration-1000'
										/>
										<defs>
											<linearGradient id='scoreGradient'>
												<stop
													offset='0%'
													stopColor={
														reportData.accessibility_score.percentage >= 80
															? '#10b981'
															: reportData.accessibility_score.percentage >= 50
															? '#f59e0b'
															: '#ef4444'
													}
												/>
												<stop
													offset='100%'
													stopColor={
														reportData.accessibility_score.percentage >= 80
															? '#22c55e'
															: reportData.accessibility_score.percentage >= 50
															? '#fbbf24'
															: '#f87171'
													}
												/>
											</linearGradient>
										</defs>
									</svg>
									<div className='relative'>
										<div
											className={`text-5xl font-bold bg-gradient-to-r ${getScoreGradient(
												reportData.accessibility_score.percentage
											)} bg-clip-text text-transparent`}
										>
											{reportData.accessibility_score.percentage}%
										</div>
									</div>
								</div>
								<div className='space-y-2'>
									<p className='text-2xl font-semibold text-white'>
										Poziom dostępności:{' '}
										<span
											className={`bg-gradient-to-r ${getScoreGradient(
												reportData.accessibility_score.percentage
											)} bg-clip-text text-transparent`}
										>
											{reportData.accessibility_score.level}
										</span>
									</p>
									<p className='text-gray-400'>
										{reportData.metadata.filename}
									</p>
								</div>
							</div>
						</div>

						{/* Key Metrics Grid */}
						<div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
							<div className='bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:border-white/20 transition-all duration-200'>
								<div className='flex items-start justify-between mb-2'>
									<span className='text-gray-400 text-sm font-medium'>
										Zgodność PDF/UA
									</span>
									<span className='p-1.5 bg-white/10 rounded-lg'>
										{reportData.pdf_ua_validation.is_compliant ? '✅' : '❌'}
									</span>
								</div>
								<p
									className={`text-2xl font-bold ${
										reportData.pdf_ua_validation.is_compliant
											? 'text-emerald-400'
											: 'text-red-400'
									}`}
								>
									{reportData.pdf_ua_validation.is_compliant
										? 'Zgodny'
										: 'Niezgodny'}
								</p>
								<p className='text-xs text-gray-500 mt-1'>Standard PDF/UA</p>
							</div>

							<div className='bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:border-white/20 transition-all duration-200'>
								<div className='flex items-start justify-between mb-2'>
									<span className='text-gray-400 text-sm font-medium'>
										Wykryte błędy
									</span>
									<span className='p-1.5 bg-white/10 rounded-lg'>
										<svg
											className='w-4 h-4 text-amber-400'
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
									</span>
								</div>
								<p className='text-2xl font-bold text-white'>
									{reportData.pdf_ua_validation.failed_rules_count}
								</p>
								<p className='text-xs text-gray-500 mt-1'>Naruszeń standardu</p>
							</div>

							<div className='bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:border-white/20 transition-all duration-200'>
								<div className='flex items-start justify-between mb-2'>
									<span className='text-gray-400 text-sm font-medium'>
										Rozmiar pliku
									</span>
									<span className='p-1.5 bg-white/10 rounded-lg'>
										<svg
											className='w-4 h-4 text-purple-400'
											fill='none'
											stroke='currentColor'
											viewBox='0 0 24 24'
										>
											<path
												strokeLinecap='round'
												strokeLinejoin='round'
												strokeWidth={2}
												d='M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z'
											/>
										</svg>
									</span>
								</div>
								<p className='text-2xl font-bold text-white'>
									{(reportData.metadata.file_size / 1024 / 1024).toFixed(2)} MB
								</p>
								<p className='text-xs text-gray-500 mt-1'>Wielkość dokumentu</p>
							</div>
						</div>
					</div>
				)}

				{activeTab === 'details' && (
					<div className='space-y-6 animate-fadeIn'>
						{/* Scoring Details Card */}
						<div className='bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10'>
							<h3 className='text-xl font-semibold text-white mb-6 flex items-center gap-2'>
								<span className='p-2 bg-purple-500/20 rounded-lg'>
									<svg
										className='w-5 h-5 text-purple-400'
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
								</span>
								Szczegóły punktacji
							</h3>
							<div className='space-y-4'>
								{reportData.accessibility_score.details.map((detail, idx) => (
									<div
										key={idx}
										className='group hover:bg-white/5 rounded-lg p-3 transition-all duration-200'
									>
										<div className='flex items-center justify-between mb-2'>
											<span className='text-gray-300 font-medium'>
												{detail.criterion}
											</span>
											<div className='flex items-center gap-3'>
												<span className='text-white font-semibold'>
													{detail.points}/{detail.max} pkt
												</span>
												<span
													className={`text-sm px-2 py-1 rounded-full ${
														detail.points === detail.max
															? 'bg-emerald-500/20 text-emerald-400'
															: detail.points > 0
															? 'bg-amber-500/20 text-amber-400'
															: 'bg-red-500/20 text-red-400'
													}`}
												>
													{Math.round((detail.points / detail.max) * 100)}%
												</span>
											</div>
										</div>
										<div className='w-full h-2 bg-white/10 rounded-full overflow-hidden'>
											<div
												className={`h-full transition-all duration-500 ${
													detail.points === detail.max
														? 'bg-gradient-to-r from-emerald-500 to-green-500'
														: detail.points > 0
														? 'bg-gradient-to-r from-amber-500 to-yellow-500'
														: 'bg-gradient-to-r from-red-500 to-rose-500'
												}`}
												style={{
													width: `${(detail.points / detail.max) * 100}%`,
												}}
											/>
										</div>
									</div>
								))}
							</div>
						</div>

						{/* PDF/UA Validation Errors */}
						{reportData.pdf_ua_validation.failed_rules.length > 0 && (
							<div className='bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10'>
								<h3 className='text-xl font-semibold text-white mb-6 flex items-center gap-2'>
									<span className='p-2 bg-red-500/20 rounded-lg'>
										<svg
											className='w-5 h-5 text-red-400'
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
									</span>
									Błędy zgodności PDF/UA (
									{reportData.pdf_ua_validation.failed_rules.length})
								</h3>
								<div className='space-y-3 max-h-96 overflow-y-auto custom-scrollbar'>
									{reportData.pdf_ua_validation.failed_rules.map(
										(rule, idx) => (
											<div
												key={idx}
												className='bg-white/5 rounded-xl p-4 border border-white/10 hover:border-red-500/30 transition-all duration-200'
											>
												<div className='flex items-start gap-3'>
													<span className='flex-shrink-0 w-8 h-8 bg-red-500/20 rounded-lg flex items-center justify-center text-red-400 font-semibold text-sm'>
														{idx + 1}
													</span>
													<div className='flex-1'>
														<div className='flex items-center gap-2 mb-1'>
															<span className='text-xs font-mono bg-white/10 px-2 py-1 rounded text-gray-400'>
																Klauzula {rule.clause}
															</span>
															{rule.testNumber && (
																<span className='text-xs font-mono bg-white/10 px-2 py-1 rounded text-gray-400'>
																	Test {rule.testNumber}
																</span>
															)}
														</div>
														<p className='text-white text-sm leading-relaxed'>
															{rule.description}
														</p>
													</div>
												</div>
											</div>
										)
									)}
								</div>
							</div>
						)}
					</div>
				)}

				{activeTab === 'recommendations' && (
					<div className='space-y-4 animate-fadeIn'>
						{reportData.recommendations.length === 0 ? (
							<div className='bg-gradient-to-br from-emerald-500/10 to-green-500/10 rounded-2xl p-8 text-center border border-emerald-500/20'>
								<div className='inline-flex items-center justify-center w-16 h-16 bg-emerald-500/20 rounded-full mb-4'>
									<svg
										className='w-8 h-8 text-emerald-400'
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
								<p className='text-emerald-400 text-lg font-semibold'>
									Świetna robota!
								</p>
								<p className='text-gray-300 mt-2'>
									Nie znaleziono krytycznych problemów wymagających
									natychmiastowej uwagi.
								</p>
							</div>
						) : (
							<>
								<div className='mb-4 flex items-center gap-4 flex-wrap'>
									<span className='text-gray-400 text-sm'>
										Legenda priorytetów:
									</span>
									{['high', 'medium', 'low'].map((priority) => (
										<span
											key={priority}
											className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(
												priority
											)}`}
										>
											{getPriorityIcon(priority)} {priority.toUpperCase()}
										</span>
									))}
								</div>
								{reportData.recommendations.map((rec, idx) => (
									<div
										key={idx}
										className='bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:border-white/20 transition-all duration-200 overflow-hidden group'
									>
										<div className='p-6'>
											<div className='flex items-start gap-4'>
												<div
													className={`flex-shrink-0 px-3 py-1.5 rounded-lg text-sm font-semibold border ${getPriorityColor(
														rec.priority
													)}`}
												>
													<span className='flex items-center gap-1.5'>
														{getPriorityIcon(rec.priority)}
														{rec.priority.toUpperCase()}
													</span>
												</div>
												<div className='flex-1 space-y-3'>
													<div>
														<h4 className='text-white font-semibold text-lg mb-1'>
															{rec.issue}
														</h4>
														<p className='text-gray-300 leading-relaxed'>
															{rec.recommendation}
														</p>
													</div>
													<div className='pt-3 border-t border-white/10'>
														<p className='text-xs text-gray-400 flex items-center gap-2'>
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
															Zalecenie #{idx + 1} z{' '}
															{reportData.recommendations.length}
														</p>
													</div>
												</div>
											</div>
										</div>
										<div
											className={`h-1 bg-gradient-to-r ${
												rec.priority === 'high'
													? 'from-red-500 to-rose-500'
													: rec.priority === 'medium'
													? 'from-amber-500 to-yellow-500'
													: 'from-emerald-500 to-green-500'
											} opacity-50 group-hover:opacity-100 transition-opacity duration-200`}
										/>
									</div>
								))}
							</>
						)}
					</div>
				)}
			</div>
		</div>
	);
};
