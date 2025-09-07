import React from 'react';

export type AnalysisLevel = 'quick' | 'standard' | 'professional';

interface AnalysisLevelSelectorProps {
	selectedLevel: AnalysisLevel;
	onLevelChange: (level: AnalysisLevel) => void;
	disabled?: boolean;
}

const ANALYSIS_LEVELS = [
	{
		id: 'quick' as AnalysisLevel,
		name: 'Szybki skan',
		icon: '⚡',
		time: '< 1s',
		description: 'Podstawowa weryfikacja dostępności',
		features: [
			'Weryfikacja tagowania (TAK/NIE)',
			'Obecność tekstu',
			'Liczba stron i obrazów',
			'Podstawowa ocena',
		],
		color: 'indigo',
		recommended: false,
	},
	{
		id: 'standard' as AnalysisLevel,
		name: 'Analiza standardowa',
		icon: '📊',
		time: '5-10s',
		description: 'Szczegółowa analiza z rekomendacjami',
		features: [
			'Wszystko z szybkiego skanu',
			'Analiza nagłówków i struktury',
			'Weryfikacja alt-tekstów',
			'Sprawdzenie PDF/UA',
			'Rekomendacje napraw',
		],
		color: 'emerald',
		recommended: true,
	},
	{
		id: 'professional' as AnalysisLevel,
		name: 'Audyt profesjonalny',
		icon: '🔬',
		time: '30s+',
		description: 'Kompletny audyt zgodności WCAG/PDF-UA',
		features: [
			'Wszystko z analizy standardowej',
			'Deep scan wszystkich tagów',
			'Analiza każdej strony',
			'Weryfikacja formularzy',
			'Analiza tabel i linków',
			'Pełny raport WCAG 2.1',
		],
		color: 'purple',
		recommended: false,
	},
] as const;

export const AnalysisLevelSelector: React.FC<AnalysisLevelSelectorProps> = ({
	selectedLevel,
	onLevelChange,
	disabled = false,
}) => {
	return (
		<div className='bg-slate-800 rounded-2xl p-8 shadow-xl border border-slate-700'>
			<h2 className='text-2xl font-bold text-white mb-6 flex items-center gap-3'>
				<svg
					className='w-8 h-8 text-indigo-400'
					fill='none'
					stroke='currentColor'
					viewBox='0 0 24 24'
					aria-hidden='true'
				>
					<path
						strokeLinecap='round'
						strokeLinejoin='round'
						strokeWidth={2}
						d='M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4'
					/>
				</svg>
				Wybierz poziom analizy
			</h2>

			<div className='grid md:grid-cols-3 gap-6'>
				{ANALYSIS_LEVELS.map((level) => {
					const isSelected = selectedLevel === level.id;
					const colorClasses = {
						indigo: {
							border: isSelected ? 'border-indigo-500' : 'border-slate-600',
							bg: isSelected ? 'bg-indigo-950/30' : 'bg-slate-900',
							badge: 'bg-indigo-600',
							icon: 'text-indigo-400',
							button: 'bg-indigo-600 hover:bg-indigo-700',
						},
						emerald: {
							border: isSelected ? 'border-emerald-500' : 'border-slate-600',
							bg: isSelected ? 'bg-emerald-950/30' : 'bg-slate-900',
							badge: 'bg-emerald-600',
							icon: 'text-emerald-400',
							button: 'bg-emerald-600 hover:bg-emerald-700',
						},
						purple: {
							border: isSelected ? 'border-purple-500' : 'border-slate-600',
							bg: isSelected ? 'bg-purple-950/30' : 'bg-slate-900',
							badge: 'bg-purple-600',
							icon: 'text-purple-400',
							button: 'bg-purple-600 hover:bg-purple-700',
						},
					}[level.color];

					return (
						<button
							key={level.id}
							onClick={() => onLevelChange(level.id)}
							disabled={disabled}
							className={`
								relative p-6 rounded-xl border-2 transition-all duration-300
								${colorClasses.border} ${colorClasses.bg}
								${
									!disabled
										? 'hover:scale-105 cursor-pointer'
										: 'opacity-50 cursor-not-allowed'
								}
								${isSelected ? 'ring-2 ring-offset-2 ring-offset-slate-800' : ''}
							`}
							aria-pressed={isSelected}
							aria-label={`${level.name} - ${level.description}`}
						>
							{level.recommended && (
								<div className='absolute -top-3 -right-3'>
									<span className='bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full'>
										ZALECANE
									</span>
								</div>
							)}

							<div className='text-center mb-4'>
								<div className='text-4xl mb-2' aria-hidden='true'>
									{level.icon}
								</div>
								<h3 className='text-xl font-bold text-white mb-1'>
									{level.name}
								</h3>
								<div
									className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg ${colorClasses.badge} text-white text-sm`}
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
											d='M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
										/>
									</svg>
									{level.time}
								</div>
							</div>

							<p className='text-slate-300 text-sm mb-4'>{level.description}</p>

							<ul className='space-y-2 text-left'>
								{level.features.map((feature, idx) => (
									<li key={idx} className='flex items-start gap-2 text-sm'>
										<svg
											className={`w-4 h-4 mt-0.5 flex-shrink-0 ${colorClasses.icon}`}
											fill='none'
											stroke='currentColor'
											viewBox='0 0 24 24'
										>
											<path
												strokeLinecap='round'
												strokeLinejoin='round'
												strokeWidth={2}
												d='M5 13l4 4L19 7'
											/>
										</svg>
										<span className='text-slate-300'>{feature}</span>
									</li>
								))}
							</ul>

							{isSelected && (
								<div className='mt-4 pt-4 border-t border-slate-700'>
									<span className='text-white font-semibold flex items-center justify-center gap-2'>
										<svg
											className='w-5 h-5 text-green-400'
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
										Wybrany
									</span>
								</div>
							)}
						</button>
					);
				})}
			</div>

			{/* Informacja o wybranym poziomie */}
			<div className='mt-6 p-4 bg-slate-900 rounded-xl border border-slate-700'>
				<div className='flex items-center gap-3'>
					<svg
						className='w-5 h-5 text-indigo-400 flex-shrink-0'
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
					<p className='text-slate-300 text-sm'>
						<span className='font-semibold text-white'>Wybrany poziom: </span>
						{ANALYSIS_LEVELS.find((l) => l.id === selectedLevel)?.name} - Czas
						analizy: {ANALYSIS_LEVELS.find((l) => l.id === selectedLevel)?.time}
					</p>
				</div>
			</div>
		</div>
	);
};
