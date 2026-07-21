export default function Footer() {
  return (
    <footer className="w-full bg-slate-900 text-white py-6 border-t-4 border-emerald-600 mt-12">
      <div className="max-w-4xl mx-auto px-4 text-center space-y-2">
        <p className="font-semibold text-lg text-emerald-400">🌾 منصة محاصيل السودان</p>
        <p className="text-sm text-slate-300">
          جميع الحقوق محفوظة © {new Date().getFullYear()}
        </p>
        <div className="pt-2 text-xs text-slate-400 border-t border-slate-800">
          <p>
            طور بواسطة <span className="text-emerald-400 font-bold">مصطفى الماحي</span> | 
            تحت إشراف مهندس زراعي <span className="text-emerald-400 font-bold">محمد حيدر</span>
          </p>
        </div>
      </div>
    </footer>
  );
}
