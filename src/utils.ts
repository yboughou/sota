import { GameCard, GameData } from './types';

// Fisher-Yates shuffle algorithm
export function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

// Create game cards from game data
export function createGameCards(gameData: GameData[]): GameCard[] {
  const cards: GameCard[] = [];
  
  gameData.forEach((item, index) => {
    // Create term card
    cards.push({
      id: `term-${index}`,
      type: 'term',
      content: item.term,
      pairId: `pair-${index}`,
      isFlipped: false,
      isMatched: false
    });
    
    // Create image card
    cards.push({
      id: `image-${index}`,
      type: 'image',
      content: item.image_prompt,
      pairId: `pair-${index}`,
      isFlipped: false,
      isMatched: false
    });
  });
  
  return shuffleArray(cards);
}

// Format time as MM:SS
export function formatTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Check if two cards are a match
export function isMatch(card1: GameCard, card2: GameCard): boolean {
  return card1.pairId === card2.pairId && card1.id !== card2.id;
} 