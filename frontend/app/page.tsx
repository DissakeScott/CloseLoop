"use client";

import { ArrowRight, Mail, Bot, TrendingUp, CheckCircle, Shield } from "lucide-react";
import { motion, type Variants } from "framer-motion";
import Link from "next/link";

export default function LandingPage() {
  const handleLogin = () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    window.location.href = `${apiUrl}/auth/login`;
  };

  // --- VARIABLES D'ANIMATION ---
  const staggerContainer: Variants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.15 }
    }
  };

  const fadeUp: Variants = {
    hidden: { opacity: 0, y: 30 },
    show: {
      opacity: 1,
      y: 0,
      transition: { type: "spring" as const, stiffness: 70, damping: 15 }
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans selection:bg-blue-200 relative overflow-hidden">
      
      {/* EFFET DE LUMIÈRE EN ARRIÈRE-PLAN (GLOW ORB) */}
      <div className="absolute top-[-10%] left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-gradient-to-br from-blue-400/20 to-emerald-300/20 blur-[100px] rounded-full pointer-events-none -z-10" />

      {/* --- NAVIGATION --- */}
      <motion.nav 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 100, damping: 20 }}
        className="fixed w-full bg-white/70 backdrop-blur-md border-b border-slate-200/50 z-50"
      >
      <div className="max-w-6xl mx-auto px-6 h-28 flex items-center justify-between"> {/* h-16 -> h-28 pour accueillir le grand logo */}
  <div className="relative group transition-transform hover:scale-105 active:scale-95 cursor-pointer flex items-center gap-3">
    <img 
      src="/Logo.png" 
      alt="MailtiVoo Logo" 
      className="w-50 h-54 -mt-10 -mb-10 object-contain drop-shadow-xl transition-all"
    />
    
    {/* Effet de halo accentué pour accompagner la nouvelle taille */}
    <div className="absolute inset-0 bg-blue-500 blur-3xl opacity-20 rounded-full -z-10 scale-150"></div>
    
    {/* Optionnel : un petit reflet brillant au survol pour le côté Premium */}
    <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-xl"></div>
  </div>
          <button 
            onClick={handleLogin}
            className="text-sm font-semibold text-slate-700 hover:text-blue-600 transition-colors"
          >
            Se connecter
          </button>
        </div>
      </motion.nav>

      {/* --- HERO SECTION --- */}
      <motion.section 
        variants={staggerContainer}
        initial="hidden"
        animate="show"
        className="pt-40 pb-20 px-6 text-center max-w-5xl mx-auto relative z-10"
      >
        <motion.div variants={fadeUp} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-50/80 backdrop-blur-sm border border-blue-200/50 text-blue-600 text-xs font-bold uppercase tracking-wider mb-8 shadow-sm">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
          </span>
          L'IA qui booste votre chiffre d'affaires
        </motion.div>
        
        <motion.h1 variants={fadeUp} className="text-5xl md:text-7xl font-extrabold text-slate-900 tracking-tight leading-tight mb-6">
          Arrêtez de perdre de l'argent <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-emerald-500">
            par manque de relance.
          </span>
        </motion.h1>
        
        <motion.p variants={fadeUp} className="text-xl text-slate-500 mb-10 max-w-2xl mx-auto leading-relaxed">
          MailtiVoo se connecte à votre Gmail, détecte les prospects qui vous ignorent, et rédige des relances ultra-personnalisées avec votre propre style. 
        </motion.p>
        
        <motion.div variants={fadeUp} className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button 
            onClick={handleLogin}
            className="group flex items-center justify-center gap-2 w-full sm:w-auto px-8 py-4 bg-slate-900 text-white rounded-2xl font-bold text-lg hover:bg-slate-800 hover:shadow-2xl hover:shadow-slate-900/20 hover:-translate-y-1 transition-all duration-300"
          >
            Commencer gratuitement 
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
          <p className="text-sm text-slate-400 sm:hidden">Aucune carte bancaire requise.</p>
        </motion.div>
        
        <motion.div variants={fadeUp} className="mt-8 flex items-center justify-center gap-6 text-sm text-slate-500 hidden sm:flex">
          <span className="flex items-center gap-1.5"><CheckCircle className="w-4 h-4 text-emerald-500" /> 5 relances gratuites</span>
          <span className="flex items-center gap-1.5"><CheckCircle className="w-4 h-4 text-emerald-500" /> Sans engagement</span>
          <span className="flex items-center gap-1.5"><Shield className="w-4 h-4 text-emerald-500" /> Sécurisé par Google</span>
        </motion.div>
      </motion.section>

      {/* --- DASHBOARD PREVIEW ANIMÉ --- */}
      <motion.section 
        initial={{ opacity: 0, y: 50 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.8, type: "spring", bounce: 0.4 }}
        className="px-6 pb-24 max-w-6xl mx-auto"
      >
        <div className="rounded-3xl border border-white bg-white/40 p-2 shadow-2xl shadow-blue-900/5 backdrop-blur-md transform-gpu hover:scale-[1.01] transition-transform duration-500">
          <div className="rounded-2xl border border-slate-100 bg-slate-50/80 overflow-hidden relative">
             <div className="absolute top-0 left-0 w-full h-12 bg-white/50 border-b border-slate-200/50 flex items-center px-4 gap-2 backdrop-blur-sm z-10">
                <div className="w-3 h-3 rounded-full bg-red-400"></div>
                <div className="w-3 h-3 rounded-full bg-amber-400"></div>
                <div className="w-3 h-3 rounded-full bg-emerald-400"></div>
             </div>
             
             {/* Animation du faux dashboard */}
             <div className="pt-24 pb-16 px-8 text-center text-slate-400 flex flex-col items-center justify-center min-h-[400px] relative overflow-hidden">
                <motion.div
                  animate={{ y: [0, -10, 0] }}
                  transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
                >
                  <TrendingUp className="w-20 h-20 text-emerald-400 mb-6 opacity-80 drop-shadow-lg" />
                </motion.div>
                <p className="font-bold text-2xl text-slate-700 bg-white/60 px-6 py-2 rounded-full border border-slate-200/50 shadow-sm backdrop-blur-sm">
                  Revenus récupérés : 1 500 €
                </p>
                <motion.p 
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1 }}
                  className="text-sm mt-4 font-medium text-blue-600 bg-blue-50 px-4 py-1.5 rounded-full"
                >
                  ✨ 3 opportunités trouvées par l'IA
                </motion.p>
             </div>
          </div>
        </div>
      </motion.section>

      {/* --- FEATURES (SCROLL REVEAL) --- */}
      <section className="py-32 bg-white border-y border-slate-200/50 relative">
        <div className="max-w-6xl mx-auto px-6">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-20"
          >
            <h2 className="text-3xl md:text-5xl font-bold text-slate-900 mb-6 tracking-tight">L'automatisation au service de la vente</h2>
            <p className="text-slate-500 max-w-2xl mx-auto text-lg">Ne laissez plus la charge mentale dicter votre chiffre d'affaires. MailtiVoo s'occupe de la partie la plus ingrate de la prospection.</p>
          </motion.div>

          <motion.div 
            variants={staggerContainer}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, margin: "-50px" }}
            className="grid md:grid-cols-3 gap-8"
          >
            {/* Carte 1 */}
            <motion.div variants={fadeUp} className="group bg-slate-50 p-8 rounded-3xl border border-slate-100 hover:border-blue-200 hover:bg-blue-50/50 hover:shadow-xl hover:shadow-blue-900/5 transition-all duration-300">
              <div className="w-14 h-14 bg-white text-blue-600 rounded-2xl flex items-center justify-center mb-6 shadow-sm group-hover:scale-110 transition-transform">
                <Mail className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">Scan Intelligent</h3>
              <p className="text-slate-500 leading-relaxed">Notre algorithme analyse vos fils de discussion en arrière-plan et détecte instantanément les e-mails restés sans réponse.</p>
            </motion.div>
            
            {/* Carte 2 */}
            <motion.div variants={fadeUp} className="group bg-slate-50 p-8 rounded-3xl border border-slate-100 hover:border-emerald-200 hover:bg-emerald-50/50 hover:shadow-xl hover:shadow-emerald-900/5 transition-all duration-300">
              <div className="w-14 h-14 bg-white text-emerald-600 rounded-2xl flex items-center justify-center mb-6 shadow-sm group-hover:scale-110 transition-transform">
                <Bot className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">Brouillons IA "Clonés"</h3>
              <p className="text-slate-500 leading-relaxed">L'IA Gemini analyse votre style d'écriture passé pour rédiger des relances naturelles qui vous ressemblent à 100%.</p>
            </motion.div>

            {/* Carte 3 */}
            <motion.div variants={fadeUp} className="group bg-slate-50 p-8 rounded-3xl border border-slate-100 hover:border-purple-200 hover:bg-purple-50/50 hover:shadow-xl hover:shadow-purple-900/5 transition-all duration-300">
              <div className="w-14 h-14 bg-white text-purple-600 rounded-2xl flex items-center justify-center mb-6 shadow-sm group-hover:scale-110 transition-transform">
                <TrendingUp className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">ROI Mesurable</h3>
              <p className="text-slate-500 leading-relaxed">Suivez exactement combien de chiffre d'affaires vos relances vous ont permis de sauver ce mois-ci sur un tableau de bord clair.</p>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* --- PRICING --- */}
      <section className="py-32 px-6 max-w-5xl mx-auto">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <h2 className="text-3xl md:text-5xl font-bold text-slate-900 mb-6 tracking-tight">Rentabilisé à la première relance</h2>
          <p className="text-slate-500 text-lg">Commencez gratuitement, passez à la vitesse supérieure quand vous êtes convaincu.</p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8 items-center">
          {/* Plan Gratuit */}
          <motion.div 
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="bg-white p-10 rounded-3xl border border-slate-200 shadow-lg hover:shadow-xl transition-shadow flex flex-col h-full"
          >
            <h3 className="text-2xl font-bold text-slate-900 mb-2">Plan Découverte</h3>
            <p className="text-slate-500 mb-8">Pour tester la puissance de l'IA.</p>
            <div className="mb-10">
              <span className="text-6xl font-extrabold text-slate-900">0 €</span>
            </div>
            <ul className="space-y-5 mb-10 flex-1">
              <li className="flex items-center gap-4 text-slate-600"><CheckCircle className="w-6 h-6 text-slate-300" /> 5 relances générées par IA</li>
              <li className="flex items-center gap-4 text-slate-600"><CheckCircle className="w-6 h-6 text-slate-300" /> Clonage de style d'écriture</li>
              <li className="flex items-center gap-4 text-slate-600"><CheckCircle className="w-6 h-6 text-slate-300" /> Scan Gmail quotidien</li>
            </ul>
            <button 
              onClick={handleLogin}
              className="w-full py-4 rounded-xl border-2 border-slate-200 text-slate-700 font-bold hover:border-slate-800 hover:text-slate-900 transition-colors"
            >
              Créer mon compte
            </button>
          </motion.div>

          {/* Plan Pro */}
          <motion.div 
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-slate-900 p-10 rounded-3xl border border-slate-800 shadow-2xl shadow-blue-900/20 flex flex-col relative overflow-hidden transform md:scale-105 z-10"
          >
            {/* Effet brillant en arrière plan du plan Pro */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 blur-3xl rounded-full pointer-events-none" />
            
            <motion.div 
              animate={{ opacity: [0.8, 1, 0.8] }}
              transition={{ repeat: Infinity, duration: 2 }}
              className="absolute top-0 right-0 bg-gradient-to-r from-blue-500 to-emerald-400 text-white text-xs font-bold px-5 py-2 rounded-bl-2xl uppercase tracking-wider shadow-md"
            >
              Le plus rentable
            </motion.div>
            
            <h3 className="text-2xl font-bold text-white mb-2 relative z-10">Plan Pro</h3>
            <p className="text-slate-400 mb-8 relative z-10">Pour les indépendants qui scalent.</p>
            <div className="mb-10 relative z-10">
              <span className="text-6xl font-extrabold text-white">29 €</span>
              <span className="text-slate-400 text-lg">/mois</span>
            </div>
            <ul className="space-y-5 mb-10 flex-1 relative z-10">
              <li className="flex items-center gap-4 text-slate-300"><CheckCircle className="w-6 h-6 text-emerald-400" /> <strong className="text-white text-lg">Relances illimitées</strong></li>
              <li className="flex items-center gap-4 text-slate-300"><CheckCircle className="w-6 h-6 text-emerald-400" /> Suivi du ROI en direct</li>
              <li className="flex items-center gap-4 text-slate-300"><CheckCircle className="w-6 h-6 text-emerald-400" /> Envoi direct en 1 clic</li>
              <li className="flex items-center gap-4 text-slate-300"><CheckCircle className="w-6 h-6 text-emerald-400" /> Support prioritaire</li>
            </ul>
            <button 
              onClick={handleLogin}
              className="relative z-10 w-full py-4 rounded-xl bg-blue-600 text-white font-bold hover:bg-blue-500 transition-all shadow-lg shadow-blue-900/40 hover:shadow-blue-900/60 hover:-translate-y-0.5"
            >
              Débloquer l'illimité
            </button>
          </motion.div>
        </div>
      </section>

      {/* --- FOOTER --- */}
      <footer className="bg-white border-t border-slate-200 py-12 text-center text-slate-500">
        <div className="flex items-center justify-center gap-2 -mb-4 -mt-10 hover:opacity-80 transition-opacity cursor-pointer">
          <img src="/Logo.png" alt="MailtiVoo Logo" className="w-44 h-20 opacity-80 grayscale" />
        </div>
        
        <p className="text-sm mb-4">© {new Date().getFullYear()} MailtiVoo. Conçu pour maximiser votre potentiel.</p>
        <div className="flex justify-center gap-6 -mb-8">
          <Link href="/privacy" className="hover:text-blue-600 transition-colors">Politique de Confidentialité</Link>
          <Link href="/terms" className="hover:text-blue-600 transition-colors">Conditions d'utilisation</Link>
        </div>
      </footer>
    </div>
  );
}