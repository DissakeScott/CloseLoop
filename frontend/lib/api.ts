
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ⚡ 1. LECTURE RAPIDE (Lit Supabase en 0.1s)
export const fetchOpportunities = async (email: string) => {
  if (!email) throw new Error("Email manquant");
  
  const response = await fetch(`${API_URL}/threads/opportunities?email=${encodeURIComponent(email)}`, {
    method: "GET",
  });

  if (!response.ok) {
    if (response.status === 401) throw new Error("AUTH_EXPIRED");
    throw new Error("Erreur lors de la récupération des opportunités");
  }

  return response.json();
};

// 🤖 2. SYNCHRONISATION IA (Prend 40s)
export const syncOpportunities = async (email: string, accessToken: string, refreshToken: string) => {
  const response = await fetch(`${API_URL}/threads/sync-opportunities`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      email, 
      access_token: accessToken, 
      refresh_token: refreshToken 
    }),
  });

  if (!response.ok) {
    if (response.status === 401) throw new Error("AUTH_EXPIRED");
    throw new Error("Erreur lors de la synchronisation");
  }

  return response.json();
};

export async function generateDraft(threadId: string, accessToken: string, refreshToken: string, tone: string = "naturel") {
  const response = await fetch(`${API_URL}/threads/${threadId}/draft`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      access_token: accessToken, 
      refresh_token: refreshToken,
      tone: tone // <-- On envoie le ton au backend !
    }),
  });
  if (response.status === 401) {
    throw new Error("AUTH_EXPIRED"); // On lance un mot-clé précis
  }
  return response.json();
}

export const sendReply = async (threadId: string, accessToken: string, refreshToken: string, draftText: string, email: string) => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const response = await fetch(`${apiUrl}/threads/${threadId}/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      access_token: accessToken, 
      refresh_token: refreshToken, 
      draft_text: draftText,
      email: email 
    }),
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    if (errorData.detail === "QUOTA_REACHED") {
      throw new Error("QUOTA_REACHED");
    }
    throw new Error(errorData.detail || "Erreur d'envoi");
  }
  return response.json();
};