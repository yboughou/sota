import React, { useState, useEffect } from 'react';
import { GameCard } from '../types';
import { generateImage } from '../services/imageApi';

interface CardProps {
  card: GameCard;
  onClick: () => void;
}

const Card: React.FC<CardProps> = ({ card, onClick }) => {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (card.type === 'image' && card.isFlipped && !imageUrl && !isLoading) {
      loadImage();
    }
  }, [card.isFlipped, card.type]);

  const loadImage = async () => {
    if (card.type === 'image' && !imageUrl) {
      setIsLoading(true);
      try {
                  const response = await generateImage({
            prompt: card.content,
            provider: 'openai' // You can change this to 'openai' or 'unsplash'
          });
        setImageUrl(response.imageUrl);
      } catch (error) {
        console.error('Failed to load image:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const getCardContent = () => {
    if (card.type === 'term') {
      return card.content;
    } else {
      if (isLoading) {
        return (
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '5px' }}>⏳</div>
            <div>Loading...</div>
          </div>
        );
      }
      
      if (imageUrl) {
        return (
          <img 
            src={imageUrl} 
            alt={card.content}
            style={{ 
              width: '100%', 
              height: '100%', 
              objectFit: 'cover',
              borderRadius: '15px'
            }} 
          />
        );
      }
      
      // Show a placeholder with the prompt text for now
      return (
        <div style={{ textAlign: 'center', padding: '10px' }}>
          <div style={{ fontSize: '2rem', marginBottom: '10px' }}>📷</div>
          <div style={{ fontSize: '0.8rem', color: '#666' }}>
            {card.content.substring(0, 50)}...
          </div>
        </div>
      );
    }
  };

  const getCardClassName = () => {
    let className = 'card';
    if (card.isFlipped) className += ' flipped';
    if (card.isMatched) className += ' matched';
    return className;
  };

  return (
    <div className={getCardClassName()} onClick={onClick}>
      {card.isFlipped ? (
        <div className="card-content card-front">
          {getCardContent()}
        </div>
      ) : (
        <div className="card-content card-back">
          ?
        </div>
      )}
    </div>
  );
};

export default Card; 