import { ShieldIcon } from './Icons';

export const Header = () => (
	<header className='text-center mb-12'>
		<div
			className='inline-flex items-center justify-center p-3 bg-indigo-600 rounded-2xl shadow-2xl mb-6'
			aria-hidden='true'
		>
			<ShieldIcon />
		</div>

		<h1 className='text-5xl sm:text-6xl font-bold text-white mb-4 tracking-tight'>
			PDF
			<span className='text-indigo-400'> Audytor</span>
		</h1>

		<p className='text-xl text-slate-300 max-w-2xl mx-auto'>
			Profesjonalna analiza dostępności dokumentów PDF zgodna ze standardami
			WCAG 2.1
		</p>

		<div className='flex flex-wrap justify-center gap-4 mt-8'>
			<div className='flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-full border border-slate-700'>
				<svg
					className='w-4 h-4 text-yellow-300'
					fill='none'
					stroke='currentColor'
					viewBox='0 0 24 24'
					aria-hidden='true'
				>
					<path
						strokeLinecap='round'
						strokeLinejoin='round'
						strokeWidth={2}
						d='M13 10V3L4 14h7v7l9-11h-7z'
					/>
				</svg>
				<span className='text-sm text-white font-medium'>
					Błyskawiczna analiza
				</span>
			</div>
			<div className='flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-full border border-slate-700'>
				<svg
					className='w-4 h-4 text-green-400'
					fill='none'
					stroke='currentColor'
					viewBox='0 0 24 24'
					aria-hidden='true'
				>
					<path
						strokeLinecap='round'
						strokeLinejoin='round'
						strokeWidth={2}
						d='M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z'
					/>
				</svg>
				<span className='text-sm text-white font-medium'>WCAG 2.1 AA</span>
			</div>
			<div className='flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-full border border-slate-700'>
				<svg
					className='w-4 h-4 text-indigo-400'
					fill='none'
					stroke='currentColor'
					viewBox='0 0 24 24'
					aria-hidden='true'
				>
					<path
						strokeLinecap='round'
						strokeLinejoin='round'
						strokeWidth={2}
						d='M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z'
					/>
				</svg>
				<span className='text-sm text-white font-medium'>
					Szczegółowe raporty
				</span>
			</div>
		</div>
	</header>
);
