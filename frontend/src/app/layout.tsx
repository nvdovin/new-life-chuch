import './globals.css';
import { ReactNode } from 'react';

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang='ru'>
      <body className='mx-auto max-w-6xl p-6'>{children}</body>
    </html>
  );
}
