"use client";
import { useState, useEffect } from "react";
import { User, CreditCard, Calendar, ArrowLeft, ExternalLink, Loader2, CheckCircle, AlertCircle, Info } from "lucide-react";
import Link from "next/link";

export default function SettingsPage() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<{message: string, type: 'success' | 'error' | 'info'} | null>(null);

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  useEffect(() => {
    const loadUserProfile = async () => {
      const email = localStorage.getItem('user_email');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      if (!email) {
        window.location.href = "/";
        return;
      }

      try {
        const res = await fetch(`${apiUrl}/threads/stats/${encodeURIComponent(email)}`);
        
        if (res.ok) {
          const data = await res.json();
          setUser({
            full_name: email.split('@')[0], 
            email: email,
            plan: data.plan,
            subscription_end: data.subscription_end || "2026-12-31" 
          });
        }
      } catch (error) {
        showToast("Impossible de charger le profil", "error");
      } finally {
        setLoading(false);
      }
    };

    loadUserProfile();
  }, []);

  // 💡 NOUVELLE FONCTION POUR LE PAIEMENT !
  const handleUpgrade = async () => {
    const email = localStorage.getItem('user_email');
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    if (!email) return;

    showToast("Création de votre lien de paiement...", "info");

    try {
      const res = await fetch(`${apiUrl}/payments/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email }), 
      });

      if (res.ok) {
        const data = await res.json();
        if (data.checkout_url) {
          window.location.href = data.checkout_url; // Redirection vers Stripe
        } else {
          showToast("Lien de paiement introuvable.", "error");
        }
      } else {
        showToast("Erreur lors de la préparation du paiement.", "error");
      }
    } catch (error) {
      showToast("Erreur de connexion au serveur.", "error");
    }
  };

  const handleManageBilling = async () => {
    const email = localStorage.getItem('user_email');
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    if (!email) return;

    showToast("Connexion sécurisée à Stripe...", "info");

    try {
      const res = await fetch(`${apiUrl}/payments/customer-portal?email=${encodeURIComponent(email)}`, {
        method: 'POST',
      });

      if (res.ok) {
        const data = await res.json();
        window.location.href = data.url;
      } else {
        const errorData = await res.json();
        if (errorData.detail?.includes("Client Stripe non trouvé")) {
            showToast("Aucun abonnement actif trouvé.", "error");
        } else {
            showToast("Erreur lors de l'accès au portail.", "error");
        }
      }
    } catch (error) {
      showToast("Erreur de connexion au serveur.", "error");
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen bg-slate-50">
      <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-3xl mx-auto">
        <Link href="/dashboard" className="flex items-center gap-2 text-slate-500 hover:text-slate-900 mb-8 transition-colors w-fit">
          <ArrowLeft className="w-4 h-4" /> Retour au Dashboard
        </Link>

        <h1 className="text-2xl font-bold text-slate-900 mb-8 tracking-tight">Paramètres du compte</h1>

        <div className="grid gap-6">
          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm transition-all hover:shadow-md">
            <div className="flex items-center gap-4 mb-8">
              <div className="w-12 h-12 bg-blue-100 rounded-2xl flex items-center justify-center text-blue-600 shadow-inner">
                <User className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-900">Profil</h2>
                <p className="text-sm text-slate-500">Vos identifiants de connexion MailtiVoo.</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 block">Nom d'utilisateur</label>
                <p className="text-slate-900 font-semibold text-lg capitalize">{user?.full_name}</p>
              </div>
              <div>
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 block">Adresse e-mail</label>
                <p className="text-slate-900 font-semibold text-lg">{user?.email}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm relative overflow-hidden transition-all hover:shadow-md">
            <div className="flex items-center gap-4 mb-8">
              <div className="w-12 h-12 bg-emerald-100 rounded-2xl flex items-center justify-center text-emerald-600 shadow-inner">
                <CreditCard className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-900">Abonnement</h2>
                <p className="text-sm text-slate-500">Gérez vos préférences de facturation.</p>
              </div>
            </div>

            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100 mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-slate-600 font-bold uppercase text-xs tracking-widest">Offre actuelle</span>
                  <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter ${user?.plan === 'pro' ? 'bg-blue-600 text-white shadow-lg shadow-blue-200' : 'bg-slate-200 text-slate-600'}`}>
                    Plan {user?.plan}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-500 font-medium">
                  <Calendar className="w-4 h-4 text-slate-400" /> 
                  Expire le {new Date(user?.subscription_end).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}
                </div>
              </div>
              
              {/* 💡 CORRECTION DU BOUTON ICI ! */}
              {user?.plan === "free" && (
                <button 
                  onClick={handleUpgrade}
                  className="text-sm font-bold text-blue-600 hover:text-blue-700 underline underline-offset-4 bg-transparent border-none cursor-pointer"
                >
                  Passer au plan Pro →
                </button>
              )}
            </div>

            <button 
              onClick={handleManageBilling}
              className="group flex items-center justify-center gap-3 w-full py-4 bg-slate-900 text-white rounded-2xl font-bold hover:bg-slate-800 transition-all shadow-lg shadow-slate-200 active:scale-95"
            >
              Gérer la facturation sur Stripe 
              <ExternalLink className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            </button>
          </div>
        </div>
      </div>

      {toast && (
        <div className="fixed bottom-8 right-8 z-50 flex items-center gap-3 px-6 py-4 bg-slate-900 text-white rounded-2xl shadow-2xl transition-all duration-300 animate-in slide-in-from-bottom-5 border border-slate-700">
          {toast.type === 'success' ? <CheckCircle className="w-5 h-5 text-emerald-400" /> : toast.type === 'info' ? <Info className="w-5 h-5 text-blue-400" /> : <AlertCircle className="w-5 h-5 text-red-400" />}
          <span className="font-medium">{toast.message}</span>
        </div>
      )}
    </div>
  );
}