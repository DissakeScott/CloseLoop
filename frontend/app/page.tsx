"use client";
import Image from "next/image"; // On importe le composant Image de Next.js
import { ArrowRight } from "lucide-react";

export default function Home() {
  const handleLogin = () => {
    window.location.href = "http://localhost:8000/auth/login";
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 px-4">
      <div className="max-w-md w-full text-center space-y-8">
        
        {/* --- TON NOUVEAU LOGO --- */}
        <div className="flex justify-center">
          <Image 
            src="/logo.png" 
            alt="CloseLoop Logo" 
            width={300} 
            height={200} 
            className="drop-shadow-md"
          />
        </div>
        
        {/* --- TON NOUVEAU NOM ET SLOGAN --- */}
        <div className="space-y-2">
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">
            CloseLoop
          </h1>
          <p className="text-lg text-slate-600 font-medium">
            Seamless Connection. Enduring Value.
          </p>
        </div>

        <button
          onClick={handleLogin}
          className="group relative w-full flex justify-center py-4 px-4 border border-transparent text-sm font-semibold rounded-xl text-white bg-slate-900 hover:bg-slate-800 focus:outline-none transition-all duration-200 shadow-lg"
        >
          <span className="flex items-center gap-2">
            Se connecter avec Google
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </span>
        </button>

        <p className="text-xs text-slate-400">
          En vous connectant, vous autorisez CloseLoop à analyser vos emails pour détecter les relances.
        </p>
      </div>
    </div>
  );
}