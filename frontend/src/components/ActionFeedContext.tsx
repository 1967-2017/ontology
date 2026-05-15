"use client";

import { createContext, ReactNode, useContext, useEffect, useMemo, useState } from "react";

import { AgentAction, ProjectDocument } from "@/types/ontology";

type ActionFeedItem = {
  id: string;
  action: AgentAction;
};

type ActionFeedContextValue = {
  items: ActionFeedItem[];
  pushAction: (action: AgentAction) => void;
  sessionDocuments: ProjectDocument[];
  replaceSessionDocuments: (documents: ProjectDocument[]) => void;
  upsertSessionDocument: (document: ProjectDocument) => void;
  patchSessionDocument: (documentId: number, updates: Partial<ProjectDocument>) => void;
  removeSessionDocuments: (documentIds: number[]) => void;
};

const ActionFeedContext = createContext<ActionFeedContextValue | null>(null);

export function ActionFeedProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ActionFeedItem[]>([]);
  const [sessionDocuments, setSessionDocuments] = useState<ProjectDocument[]>([]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const raw = window.localStorage.getItem("pending-upload-documents");
    if (!raw) {
      return;
    }
    try {
      const parsed = JSON.parse(raw) as ProjectDocument[];
      setSessionDocuments(Array.isArray(parsed) ? parsed : []);
    } catch {
      window.localStorage.removeItem("pending-upload-documents");
    }
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    window.localStorage.setItem("pending-upload-documents", JSON.stringify(sessionDocuments));
  }, [sessionDocuments]);

  const value = useMemo<ActionFeedContextValue>(
    () => ({
      items,
      pushAction: (action) =>
        setItems((current) => [
          {
            id: `${action.name}-${Date.now()}-${current.length}`,
            action,
          },
          ...current,
        ]),
      sessionDocuments,
      replaceSessionDocuments: (documents) => setSessionDocuments(documents),
      upsertSessionDocument: (document) =>
        setSessionDocuments((current) => [document, ...current.filter((item) => item.document_id !== document.document_id)]),
      patchSessionDocument: (documentId, updates) =>
        setSessionDocuments((current) =>
          current.map((document) => (document.document_id === documentId ? { ...document, ...updates } : document)),
        ),
      removeSessionDocuments: (documentIds) => {
        if (documentIds.length === 0) {
          return;
        }
        setSessionDocuments((current) => current.filter((document) => !documentIds.includes(document.document_id)));
      },
    }),
    [items, sessionDocuments],
  );

  return <ActionFeedContext.Provider value={value}>{children}</ActionFeedContext.Provider>;
}

export function useActionFeed() {
  const context = useContext(ActionFeedContext);
  if (!context) {
    throw new Error("useActionFeed must be used inside ActionFeedProvider");
  }
  return context;
}
