import Link from 'next/link';
import { BookOpen } from 'lucide-react';

export default function LearnPage() {
  const lessons = [
    {
      title: 'How the GRID Routes Your Request',
      slug: 'grid-routing',
      description: 'Learn how Sentient GRID intelligently routes queries to specialized agents',
      level: 'beginner'
    },
    {
      title: 'Understanding OML: Open, Monetizable, Loyal',
      slug: 'oml',
      description: 'Discover the principles behind Sentient\'s Open Model License',
      level: 'beginner'
    },
    {
      title: 'Agents and Their Roles',
      slug: 'agents',
      description: 'Explore how specialized agents work together in the GRID',
      level: 'intermediate'
    },
  ];

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-4">Learn About Sentient</h1>
        <p className="text-muted-foreground mb-12">
          Explore interactive lessons about GRID, agents, and the future of open-source AGI
        </p>

        <div className="grid gap-6">
          {lessons.map((lesson) => (
            <Link
              key={lesson.slug}
              href={`/learn/${lesson.slug}`}
              className="block p-6 bg-card border border-border rounded-lg hover:border-primary transition-colors"
            >
              <div className="flex items-start gap-4">
                <div className="p-3 bg-primary/10 rounded-lg">
                  <BookOpen className="h-6 w-6 text-primary" />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold mb-2">{lesson.title}</h3>
                  <p className="text-muted-foreground mb-3">{lesson.description}</p>
                  <span className="inline-block px-3 py-1 text-xs bg-secondary/20 text-secondary rounded-full">
                    {lesson.level}
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
