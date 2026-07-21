'use client';
import { useState } from 'react';
import { supabase } from '@/lib/supabase';
import { useRouter } from 'next/navigation';

export default function AddPricePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    state: 'ولاية الجزيرة',
    locality: 'المناقل',
    market_name: 'سوق الهدى',
    merchant_name: '',
    phone: '',
    notes: '',
  });

  const [items, setItems] = useState([
    { name: 'القمح', price: '' },
    { name: 'الفول المصري', price: '' }
  ]);

  const handleItemChange = (index, field, value) => {
    const updated = [...items];
    updated[index][field] = value;
    setItems(updated);
  };

  const addItemRow = () => {
    setItems([...items, { name: '', price: '' }]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const { error } = await supabase.from('market_posts').insert([
      {
        ...formData,
        items: items.filter(i => i.name && i.price),
      },
    ]);

    setLoading(false);

    if (error) {
      alert('حدث خطأ أثناء حفظ نشرة الأسعار: ' + error.message);
    } else {
      alert('تم نشر الأسعار بنجاح!');
      router.push('/');
      router.refresh();
    }
  };

  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 max-w-2xl mx-auto dir-rtl">
      <h1 className="text-xl font-bold text-slate-800 mb-6 text-center">إضافة نشرة أسعار جديدة</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-bold mb-1">الولاية</label>
            <input 
              type="text" 
              required
              className="w-full border p-2 rounded-lg text-sm"
              value={formData.state} 
              onChange={e => setFormData({...formData, state: e.target.value})} 
            />
          </div>
          <div>
            <label className="block text-xs font-bold mb-1">المحلية</label>
            <input 
              type="text" 
              required
              className="w-full border p-2 rounded-lg text-sm"
              value={formData.locality} 
              onChange={e => setFormData({...formData, locality: e.target.value})} 
            />
          </div>
          <div>
            <label className="block text-xs font-bold mb-1">اسم السوق</label>
            <input 
              type="text" 
              required
              className="w-full border p-2 rounded-lg text-sm"
              value={formData.market_name} 
              onChange={e => setFormData({...formData, market_name: e.target.value})} 
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold mb-1">اسم التاجر/المحل</label>
            <input 
              type="text" 
              required
              placeholder="مثال: ود البله للمحاصيل"
              className="w-full border p-2 rounded-lg text-sm"
              value={formData.merchant_name} 
              onChange={e => setFormData({...formData, merchant_name: e.target.value})} 
            />
          </div>
          <div>
            <label className="block text-xs font-bold mb-1">رقم الهاتف</label>
            <input 
              type="text" 
              required
              placeholder="0120827832"
              className="w-full border p-2 rounded-lg text-sm dir-ltr text-right"
              value={formData.phone} 
              onChange={e => setFormData({...formData, phone: e.target.value})} 
            />
          </div>
        </div>

        {/* قائمة الأجناس والأسعار */}
        <div className="border-t pt-4 mt-4">
          <label className="block text-xs font-bold mb-2">الأصناف والأسعار</label>
          {items.map((item, index) => (
            <div key={index} className="flex gap-2 mb-2">
              <input 
                type="text" 
                placeholder="اسم المحصول/المنتج" 
                className="flex-1 border p-2 rounded-lg text-sm"
                value={item.name}
                onChange={e => handleItemChange(index, 'name', e.target.value)}
              />
              <input 
                type="text" 
                placeholder="السعر (مثال: 190 أو 550-650)" 
                className="flex-1 border p-2 rounded-lg text-sm"
                value={item.price}
                onChange={e => handleItemChange(index, 'price', e.target.value)}
              />
            </div>
          ))}
          <button 
            type="button" 
            onClick={addItemRow}
            className="text-xs text-emerald-700 font-bold mt-1 hover:underline"
          >
            ➕ إضافة صنف آخر
          </button>
        </div>

        <div>
          <label className="block text-xs font-bold mb-1">ملاحظات أو طلبات الشراء</label>
          <textarea 
            rows="3"
            placeholder="مثال: نشتري كميات بسعر السوق..."
            className="w-full border p-2 rounded-lg text-sm"
            value={formData.notes}
            onChange={e => setFormData({...formData, notes: e.target.value})}
          />
        </div>

        <button 
          type="submit" 
          disabled={loading}
          className="w-full bg-emerald-700 text-white font-bold py-3 rounded-xl hover:bg-emerald-800 transition"
        >
          {loading ? 'جاري النشر...' : 'نشر الأسعار الان'}
        </button>
      </form>
    </div>
  );
}
