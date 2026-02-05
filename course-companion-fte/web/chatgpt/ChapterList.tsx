import { useSession } from "@gadgetinc/react";
import { useRequestDisplayMode } from "@gadgetinc/react-chatgpt-apps";
import { Button } from "@openai/apps-sdk-ui/components/Button";
import { Expand } from "@openai/apps-sdk-ui/components/Icon";

const CHAPTERS = [
  {
    id: "1",
    title: "Introduction to AI Agents",
    order: 1,
    difficulty_level: "BEGINNER",
    estimated_time: 30,
    description: "Big-picture stuff: what agents are, why they matter, and how they're different from regular scripts or chatbots."
  },
  {
    id: "2",
    title: "Understanding MCP (Model Context Protocol)",
    order: 2,
    difficulty_level: "BEGINNER",
    estimated_time: 30,
    description: "You'll learn how context, tools, and memory are structured so agents can actually do things reliably."
  },
  {
    id: "3",
    title: "Creating Your First Agent",
    order: 3,
    difficulty_level: "BEGINNER",
    estimated_time: 30,
    description: "Hands-on time! You'll wire up an agent and see it work end to end."
  },
  {
    id: "4",
    title: "Building Reusable Skills",
    order: 4,
    difficulty_level: "BEGINNER",
    estimated_time: 30,
    description: "This is where things level up: turning logic into reusable, composable skills you can plug into future agents."
  }
];

const ChapterList = () => {
  const displayMode = useRequestDisplayMode();

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="w-full flex justify-end mb-4">
        {displayMode && (
          <Button
            color="secondary"
            variant="soft"
            aria-label="Enter fullscreen"
            className="rounded-full size-10"
            onClick={() => displayMode("fullscreen")}
          >
            <Expand />
          </Button>
        )}
      </div>

      <div className="mb-6">
        <h2 className="text-xl font-semibold tracking-tight mb-2">📚 Course Chapters</h2>
        <p className="text-sm text-gray-600">Master AI Agent Development with these interactive lessons</p>
      </div>

      <div className="flex flex-col gap-3">
        {CHAPTERS.map((chapter, index) => (
          <div
            key={chapter.id}
            className="group bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-500 hover:shadow-md transition-all cursor-pointer"
            onClick={() => {
              // TODO: Call get_chapter tool when clicked
              console.log("Chapter clicked:", chapter.id);
            }}
          >
            <div className="flex items-center gap-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-indigo-600 text-white flex items-center justify-center font-semibold text-sm">
                {index + 1}
              </div>

              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-gray-900 mb-1">{chapter.title}</h3>
                <div className="flex items-center gap-2 text-xs text-gray-600">
                  <span className="px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-semibold">
                    {chapter.difficulty_level}
                  </span>
                  <span>⏱️ ~{chapter.estimated_time} min</span>
                </div>
                <p className="text-sm text-gray-500 mt-2 line-clamp-2">{chapter.description}</p>
              </div>

              <div className="text-gray-400 group-hover:text-blue-500 transition-colors">
                →
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-900">
          💡 <strong>Tip:</strong> Complete chapters in order to build your AI agent skills step by step!
        </p>
      </div>
    </div>
  );
};

export default ChapterList;
