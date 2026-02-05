// Chapter List Widget for Course Companion FTE
import React, { useState, useEffect } from 'react';

// Types
interface Chapter {
  id: string;
  title: string;
  order: number;
  difficulty_level: string;
  estimated_time: number;
}

interface ChapterListData {
  chapters: Chapter[];
}

// Main Chapter List Component
function ChapterListWidget() {
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get tool output from window.openai
  useEffect(() => {
    try {
      const toolOutput = (window.openai as any)?.toolOutput as ChapterListData;
      if (toolOutput?.chapters) {
        setChapters(toolOutput.chapters);
      }
      setLoading(false);
    } catch (err) {
      setError('Failed to load chapters');
      setLoading(false);
    }
  }, []);

  // Get difficulty color
  function getDifficultyColor(level: string): string {
    switch (level) {
      case 'BEGINNER': return '#10b981';
      case 'INTERMEDIATE': return '#f59e0b';
      case 'ADVANCED': return '#ef4444';
      default: return '#6b7280';
    }
  }

  // View chapter content
  async function viewChapter(chapterId: string, title: string) {
    try {
      const callTool = (window.openai as any)?.callTool;
      if (callTool) {
        await callTool('get_chapter', { chapter_id: chapterId });
        // Request fullscreen for better reading experience
        (window.openai as any)?.requestLayout('fullscreen');
      }
    } catch (err) {
      setError('Failed to load chapter');
    }
  }

  if (loading) {
    return (
      <div className="chapter-list-widget">
        <div className="loading">Loading chapters...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chapter-list-widget">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="chapter-list-widget">
      <header>
        <h2>📚 Course Chapters</h2>
        <span className="count">{chapters.length} chapters</span>
      </header>

      <div className="chapters">
        {chapters.map((chapter, index) => (
          <div
            key={chapter.id}
            className="chapter-card"
            onClick={() => viewChapter(chapter.id, chapter.title)}
          >
            <div className="chapter-number">{index + 1}</div>
            <div className="chapter-info">
              <h3>{chapter.title}</h3>
              <div className="meta">
                <span
                  className="difficulty"
                  style={{ backgroundColor: getDifficultyColor(chapter.difficulty_level) }}
                >
                  {chapter.difficulty_level}
                </span>
                <span className="duration">⏱️ {chapter.estimated_time} min</span>
              </div>
            </div>
            <div className="arrow">→</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Mount the widget
const root = document.getElementById('root');
if (root) {
  React.createElement(ChapterListWidget);
  // @ts-ignore
  ReactDOM.createRoot(root).render(<ChapterListWidget />);
}

export default ChapterListWidget;
