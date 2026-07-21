export default function PriceCard({ post }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-emerald-100 p-5 mb-6 text-right dir-rtl">
      {/* Header */}
      <div className="bg-emerald-50 border-r-4 border-emerald-600 p-3 rounded-lg mb-4">
        <h2 className="font-bold text-lg text-emerald-900">
          📍 أسعار المحاصيل – {post.market_name} (محلية {post.locality} - {post.state})
        </h2>
        <p className="text-xs text-slate-500 mt-1">🗓️ {post.post_date}</p>
      </div>

      {/* Items Table */}
      <div className="divide-y divide-slate-100 mb-4">
        {post.items && post.items.map((item, idx) => (
          <div key={idx} className="py-2 flex justify-between items-center text-sm">
            <span className="font-medium text-slate-800">🔼 {item.name}</span>
            <span className="font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
              {item.price}
            </span>
          </div>
        ))}
      </div>

      {/* Merchant Notes */}
      {post.notes && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs text-amber-900 mb-3">
          📢 {post.notes}
        </div>
      )}

      {/* Merchant Contact */}
      <div className="flex justify-between items-center pt-2 border-t text-sm font-semibold">
        <span className="text-slate-700">✅ {post.merchant_name}</span>
        <a 
          href={`tel:${post.phone}`} 
          className="bg-emerald-100 text-emerald-800 px-3 py-1 rounded-lg text-xs font-mono font-bold dir-ltr"
        >
          📞 {post.phone}
        </a>
      </div>
    </div>
  );
}
