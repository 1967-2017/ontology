import { ChatWorkspace } from "@/components/ChatWorkspace";
import { CopilotShell } from "@/components/CopilotShell";

export default function HomePage() {
  return (
    <CopilotShell>
      <ChatWorkspace />
    </CopilotShell>
  );
}
