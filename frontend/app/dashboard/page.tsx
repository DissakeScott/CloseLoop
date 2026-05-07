"use client";
import { useEffect, useState } from "react";
import { fetchOpportunities, generateDraft, sendReply } from "@/lib/api";
import { RefreshCw, MessageSquare, Clock, X, Send, Loader2, CheckCircle, AlertCircle, Mail, LogOut } from "lucide-react";

export default function Dashboard() {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // --- ÉTATS ---
  const [userEmail, setUserEmail] = useState("");
  const [activeTone, setActiveTone] = useState("naturel");
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
      setOpportunities(result.data);
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

  const handleGenerateClick = async (opp: any, tone: string = "naturel") => {
    setSelectedThread(opp);
    setActiveTone(tone); 
    setIsModalOpen(true);
    setIsGenerating(true);
    setDraftText(""); // On s'assure de vider le texte précédent

    try {
      const acc = localStorage.getItem('access_token') || "";
      const ref = localStorage.getItem('refresh_token') || "";
      const result = await generateDraft(opp.thread_id, acc, ref, tone);
      
      // SÉCURITÉ : On s'assure que même si l'API renvoie undefined, on met une chaîne vide
      setDraftText(result.ai_draft || "Désolé, l'IA n'a pas pu générer le texte. Veuillez réessayer.");
    } catch (error: any) {
      if (error.message === "AUTH_EXPIRED") {
        showToast("Session expirée. Redirection en cours...", "error");
        setTimeout(() => handleLogout(), 2000);
      } else {
        showToast("Erreur de l'IA. Impossible de générer la relance.", "error");
      }
      setDraftText("");
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
      if (error.message === "AUTH_EXPIRED") {
        showToast("Session expirée. Redirection en cours...", "error");
        setTimeout(() => handleLogout(), 2000);
      } else {
        showToast("Erreur lors de l'envoi de la relance.", "error");
      }
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      
      {/* --- LE HEADER --- */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img 
              src="/logo.png" 
              alt="CloseLoop" 
              className="w-10 h-10 object-contain drop-shadow-sm" 
            />
            <span className="font-extrabold text-xl text-slate-900 tracking-tight">
              CloseLoop
            </span>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 bg-slate-50 py-1.5 px-2 pr-4 rounded-full border border-slate-200">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold shadow-sm">
                {userEmail ? userEmail.charAt(0).toUpperCase() : 'U'}
              </div>
              <span className="text-sm font-medium text-slate-700 hidden sm:block">
                {userEmail || "Chargement..."}
              </span>
            </div>
            
            <button 
              onClick={handleLogout}
              className="flex items-center justify-center p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-colors duration-200"
              title="Se déconnecter"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* --- LE CONTENU PRINCIPAL --- */}
      <main className="p-8 max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Tes opportunités de relance</h1>
            <p className="text-slate-500 mt-1">Mise à jour basée sur tes derniers emails envoyés.</p>
          </div>
          <button 
            onClick={handleManualRefresh}
            disabled={loading}
            className="flex items-center gap-2 bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-xl hover:bg-slate-50 hover:border-slate-300 disabled:opacity-50 transition-all font-medium shadow-sm"
          >
            <RefreshCw className={`w-4 h-4 text-blue-600 ${loading ? 'animate-spin' : ''}`} />
            {loading ? "Recherche..." : "Actualiser"}
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
                <div className="space-y-2 flex-1 pr-6">
                  <h3 className="font-semibold text-slate-900 line-clamp-1">{opp.subject}</h3>
                  <p className="text-sm text-slate-500">{opp.recipient}</p>
                  <div className="flex items-center gap-4 mt-2">
                    <span className="flex items-center gap-1.5 text-xs font-semibold text-orange-700 bg-orange-100 px-3 py-1.5 rounded-full">
                      <Clock className="w-3.5 h-3.5" />
                      Attente : {opp.days_waiting} jours
                    </span>
                  </div>
                </div>
                <button 
                  onClick={() => handleGenerateClick(opp, "naturel")}
                  className="flex items-center gap-2 text-white bg-blue-600 hover:bg-blue-700 px-5 py-2.5 rounded-xl transition-all font-medium shadow-sm hover:shadow opacity-90 group-hover:opacity-100"
                >
                  <MessageSquare className="w-4 h-4" />
                  Rédiger
                </button>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* --- LA MODALE --- */}
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
              
              {/* --- BARRE DE SÉLECTION DU TON --- */}
              <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
                {[
                  { id: 'naturel', label: '👋 Naturel' },
                  { id: 'formel', label: '👔 Formel' },
                  { id: 'direct', label: '🎯 Direct' },
                  { id: 'court', label: '⚡ Très court' }
                ].map((t) => (
                  <button
                    key={t.id}
                    onClick={() => handleGenerateClick(selectedThread, t.id)}
                    disabled={isGenerating || isSending}
                    className={`px-4 py-2 text-sm font-semibold rounded-xl transition-all whitespace-nowrap ${
                      activeTone === t.id
                        ? 'bg-blue-100 text-blue-700 border-2 border-blue-200'
                        : 'bg-white text-slate-600 border-2 border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                    } disabled:opacity-50`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>

              {/* --- ZONE DE TEXTE --- */}
              {isGenerating ? (
                <div className="flex flex-col items-center justify-center py-16 text-slate-500 gap-4 flex-1">
                  <div className="relative">
                    <Loader2 className="w-10 h-10 animate-spin text-blue-600" />
                    <div className="absolute inset-0 bg-blue-400 blur-xl opacity-20 rounded-full"></div>
                  </div>
                  <p className="font-medium animate-pulse">Nous ajustons le ton de votre relance...</p>
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
              <button 
                onClick={() => setIsModalOpen(false)}
                className="px-6 py-2.5 text-slate-600 font-semibold hover:bg-slate-100 rounded-xl transition-colors"
              >
                Annuler
              </button>
              {/* SÉCURITÉ : !draftText?.trim() au lieu de !draftText.trim() */}
              <button 
                onClick={handleSendClick}
                disabled={isGenerating || isSending || !draftText?.trim()}
                className="flex items-center gap-2 px-6 py-2.5 bg-slate-900 text-white font-semibold rounded-xl hover:bg-slate-800 disabled:opacity-50 transition-all shadow-md"
              >
                {isSending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                {isSending ? "Envoi en cours..." : "Envoyer la relance"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* --- LE TOAST DE NOTIFICATION --- */}
      {toast && (
        <div className="fixed bottom-8 right-8 z-50 flex items-center gap-3 px-6 py-4 bg-slate-900 text-white rounded-2xl shadow-2xl transition-all duration-300 animate-in slide-in-from-bottom-5 border border-slate-700">
          {toast.type === 'success' ? (
            <CheckCircle className="w-5 h-5 text-emerald-400" />
          ) : (
            <AlertCircle className="w-5 h-5 text-red-400" />
          )}
          <span className="font-medium">{toast.message}</span>
        </div>
      )}
    </div>
  );
}