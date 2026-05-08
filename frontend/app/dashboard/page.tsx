"use client";
import { useEffect, useState } from "react";
import { fetchOpportunities, generateDraft, sendReply } from "@/lib/api";
import { RefreshCw, MessageSquare, Clock, X, Send, Loader2, CheckCircle, AlertCircle, LogOut, Info } from "lucide-react";

export default function Dashboard() {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const [userEmail, setUserEmail] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedThread, setSelectedThread] = useState<any>(null);
  const [draftText, setDraftText] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [toast, setToast] = useState<{message: string, type: 'success' | 'error'} | null>(null);

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const urlAccess = urlParams.get('access_token');
    const urlRefresh = urlParams.get('refresh_token');
    const urlEmail = urlParams.get('email');

    if (urlAccess) {
      localStorage.setItem('access_token', urlAccess);
      if (urlEmail) localStorage.setItem('user_email', urlEmail);
      if (urlRefresh && urlRefresh !== "None") {
        localStorage.setItem('refresh_token', urlRefresh);
      }
      window.history.replaceState({}, document.title, "/dashboard");
    }

    const savedAccess = urlAccess || localStorage.getItem('access_token');
    const savedRefresh = urlRefresh || localStorage.getItem('refresh_token');
    const savedEmail = urlEmail || localStorage.getItem('user_email');

    if (savedEmail) setUserEmail(savedEmail);

    if (savedAccess) {
      loadData(savedAccess, savedRefresh || "");
    } else {
      window.location.href = "/";
    }
  }, []);

  const loadData = async (acc: string, ref: string) => {
    setLoading(true);
    try {
      const result = await fetchOpportunities(acc, ref);
      
      // 🔥 LA HEATMAP (Tri intelligent) : On met les "OUBLI" en haut de la pile
      const sortedOpportunities = result.data.sort((a: any, b: any) => {
        const rank: any = { "OUBLI": 1, "OBJECTION": 2, "ATTENTE": 3 };
        const rankA = rank[a.intent_category] || 4;
        const rankB = rank[b.intent_category] || 4;
        return rankA - rankB;
      });
      
      setOpportunities(sortedOpportunities);
    } catch (error: any) {
      if (error.message === "AUTH_EXPIRED") {
        showToast("Session expirée. Redirection en cours...", "error");
        setTimeout(() => handleLogout(), 2000);
      } else {
        showToast("Erreur lors du chargement des e-mails.", "error");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleManualRefresh = () => {
    const acc = localStorage.getItem('access_token');
    const ref = localStorage.getItem('refresh_token');
    if (acc) loadData(acc, ref || "");
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_email');
    window.location.href = "/";
  };

  const handleGenerateClick = async (opp: any) => {
    setSelectedThread(opp);
    setIsModalOpen(true);
    setIsGenerating(true);
    setDraftText(""); 

    try {
      const acc = localStorage.getItem('access_token') || "";
      const ref = localStorage.getItem('refresh_token') || "";
      const result = await generateDraft(opp.thread_id, acc, ref);
      setDraftText(result.ai_draft || "Désolé, l'IA n'a pas pu générer le texte.");
    } catch (error: any) {
      showToast("Erreur de l'IA.", "error");
      setIsModalOpen(false);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSendClick = async () => {
    setIsSending(true);
    try {
      const acc = localStorage.getItem('access_token') || "";
      const ref = localStorage.getItem('refresh_token') || "";
      await sendReply(selectedThread.thread_id, acc, ref, draftText);
      setIsModalOpen(false);
      showToast("🚀 Relance envoyée avec succès !"); 
      loadData(acc, ref); 
    } catch (error: any) {
      showToast("Erreur lors de l'envoi.", "error");
    } finally {
      setIsSending(false);
    }
  };

  // Fonction pour styliser le badge en fonction de l'intention
  const getIntentStyle = (category: string) => {
    switch(category) {
      case "OUBLI": return "bg-emerald-100 text-emerald-800 border-emerald-200";
      case "OBJECTION": return "bg-red-100 text-red-800 border-red-200";
      case "ATTENTE": return "bg-amber-100 text-amber-800 border-amber-200";
      default: return "bg-slate-100 text-slate-800 border-slate-200";
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="CloseLoop" className="w-10 h-10 object-contain drop-shadow-sm" />
            <span className="font-extrabold text-xl text-slate-900 tracking-tight">CloseLoop</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 bg-slate-50 py-1.5 px-2 pr-4 rounded-full border border-slate-200">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold shadow-sm">
                {userEmail ? userEmail.charAt(0).toUpperCase() : 'U'}
              </div>
              <span className="text-sm font-medium text-slate-700 hidden sm:block">{userEmail || "Chargement..."}</span>
            </div>
            <button onClick={handleLogout} className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-colors">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <main className="p-8 max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Tes opportunités de relance</h1>
            <p className="text-slate-500 mt-1">Classées intelligemment par priorité IA.</p>
          </div>
          <button onClick={handleManualRefresh} disabled={loading} className="flex items-center gap-2 bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-xl hover:bg-slate-50 hover:border-slate-300 disabled:opacity-50 transition-all font-medium shadow-sm">
            <RefreshCw className={`w-4 h-4 text-blue-600 ${loading ? 'animate-spin' : ''}`} />
            {loading ? "Analyse IA..." : "Actualiser"}
          </button>
        </div>

        <div className="grid gap-4">
          {opportunities.length === 0 && !loading && (
            <div className="text-center py-24 border-2 border-dashed border-slate-200 rounded-3xl bg-white text-slate-500">
              <p className="text-lg font-medium mb-2">Tout est à jour ! 🎉</p>
              <p className="text-sm">Aucun email en attente de réponse ne nécessite de relance.</p>
            </div>
          )}

          {opportunities.map((opp: any) => (
            <div key={opp.thread_id} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md hover:border-blue-100 transition-all duration-200 group">
              <div className="flex justify-between items-start">
                <div className="space-y-3 flex-1 pr-6">
                  
                  {/* --- BADGES ET MÉTA-DONNÉES --- */}
                  <div className="flex flex-wrap items-center gap-3">
                    <span className={`flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-full border ${getIntentStyle(opp.intent_category)}`}>
                      {opp.intent_category === "OUBLI" && "🔥 Oubli probable"}
                      {opp.intent_category === "ATTENTE" && "⏳ En attente"}
                      {opp.intent_category === "OBJECTION" && "⚠️ Objection"}
                    </span>
                    <span className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 bg-slate-100 px-3 py-1.5 rounded-full">
                      <Clock className="w-3.5 h-3.5" />
                      {opp.days_waiting} jours
                    </span>
                  </div>

                  <div>
                    <h3 className="font-semibold text-slate-900 line-clamp-1 text-lg">{opp.subject}</h3>
                    <p className="text-sm text-slate-500 mt-0.5">{opp.recipient}</p>
                  </div>

                  {/* --- RAISON DE L'IA --- */}
                  <div className="flex items-start gap-2 bg-slate-50 p-3 rounded-lg border border-slate-100 mt-2">
                    <Info className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
                    <p className="text-sm text-slate-600 italic">"{opp.intent_reason}"</p>
                  </div>

                </div>
                
                <div className="flex flex-col items-end justify-center h-full pt-4">
                  <button 
                    onClick={() => handleGenerateClick(opp)}
                    className={`flex items-center gap-2 text-white px-6 py-2.5 rounded-xl transition-all font-medium shadow-sm hover:shadow opacity-90 group-hover:opacity-100 ${
                      opp.intent_category === "ATTENTE" ? "bg-slate-800 hover:bg-slate-900" : "bg-blue-600 hover:bg-blue-700"
                    }`}
                  >
                    <MessageSquare className="w-4 h-4" />
                    Rédiger
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* --- MODALE ET TOAST (inchangés) --- */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-40">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col border border-slate-100">
            <div className="flex justify-between items-center p-6 border-b border-slate-100">
              <div>
                <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                  <span className="bg-blue-100 text-blue-600 p-1 rounded-lg">✨</span>
                  Brouillon IA
                </h2>
                <p className="text-sm text-slate-500 truncate max-w-md mt-1">Destinataire : {selectedThread?.recipient}</p>
              </div>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-red-500 p-2 rounded-xl hover:bg-red-50 transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 bg-slate-50 flex-1 flex flex-col">
              {isGenerating ? (
                <div className="flex flex-col items-center justify-center py-16 text-slate-500 gap-4 flex-1">
                  <div className="relative">
                    <Loader2 className="w-10 h-10 animate-spin text-blue-600" />
                    <div className="absolute inset-0 bg-blue-400 blur-xl opacity-20 rounded-full"></div>
                  </div>
                  <p className="font-medium animate-pulse">L'IA clone votre style et rédige la relance...</p>
                </div>
              ) : (
                <textarea
                  value={draftText}
                  onChange={(e) => setDraftText(e.target.value)}
                  className="w-full flex-1 min-h-[200px] p-5 border border-slate-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-400 outline-none resize-none shadow-inner text-slate-700 leading-relaxed transition-all"
                  placeholder="Le brouillon apparaîtra ici..."
                />
              )}
            </div>
            <div className="p-6 border-t border-slate-100 flex justify-end gap-3 bg-white">
              <button onClick={() => setIsModalOpen(false)} className="px-6 py-2.5 text-slate-600 font-semibold hover:bg-slate-100 rounded-xl transition-colors">
                Annuler
              </button>
              <button onClick={handleSendClick} disabled={isGenerating || isSending || !draftText?.trim()} className="flex items-center gap-2 px-6 py-2.5 bg-slate-900 text-white font-semibold rounded-xl hover:bg-slate-800 disabled:opacity-50 transition-all shadow-md">
                {isSending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                {isSending ? "Envoi en cours..." : "Envoyer la relance"}
              </button>
            </div>
          </div>
        </div>
      )}

      {toast && (
        <div className="fixed bottom-8 right-8 z-50 flex items-center gap-3 px-6 py-4 bg-slate-900 text-white rounded-2xl shadow-2xl transition-all duration-300 animate-in slide-in-from-bottom-5 border border-slate-700">
          {toast.type === 'success' ? <CheckCircle className="w-5 h-5 text-emerald-400" /> : <AlertCircle className="w-5 h-5 text-red-400" />}
          <span className="font-medium">{toast.message}</span>
        </div>
      )}
    </div>
  );
}