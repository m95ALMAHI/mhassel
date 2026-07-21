import Link from 'next/link';

export default function Header() {
  return (
    <header className="bg-emerald-700 text-white shadow-md sticky top-0 z-50">
      <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center dir-rtl">
        <Link href="/" className="text-2xl font-black tracking-wide flex items-center gap-2">
          🌾 <span>محاصيل السودان</span>
        </Link>
        <Link 
          href="/add-price" 
          className="bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-xl text-sm font-bold transition shadow"
        >
          ➕ إضافة نشرة أسعار
        </Link>
      </div>
    </header>
  );
}
