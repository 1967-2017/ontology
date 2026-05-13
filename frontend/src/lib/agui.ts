import { AgentAction } from "@/types/ontology";

export type TimelineItem =
  | { id: string; type: "message"; role: "user" | "assistant"; content: string }
  | { id: string; type: "action"; action: AgentAction };

export function toTimelineActions(actions: AgentAction[]): TimelineItem[] {
  return actions.map((action, index) => ({
    id: `${action.name}-${index}-${Date.now()}`,
    type: "action",
    action,
  }));
}
