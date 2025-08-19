import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
	title: 'PDF Accessibility Auditor',
	description: 'PDF document accessibility analyser tool',
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang='en'>
			<body className='antialiased'>{children}</body>
		</html>
	);
}
