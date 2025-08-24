import React from 'react';
import type { ReportData } from '@/app/types';

interface KeyMetricsProps {
	validation: ReportData['pdf_ua_validation'];
	metadata: ReportData['metadata'];
}

export const KeyMetrics: React.FC<KeyMetricsProps> = ({
	validation,
	metadata,
}) => (
	<div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
		<div className='bg-gradient-to-br from-white/10 to-white/5 rounded-xl p-6 border border-white/10'>
			<p className='text-gray-400 text-sm font-medium mb-2'>Zgodność PDF/UA</p>
			<p
				className={`text-2xl font-bold ${
					validation.is_compliant ? 'text-emerald-400' : 'text-red-400'
				}`}
			>
				{validation.is_compliant ? 'Zgodny' : 'Niezgodny'}
			</p>
		</div>
		<div className='bg-gradient-to-br from-white/10 to-white/5 rounded-xl p-6 border border-white/10'>
			<p className='text-gray-400 text-sm font-medium mb-2'>Wykryte błędy</p>
			<p className='text-2xl font-bold text-white'>
				{validation.failed_rules_count}
			</p>
		</div>
		<div className='bg-gradient-to-br from-white/10 to-white/5 rounded-xl p-6 border border-white/10'>
			<p className='text-gray-400 text-sm font-medium mb-2'>Rozmiar pliku</p>
			<p className='text-2xl font-bold text-white'>
				{(metadata.file_size / 1024 / 1024).toFixed(2)} MB
			</p>
		</div>
	</div>
);
