import React from 'react';
import { QuizQuestion } from '../types';

interface QuizProps {
  question: QuizQuestion;
  onAnswer: (answerIndex: number) => void;
  selectedAnswer: number | null;
  isAnswered: boolean;
}

const Quiz: React.FC<QuizProps> = ({ question, onAnswer, selectedAnswer, isAnswered }) => {
  const getOptionClass = (index: number) => {
    if (!isAnswered) {
      return 'quiz-option';
    }
    
    if (index === question.correctAnswer) {
      return 'quiz-option correct';
    }
    
    if (index === selectedAnswer && index !== question.correctAnswer) {
      return 'quiz-option incorrect';
    }
    
    return 'quiz-option';
  };

  return (
    <div className="quiz-container">
      <div className="question-header">
        <h2>{question.question}</h2>
      </div>
      
      <div className="options-container">
        {question.options.map((option, index) => (
          <button
            key={index}
            className={getOptionClass(index)}
            onClick={() => !isAnswered && onAnswer(index)}
            disabled={isAnswered}
          >
            {option}
          </button>
        ))}
      </div>
      
      {isAnswered && (
        <div className="explanation">
          <h3>Explanation:</h3>
          <p>{question.explanation}</p>
        </div>
      )}
    </div>
  );
};

export default Quiz; 