import React, { useState } from 'react';

interface QuizGeneratorProps {
  onQuizGenerated: (quizData: any) => void;
}

const QuizGenerator: React.FC<QuizGeneratorProps> = ({ onQuizGenerated }) => {
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [numQuestions, setNumQuestions] = useState(5);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');

  const difficulties = [
    { value: 'easy', label: 'Easy' },
    { value: 'medium', label: 'Medium' },
    { value: 'hard', label: 'Hard' }
  ];

  const generateQuiz = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic.');
      return;
    }
    
    setIsGenerating(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/generate-quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          difficulty,
          num_questions: numQuestions
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate quiz');
      }

      const quizData = await response.json();
      
      // Transform the data to match our quiz format
      const transformedQuiz = {
        title: quizData.title,
        description: quizData.description,
        questions: quizData.questions.map((q: any, index: number) => ({
          id: index + 1,
          question: q.question,
          options: q.options,
          correctAnswer: q.correct_answer,
          explanation: q.explanation
        }))
      };

      onQuizGenerated(transformedQuiz);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate quiz');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="quiz-generator">
      <div className="generator-header">
        <h2>Generate Custom Quiz</h2>
        <p>Create a personalized quiz using AI</p>
      </div>

      <div className="generator-form">
        <div className="form-group">
          <label htmlFor="topic">Topic:</label>
          <input
            id="topic"
            type="text"
            placeholder="e.g. Vietnam War"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={isGenerating}
          />
        </div>

        <div className="form-group">
          <label htmlFor="difficulty">Difficulty:</label>
          <select
            id="difficulty"
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            disabled={isGenerating}
          >
            {difficulties.map((d) => (
              <option key={d.value} value={d.value}>{d.label}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="numQuestions">Number of Questions:</label>
          <input
            id="numQuestions"
            type="number"
            min="3"
            max="10"
            value={numQuestions}
            onChange={(e) => setNumQuestions(parseInt(e.target.value))}
            disabled={isGenerating}
          />
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <button
          className="generate-button"
          onClick={generateQuiz}
          disabled={isGenerating}
        >
          {isGenerating ? 'Generating Quiz...' : 'Generate Quiz'}
        </button>
      </div>
    </div>
  );
};

export default QuizGenerator;