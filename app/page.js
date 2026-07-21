import { supabase } from '@/lib/supabase';
import PriceCard from '@/components/PriceCard';

export const revalidate = 0; // تحديث لحظي للبيانات

export default async function HomePage() {
  const { data: posts, error } = await supabase
    .from('market_posts')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) {
    console.error(error);
  }

  return (
    <div className="space-y-6">
      <div className="text-center py-4 bg-emerald-800 text-white rounded-2xl shadow-sm mb-6">
        <h1 className="text-2xl font-black mb-1">أسواق المحاصيل والمدخلات الزراعية</h1>
        <p className="text-xs text-emerald-200">تحديث يومي لأسعار المحاصيل بكافة ولايات ومحليات السودان</p>
      </div>

      {posts && posts.length > 0 ? (
        posts.map((post) => <PriceCard key={post.id} post={post} />)
      ) : (
        <div className="text-center py-12 text-slate-500">لا توجد أسعار مسجلة حالياً.</div>
      )}
    </div>
  );
}
