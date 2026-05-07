
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchOpportunities(accessToken: string, refreshToken: string) {
  const response = await fetch(`${API_URL}/threads/opportunities`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ access_token: accessToken, refresh_token: refreshToken }),
  });
  if (response.status === 401) {
    throw new Error("AUTH_EXPIRED"); // On lance un mot-clé précis
  }

  if (!response.ok) throw new Error("Erreur lors de la récupération des opportunités");
  return response.json();
}

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

export async function sendReply(threadId: string, accessToken: string, refreshToken: string, draftText: string) {
  const response = await fetch(`${API_URL}/threads/${threadId}/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      access_token: accessToken, 
      refresh_token: refreshToken,
      draft_text: draftText 
    }),
  });
  if (response.status === 401) {
    throw new Error("AUTH_EXPIRED"); // On lance un mot-clé précis
  }
  return response.json();
}