import { AlertIcon } from '@/app/components/audit/Icons';
import React from 'react';
import type { ErrorMessageProps } from '@/app/types';

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ error }) => {
	if (!error) return null;

	return (
		<div
			className='bg-red-950 border border-red-800 rounded-xl p-6'
			role='alert'
			aria-live='assertive'
		>
			<div className='flex items-start gap-4'>
				<div className='flex-shrink-0'>
					<AlertIcon />
				</div>
				<div>
					<h3 className='font-semibold text-red-300 mb-1 text-lg'>
						Wystąpił błąd
					</h3>
					<p className='text-red-200'>{error}</p>
				</div>
			</div>
		</div>
	);
};
