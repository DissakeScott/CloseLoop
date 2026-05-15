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

          <h2 className="text-xl font-bold text-slate-800 mt-8">2. Utilisation de l'API Gmail et des données Google</h2>
          <p>
            L'utilisation et le transfert par MailtiVoo vers toute autre application des informations reçues des API Google respecteront la <a href="https://developers.google.com/terms/api-services-user-data-policy" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">politique relative aux données utilisateur des services API Google (Google API Services User Data Policy)</a>, y compris les exigences d'utilisation limitée (Limited Use requirements).
          </p>
          <div className="bg-slate-100 p-4 rounded-lg mt-4 border border-slate-200">
            <p className="text-slate-800">
              <strong>Protection des données sensibles :</strong> Les jetons d'accès (access tokens) permettant de lire et de générer des brouillons d'e-mails sont chiffrés de manière sécurisée dans notre base de données. Les données de messagerie lues depuis votre boîte de réception sont traitées uniquement de façon éphémère (en mémoire) pour la détection d'opportunités et la génération de brouillons par notre intelligence artificielle. Ces données sensibles ne sont ni stockées à long terme sur nos serveurs, ni vendues, ni partagées avec des tiers à des fins publicitaires.
            </p>
          </div>
          <ul className="list-disc pl-5 space-y-2 mt-4">
            <li><strong>Ce que nous lisons :</strong> Nous accédons à vos métadonnées d'e-mails uniquement pour identifier les messages sans réponse.</li>
            <li><strong>Ce que nous ne faisons PAS :</strong> L'accès humain à vos e-mails est strictement interdit, sauf en cas d'obligation légale ou avec votre consentement explicite pour résoudre un bug technique.</li>
          </ul>

          <h2 className="text-xl font-bold text-slate-800 mt-8">3. Intelligence Artificielle et Données</h2>
          <p>MailtiVoo utilise des modèles d'intelligence artificielle pour générer des brouillons de relance. Les métadonnées et le contenu strict de l'e-mail concerné sont transmis de manière sécurisée à l'IA uniquement au moment de la génération. <strong>Vos e-mails ne sont pas utilisés pour entraîner les modèles d'IA publics.</strong></p>

          <h2 className="text-xl font-bold text-slate-800 mt-8">4. Paiements et Sécurité</h2>
          <p>Les paiements sont traités de manière sécurisée par notre partenaire Stripe. MailtiVoo ne stocke jamais vos numéros de carte bancaire sur ses propres serveurs.</p>

          <h2 className="text-xl font-bold text-slate-800 mt-8">5. Suppression des données</h2>
          <p>Vous pouvez à tout moment révoquer l'accès de MailtiVoo à votre compte Google depuis les paramètres de sécurité de votre compte Google. Pour supprimer l'intégralité de votre compte MailtiVoo et de vos données chiffrées, veuillez nous contacter.</p>
        </div>
      </div>
    </div>
  );
}