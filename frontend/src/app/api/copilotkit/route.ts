import { copilotRuntimeNextJSAppRouterEndpoint } from "@copilotkit/runtime";

import { copilotRuntime } from "@/lib/copilot-runtime";

const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
  endpoint: "/api/copilotkit",
  runtime: copilotRuntime,
});

export const POST = handleRequest;
