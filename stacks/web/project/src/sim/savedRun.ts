export interface SavedRunSummary {
  id: string;
  title: string;
  createdAt: string;
}

export function formatSavedRunTitle(title: string, createdAt: Date): string {
  const trimmed = title.trim() || "Untitled run";
  return `${trimmed} - ${createdAt.toISOString().slice(0, 10)}`;
}
