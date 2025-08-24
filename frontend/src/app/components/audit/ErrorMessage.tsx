import { AlertIcon } from '@/app/components/audit/Icons';
import React from 'react';
import type { ErrorMessageProps } from '@/app/types';

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ error }) => {
	if (!error) return null;

	return (
		<div
			className='bg-red-500/10 backdrop-blur-sm border border-red-500/20 rounded-2xl p-6'
			role='alert'
		>
			<div className='flex items-start gap-4'>
				<div className='flex-shrink-0'>
					<AlertIcon />
				</div>
				<div>
					<h3 className='font-semibold text-red-400 mb-1'>Wystąpił błąd</h3>
					<p className='text-red-300'>{error}</p>
				</div>
			</div>
		</div>
	);
};
