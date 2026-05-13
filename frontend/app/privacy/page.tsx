import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-slate-50 py-12 px-6">
      <div className="max-w-3xl mx-auto bg-white p-10 rounded-3xl shadow-sm border border-slate-200">
        <Link href="/" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium mb-8">
          <ArrowLeft className="w-4 h-4" /> Retour à l'accueil
        </Link>
        
        <h1 className="text-3xl font-extrabold text-slate-900 mb-8">Politique de Confidentialité</h1>
        
        <div className="space-y-6 text-slate-600 leading-relaxed">
          <p>Dernière mise à jour : {new Date().toLocaleDateString('fr-FR')}</p>

          <h2 className="text-xl font-bold text-slate-800 mt-8">1. Introduction</h2>
          <p>Bienvenue sur MailtiVoo. La protection de vos données personnelles est notre priorité. Cette politique explique comment nous collectons, utilisons et protégeons vos informations lorsque vous utilisez notre service d'optimisation de relances e-mail.</p>

          <h2 className="text-xl font-bold text-slate-800 mt-8">2. Utilisation de l'API Gmail (Google Workspace APIs)</h2>
          <p>L'utilisation par MailtiVoo des informations reçues des API Google respecte la <a href="https://developers.google.com/terms/api-services-user-data-policy" className="text-blue-600 underline">Google API Services User Data Policy</a>, y compris les exigences d'utilisation limitée.</p>
          <ul className="list-disc pl-5 space-y-2">
            <li><strong>Ce que nous lisons :</strong> Nous accédons à vos fils d'e-mails uniquement pour identifier les messages sans réponse (opportunités de relance).</li>
            <li><strong>Ce que nous ne faisons PAS :</strong> Nous ne vendons pas vos données. Nous n'utilisons pas vos e-mails pour diffuser des publicités. L'accès humain à vos e-mails est strictement interdit, sauf en cas d'obligation légale ou avec votre consentement explicite pour résoudre un bug.</li>
          </ul>

          <h2 className="text-xl font-bold text-slate-800 mt-8">3. Intelligence Artificielle et Données</h2>
          <p>MailtiVoo utilise des modèles d'intelligence artificielle pour générer des brouillons de relance. Les métadonnées et le contenu strict de l'e-mail concerné sont transmis de manière sécurisée à l'IA uniquement au moment de la génération. <strong>Vos e-mails ne sont pas utilisés pour entraîner les modèles d'IA publics.</strong></p>

          <h2 className="text-xl font-bold text-slate-800 mt-8">4. Paiements et Sécurité</h2>
          <p>Les paiements sont traités de manière sécurisée par notre partenaire Stripe. MailtiVoo ne stocke jamais vos numéros de carte bancaire sur ses propres serveurs.</p>

          <h2 className="text-xl font-bold text-slate-800 mt-8">5. Suppression des données</h2>
          <p>Vous pouvez à tout moment révoquer l'accès de MailtiVoo à votre compte Google depuis les paramètres de sécurité de votre compte Google. Pour supprimer l'intégralité de votre compte MailtiVoo, veuillez nous contacter.</p>
        </div>
      </div>
    </div>
  );
}