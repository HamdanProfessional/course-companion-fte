import { getWidgets } from "vite-plugin-chatgpt-widgets";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { FastifyRequest } from "fastify";
import path from "path";
import { getViteHandle } from "gadget-server/vite";

/**
 * Create MCP server to be used by external clients
 *
 */
export const createMCPServer = async (request: FastifyRequest) => {
  const mcpServer = new McpServer({
    name: "example-mcp",
    version: "1.0.0",
  });

  // use actAsSession to access the API client with the permissions of the current session
  const api = request.api.actAsSession;
  const logger = request.logger;

  // get a handle to either the vite dev server in development or the manifest path in production
  const viteHandle = await getViteHandle(request.server);

  // Get the HTML snippet for each widget
  const widgets = await getWidgets("web/chatgpt", viteHandle);

  // Register each widget's HTML snippet as a resource for exposure to ChatGPT
  for (const widget of widgets) {
    const resourceName = `widget-${widget.name.toLowerCase()}`;
    const resourceUri = `ui://widget/${widget.name}.html`;

    mcpServer.registerResource(
      resourceName,
      resourceUri,
      {
        title: widget.name,
        description: `ChatGPT widget for ${widget.name}`,
      },
      async () => {
        return {
          contents: [
            {
              uri: resourceUri,
              mimeType: "text/html+skybridge",
              text: widget.content,
              _meta: getResourceMeta(),
            },
          ],
        };
      }
    );
  }

  // Course Companion: List Chapters (calls VPS backend)
  mcpServer.registerTool(
    "listChapters",
    {
      title: "List Course Chapters",
      description: "Shows all available chapters in the AI Agent Development course",
      annotations: { readOnlyHint: true },
      _meta: {
        "openai/outputTemplate": "ui://widget/ChapterList.html",
        "openai/toolBehavior": "interactive",
      },
    },
    async (params) => {
      // Call VPS backend API
      const response = await fetch("https://sse.testservers.online/api/v1/chapters");
      const chapters = await response.json();

      return {
        structuredContent: { chapters },
        content: [
          {
            type: "text",
            text: `Found ${chapters.length} chapters in the course`
          }
        ]
      };
    }
  );

  // Course Companion: Get Quiz (calls VPS backend)
  mcpServer.registerTool(
    "getQuiz",
    {
      title: "Get Course Quiz",
      description: "Returns a quiz to test knowledge of AI Agents fundamentals",
      annotations: { readOnlyHint: true },
      _meta: {
        "openai/outputTemplate": "ui://widget/Quiz.html",
        "openai/toolBehavior": "interactive",
      },
    },
    async (params) => {
      // Call VPS backend API to get quizzes
      const response = await fetch("https://sse.testservers.online/api/v1/quizzes");
      const quizzes = await response.json();

      // Get the first quiz (for demo purposes)
      const quizData = quizzes[0];

      // Transform the quiz data to match expected format
      const quiz = {
        id: quizData.id,
        title: quizData.title,
        difficulty: quizData.difficulty,
        questions: quizData.questions || []
      };

      return {
        structuredContent: { quiz },
        content: [
          {
            type: "text",
            text: `Quiz: ${quiz.title} (${quiz.difficulty}, ${quiz.questions.length} questions)`
          }
        ]
      };
    }
  );

  // Course Companion: Get Adaptive Learning Path (Phase 2 - Premium)
  mcpServer.registerTool(
    "getAdaptivePath",
    {
      title: "Get Adaptive Learning Path",
      description: "Generates personalized learning recommendations based on your progress (Premium feature)",
      annotations: { readOnlyHint: true },
      _meta: {
        "openai/toolBehavior": "interactive",
      },
    },
    async (params) => {
      // Check if user has premium access
      const userId = params.user_id || "current_user";

      // Call VPS Phase 2 endpoint
      const response = await fetch(
        `https://sse.testservers.online/api/v1/adaptive/recommendations?user_id=${userId}`
      );

      if (!response.ok) {
        return {
          structuredContent: {
            error: "Premium feature",
            message: "Adaptive learning paths are available for Premium and Pro subscribers."
          },
          content: [
            {
              type: "text",
              text: "🔓 This is a Premium feature! Upgrade your subscription to access personalized learning paths that adapt to your progress and learning style."
            }
          ]
        };
      }

      const recommendations = await response.json();

      return {
        structuredContent: { recommendations },
        content: [
          {
            type: "text",
            text: `Based on your progress, I recommend: ${recommendations.next_chapters?.join(", ") || "Continue with current chapter"}`
          }
        ]
      };
    }
  );

  // power the @gadgetinc/react-chatgpt-apps Provider to make auth'd requests from widgets using the 'api' client
  mcpServer.registerTool(
    "__getGadgetAuthTokenV1",
    {
      title: "Get the gadget auth token",
      description:
        "Gets the gadget auth token. Should never be called by LLMs or ChatGPT -- only used for internal auth machinery.",
      _meta: {
        // ensure widgets can invoke this tool to get the token
        "openai/widgetAccessible": true,
      },
    },
    async () => {
      if (!request.headers["authorization"]) {
        return {
          structuredContent: { token: null },
          content: [],
        };
      }

      const [scheme, token] = request.headers["authorization"].split(" ", 2);
      if (scheme !== "Bearer") {
        return {
          structuredContent: { error: "incorrect token scheme", token: null },
          content: [],
        };
      }

      return {
        structuredContent: { token, scheme },
        content: [],
      };
    }
  );

  return mcpServer;
};

type ResourceMeta = {
  "openai/widgetPrefersBorder": boolean;
  "openai/widgetDomain": string;
  "openai/widgetCSP"?: {
    connect_domains: string[];
    resource_domains: string[];
  };
};

const getResourceMeta = () => {
  const _meta: ResourceMeta = {
    "openai/widgetPrefersBorder": true,
    "openai/widgetDomain": process.env.GADGET_APP_URL!,
  };

  if (process.env.NODE_ENV == "production") {
    _meta["openai/widgetCSP"] = {
      // Maps to `connect-src` rule in the iframe CSP
      connect_domains: [process.env.GADGET_APP_URL!],
      // Maps to style-src, style-src-elem, img-src, font-src, media-src etc. in the iframe CSP
      resource_domains: [process.env.GADGET_APP_URL!, "https://assets.gadget.dev", "https://app-assets.gadget.dev"],
    };
  }

  return _meta;
};