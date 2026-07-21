import './globals.css';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export const metadata = {
  title: 'منصة محاصيل السودان',
  description: 'بورصة أسعار المحاصيل والمدخلات الزراعية في ولايات ومحليات السودان',
};

export default function RootLayout({ children }) {
  return (
    <html lang="ar" dir="rtl">
      <body className="bg-slate-50 min-h-screen flex flex-col font-sans">
        <Header />
        <main className="flex-1 max-w-4xl w-full mx-auto p-4">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
