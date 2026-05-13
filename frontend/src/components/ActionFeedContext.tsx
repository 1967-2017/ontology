"use client";

import { createContext, ReactNode, useContext, useMemo, useState } from "react";

import { AgentAction } from "@/types/ontology";

type ActionFeedItem = {
  id: string;
  action: AgentAction;
};

type ActionFeedContextValue = {
  items: ActionFeedItem[];
  pushAction: (action: AgentAction) => void;
};

const ActionFeedContext = createContext<ActionFeedContextValue | null>(null);

export function ActionFeedProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ActionFeedItem[]>([]);

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
    }),
    [items],
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
