import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function TermsOfService() {
  return (
    <div className="min-h-screen bg-slate-50 py-12 px-6">
      <div className="max-w-3xl mx-auto bg-white p-10 rounded-3xl shadow-sm border border-slate-200">
        <Link href="/" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium mb-8">
          <ArrowLeft className="w-4 h-4" /> Retour à l'accueil
        </Link>
        
        <h1 className="text-3xl font-extrabold text-slate-900 mb-8">Conditions Générales d'Utilisation</h1>
        
        <div className="space-y-6 text-slate-600 leading-relaxed">
          <p>Dernière mise à jour : {new Date().toLocaleDateString('fr-FR')}</p>

          <h2 className="text-xl font-bold text-slate-800 mt-8">1. Objet du service</h2>
          <p>MailtiVoo est une solution logicielle (SaaS) conçue pour aider les professionnels à suivre leurs opportunités et à générer des brouillons de relance via l'intelligence artificielle en se connectant à leur boîte de réception.</p>

          <h2 className="text-xl font-bold text-slate-800 mt-8">2. Responsabilité liée à l'Intelligence Artificielle</h2>
          <p>MailtiVoo génère des brouillons ("Drafts") à l'aide d'IA. Bien que nous visions la meilleure qualité possible, le contenu généré peut contenir des erreurs, des inexactitudes ou un ton inadapté. <strong>L'utilisateur est seul responsable de la relecture, de la modification et de l'envoi final des e-mails.</strong> MailtiVoo décline toute responsabilité concernant les conséquences commerciales d'un e-mail envoyé via notre plateforme.</p>

          <h2 className="text-xl font-bold text-slate-800 mt-8">3. Abonnements et Paiements</h2>
          <p>MailtiVoo propose un plan gratuit limité et un abonnement premium ("Plan Pro"). Les paiements sont gérés via Stripe. Les abonnements sont sans engagement et peuvent être annulés à tout moment. Aucun remboursement prorata n'est effectué pour un mois entamé.</p>

          <h2 className="text-xl font-bold text-slate-800 mt-8">4. Suspension de compte</h2>
          <p>Nous nous réservons le droit de suspendre tout compte utilisant MailtiVoo pour du spamming, de l'envoi d'e-mails non sollicités en masse, ou toute violation des conditions d'utilisation de Google Workspace.</p>
        </div>
      </div>
    </div>
  );
}