import React, { useState, useEffect } from 'react';
import Quiz from './components/Quiz';
import QuizGenerator from './components/QuizGenerator';
import { QuizData, QuizState } from './types';
import quizData from '../quiz-data.json';
import './App.css';

const App: React.FC = () => {
  const [quizState, setQuizState] = useState<QuizState>({
    currentQuestionIndex: 0,
    score: 0,
    answers: [],
    isComplete: false,
    showResults: false,
    timeElapsed: 0
  });

  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [startTime, setStartTime] = useState<number | null>(null);
  const [showGenerator, setShowGenerator] = useState(false);
  const [currentQuizData, setCurrentQuizData] = useState<QuizData>(quizData);

  const data: QuizData = currentQuizData;

  useEffect(() => {
    if (!startTime) {
      setStartTime(Date.now());
    }
  }, [startTime]);

  useEffect(() => {
    if (startTime && !quizState.isComplete) {
      const timer = setInterval(() => {
        setQuizState(prev => ({
          ...prev,
          timeElapsed: Date.now() - startTime
        }));
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [startTime, quizState.isComplete]);

  const handleAnswer = (answerIndex: number) => {
    setSelectedAnswer(answerIndex);
    setIsAnswered(true);

    const isCorrect = answerIndex === data.questions[quizState.currentQuestionIndex].correctAnswer;
    
    setTimeout(() => {
      setQuizState(prev => ({
        ...prev,
        score: isCorrect ? prev.score + 1 : prev.score,
        answers: [...prev.answers, answerIndex],
        currentQuestionIndex: prev.currentQuestionIndex + 1,
        isComplete: prev.currentQuestionIndex + 1 >= data.questions.length
      }));
      
      setSelectedAnswer(null);
      setIsAnswered(false);
    }, 2000);
  };

  const startNewQuiz = () => {
    setQuizState({
      currentQuestionIndex: 0,
      score: 0,
      answers: [],
      isComplete: false,
      showResults: false,
      timeElapsed: 0
    });
    setSelectedAnswer(null);
    setIsAnswered(false);
    setStartTime(Date.now());
    setShowGenerator(false);
  };

  const handleQuizGenerated = (newQuizData: QuizData) => {
    setCurrentQuizData(newQuizData);
    startNewQuiz();
  };

  const showResults = () => {
    setQuizState(prev => ({ ...prev, showResults: true }));
  };

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (showGenerator) {
    return (
      <div className="app">
        <div className="quiz-header">
          <h1>AI Quiz Generator</h1>
          <p>Create custom quizzes using your local Qwen model</p>
        </div>
        
        <QuizGenerator onQuizGenerated={handleQuizGenerated} />
        
        <div className="navigation-buttons">
          <button className="nav-button" onClick={() => setShowGenerator(false)}>
            Back to Quiz
          </button>
        </div>
      </div>
    );
  }

  if (quizState.showResults) {
    const percentage = Math.round((quizState.score / data.questions.length) * 100);
    return (
      <div className="app">
        <div className="quiz-header">
          <h1>{data.title}</h1>
          <p>{data.description}</p>
        </div>
        
        <div className="results-container">
          <h2>Quiz Complete!</h2>
          <div className="score-display">
            <p>Your Score: {quizState.score}/{data.questions.length} ({percentage}%)</p>
            <p>Time: {formatTime(quizState.timeElapsed)}</p>
          </div>
          
          <div className="question-review">
            {data.questions.map((question, index) => (
              <div key={question.id} className="review-item">
                <h3>Question {index + 1}</h3>
                <p>{question.question}</p>
                <p className={quizState.answers[index] === question.correctAnswer ? 'correct' : 'incorrect'}>
                  Your Answer: {question.options[quizState.answers[index]]}
                </p>
                <p className="correct-answer">
                  Correct Answer: {question.options[question.correctAnswer]}
                </p>
                <p className="explanation">{question.explanation}</p>
              </div>
            ))}
          </div>
          
          <div className="action-buttons">
            <button className="restart-button" onClick={startNewQuiz}>
              Take Quiz Again
            </button>
            <button className="generate-button" onClick={() => setShowGenerator(true)}>
              Generate New Quiz
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (quizState.isComplete) {
    return (
      <div className="app">
        <div className="quiz-header">
          <h1>{data.title}</h1>
          <p>{data.description}</p>
        </div>
        
        <div className="completion-container">
          <h2>Quiz Complete!</h2>
          <p>Your Score: {quizState.score}/{data.questions.length}</p>
          <p>Time: {formatTime(quizState.timeElapsed)}</p>
          <div className="action-buttons">
            <button className="results-button" onClick={showResults}>
              View Results
            </button>
            <button className="generate-button" onClick={() => setShowGenerator(true)}>
              Generate New Quiz
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentQuestion = data.questions[quizState.currentQuestionIndex];

  return (
    <div className="app">
      <div className="quiz-header">
        <h1>{data.title}</h1>
        <p>{data.description}</p>
        <div className="quiz-progress">
          <p>Question {quizState.currentQuestionIndex + 1} of {data.questions.length}</p>
          <p>Score: {quizState.score}</p>
          <p>Time: {formatTime(quizState.timeElapsed)}</p>
        </div>
      </div>
      
      <Quiz
        question={currentQuestion}
        onAnswer={handleAnswer}
        selectedAnswer={selectedAnswer}
        isAnswered={isAnswered}
      />
      
      <div className="navigation-buttons">
        <button className="nav-button" onClick={() => setShowGenerator(true)}>
          Generate Custom Quiz
        </button>
      </div>
    </div>
  );
};

export default App; 