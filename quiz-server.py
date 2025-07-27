from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
import requests
from typing import List, Optional
import os

app = FastAPI(title="Quiz Generator API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuizRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    num_questions: int = 5

class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_answer: int
    explanation: str

class QuizResponse(BaseModel):
    title: str
    description: str
    questions: List[QuizQuestion]

# Qwen API endpoint (assuming it's running locally)
QWEN_API_URL = "http://localhost:8080/generate"

def generate_quiz_with_qwen(topic: str, difficulty: str, num_questions: int) -> QuizResponse:
    """Generate quiz questions using the local Qwen model"""
    
    prompt = f"""
Generate a {difficulty} difficulty quiz about {topic} with {num_questions} multiple choice questions.

Format the response as a JSON object with this exact structure:
{{
    "title": "Quiz Title",
    "description": "Quiz description",
    "questions": [
        {{
            "id": 1,
            "question": "Question text here?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Explanation of why this is the correct answer"
        }}
    ]
}}

Requirements:
- Each question should have exactly 4 options (A, B, C, D)
- correct_answer should be the index (0-3) of the correct option
- Questions should be engaging and educational
- Explanations should be clear and informative
- Make sure the JSON is valid and properly formatted
"""

    try:
        # Call the local Qwen API
        response = requests.post(
            QWEN_API_URL,
            json={"prompt": prompt},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Try to parse the response as JSON
            if isinstance(result, str):
                # If it's a string, try to extract JSON from it
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("No valid JSON found in response")
            
            # Validate and return the quiz
            if "questions" in result and "title" in result:
                return QuizResponse(**result)
            else:
                raise ValueError("Invalid quiz format in response")
        else:
            raise HTTPException(status_code=500, detail=f"Qwen API error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        # If Qwen is not available, return a fallback quiz
        print(f"Qwen server not available: {str(e)}")
        return generate_fallback_quiz(topic, difficulty, num_questions)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response from Qwen: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")

def generate_fallback_quiz(topic: str, difficulty: str, num_questions: int) -> QuizResponse:
    """Generate a fallback quiz when Qwen is not available"""
    
    # Pre-made quizzes for different topics
    fallback_quizzes = {
        "Historical Events": {
            "title": f"{topic} Quiz",
            "description": f"A {difficulty} difficulty quiz about {topic}",
            "questions": [
                {
                    "id": 1,
                    "question": "When did World War II end?",
                    "options": ["1943", "1944", "1945", "1946"],
                    "correct_answer": 2,
                    "explanation": "World War II ended in 1945 with the surrender of Germany in May and Japan in September."
                },
                {
                    "id": 2,
                    "question": "Who was the first President of the United States?",
                    "options": ["Thomas Jefferson", "John Adams", "George Washington", "Benjamin Franklin"],
                    "correct_answer": 2,
                    "explanation": "George Washington was the first President of the United States, serving from 1789 to 1797."
                },
                {
                    "id": 3,
                    "question": "In what year did the Berlin Wall fall?",
                    "options": ["1987", "1988", "1989", "1990"],
                    "correct_answer": 2,
                    "explanation": "The Berlin Wall fell on November 9, 1989, marking the end of the Cold War."
                },
                {
                    "id": 4,
                    "question": "Who was the first Emperor of Rome?",
                    "options": ["Julius Caesar", "Augustus", "Nero", "Caligula"],
                    "correct_answer": 1,
                    "explanation": "Augustus was the first Emperor of Rome, ruling from 27 BC to 14 AD."
                },
                {
                    "id": 5,
                    "question": "When did the American Civil War begin?",
                    "options": ["1860", "1861", "1862", "1863"],
                    "correct_answer": 1,
                    "explanation": "The American Civil War began in 1861 with the attack on Fort Sumter."
                }
            ]
        },
        "Science and Technology": {
            "title": f"{topic} Quiz",
            "description": f"A {difficulty} difficulty quiz about {topic}",
            "questions": [
                {
                    "id": 1,
                    "question": "What is the chemical symbol for gold?",
                    "options": ["Ag", "Au", "Fe", "Cu"],
                    "correct_answer": 1,
                    "explanation": "Au is the chemical symbol for gold, from the Latin word 'aurum'."
                },
                {
                    "id": 2,
                    "question": "Which planet is known as the Red Planet?",
                    "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                    "correct_answer": 1,
                    "explanation": "Mars is known as the Red Planet due to its reddish appearance from iron oxide on its surface."
                },
                {
                    "id": 3,
                    "question": "What is the largest organ in the human body?",
                    "options": ["Heart", "Brain", "Liver", "Skin"],
                    "correct_answer": 3,
                    "explanation": "The skin is the largest organ in the human body, covering about 20 square feet."
                },
                {
                    "id": 4,
                    "question": "Who invented the World Wide Web?",
                    "options": ["Bill Gates", "Tim Berners-Lee", "Steve Jobs", "Mark Zuckerberg"],
                    "correct_answer": 1,
                    "explanation": "Tim Berners-Lee invented the World Wide Web in 1989 while working at CERN."
                },
                {
                    "id": 5,
                    "question": "What is the hardest natural substance on Earth?",
                    "options": ["Steel", "Diamond", "Granite", "Quartz"],
                    "correct_answer": 1,
                    "explanation": "Diamond is the hardest natural substance on Earth, scoring 10 on the Mohs scale."
                }
            ]
        },
        "World Geography": {
            "title": f"{topic} Quiz",
            "description": f"A {difficulty} difficulty quiz about {topic}",
            "questions": [
                {
                    "id": 1,
                    "question": "What is the capital of Australia?",
                    "options": ["Sydney", "Melbourne", "Canberra", "Brisbane"],
                    "correct_answer": 2,
                    "explanation": "Canberra is the capital of Australia, chosen as a compromise between Sydney and Melbourne."
                },
                {
                    "id": 2,
                    "question": "Which is the largest continent by area?",
                    "options": ["North America", "Africa", "Asia", "Europe"],
                    "correct_answer": 2,
                    "explanation": "Asia is the largest continent, covering about 30% of Earth's land area."
                },
                {
                    "id": 3,
                    "question": "What is the longest river in the world?",
                    "options": ["Amazon", "Nile", "Yangtze", "Mississippi"],
                    "correct_answer": 1,
                    "explanation": "The Nile is the longest river in the world, stretching about 4,135 miles."
                },
                {
                    "id": 4,
                    "question": "Which country has the most islands?",
                    "options": ["Indonesia", "Sweden", "Finland", "Norway"],
                    "correct_answer": 1,
                    "explanation": "Sweden has the most islands in the world, with over 267,570 islands."
                },
                {
                    "id": 5,
                    "question": "What is the smallest country in the world?",
                    "options": ["Monaco", "San Marino", "Vatican City", "Liechtenstein"],
                    "correct_answer": 2,
                    "explanation": "Vatican City is the smallest country in the world, covering just 0.17 square miles."
                }
            ]
        },
        "Literature and Authors": {
            "title": f"{topic} Quiz",
            "description": f"A {difficulty} difficulty quiz about {topic}",
            "questions": [
                {
                    "id": 1,
                    "question": "Who wrote 'Pride and Prejudice'?",
                    "options": ["Charlotte Brontë", "Jane Austen", "Emily Brontë", "Mary Shelley"],
                    "correct_answer": 1,
                    "explanation": "Jane Austen wrote 'Pride and Prejudice', published in 1813."
                },
                {
                    "id": 2,
                    "question": "What is the pen name of Samuel Clemens?",
                    "options": ["Mark Twain", "O. Henry", "Lewis Carroll", "George Eliot"],
                    "correct_answer": 0,
                    "explanation": "Samuel Clemens wrote under the pen name Mark Twain."
                },
                {
                    "id": 3,
                    "question": "Who wrote '1984'?",
                    "options": ["Aldous Huxley", "George Orwell", "Ray Bradbury", "H.G. Wells"],
                    "correct_answer": 1,
                    "explanation": "George Orwell wrote '1984', published in 1949."
                },
                {
                    "id": 4,
                    "question": "What is the longest novel ever written?",
                    "options": ["War and Peace", "In Search of Lost Time", "Don Quixote", "Les Misérables"],
                    "correct_answer": 1,
                    "explanation": "'In Search of Lost Time' by Marcel Proust is considered the longest novel at about 1.2 million words."
                },
                {
                    "id": 5,
                    "question": "Who wrote 'The Great Gatsby'?",
                    "options": ["Ernest Hemingway", "F. Scott Fitzgerald", "John Steinbeck", "William Faulkner"],
                    "correct_answer": 1,
                    "explanation": "F. Scott Fitzgerald wrote 'The Great Gatsby', published in 1925."
                }
            ]
        },
        "Art and Artists": {
            "title": f"{topic} Quiz",
            "description": f"A {difficulty} difficulty quiz about {topic}",
            "questions": [
                {
                    "id": 1,
                    "question": "Who painted the Mona Lisa?",
                    "options": ["Michelangelo", "Leonardo da Vinci", "Raphael", "Donatello"],
                    "correct_answer": 1,
                    "explanation": "Leonardo da Vinci painted the Mona Lisa between 1503 and 1519."
                },
                {
                    "id": 2,
                    "question": "What art movement was Pablo Picasso associated with?",
                    "options": ["Impressionism", "Cubism", "Surrealism", "Expressionism"],
                    "correct_answer": 1,
                    "explanation": "Pablo Picasso was a co-founder of Cubism along with Georges Braque."
                },
                {
                    "id": 3,
                    "question": "Who painted 'The Starry Night'?",
                    "options": ["Vincent van Gogh", "Claude Monet", "Paul Cézanne", "Henri Matisse"],
                    "correct_answer": 0,
                    "explanation": "Vincent van Gogh painted 'The Starry Night' in 1889."
                },
                {
                    "id": 4,
                    "question": "What is the most expensive painting ever sold?",
                    "options": ["The Scream", "Salvator Mundi", "Interchange", "Nafea Faa Ipoipo"],
                    "correct_answer": 1,
                    "explanation": "Salvator Mundi by Leonardo da Vinci sold for $450.3 million in 2017."
                },
                {
                    "id": 5,
                    "question": "Who sculpted 'David'?",
                    "options": ["Donatello", "Michelangelo", "Bernini", "Cellini"],
                    "correct_answer": 1,
                    "explanation": "Michelangelo sculpted 'David' between 1501 and 1504."
                }
            ]
        },
        "Mathematics": {
            "title": f"{topic} Quiz",
            "description": f"A {difficulty} difficulty quiz about {topic}",
            "questions": [
                {
                    "id": 1,
                    "question": "What is the value of π (pi) to two decimal places?",
                    "options": ["3.12", "3.14", "3.16", "3.18"],
                    "correct_answer": 1,
                    "explanation": "π (pi) is approximately 3.14159, so to two decimal places it's 3.14."
                },
                {
                    "id": 2,
                    "question": "What is the square root of 144?",
                    "options": ["10", "11", "12", "13"],
                    "correct_answer": 2,
                    "explanation": "12 × 12 = 144, so the square root of 144 is 12."
                },
                {
                    "id": 3,
                    "question": "How many degrees are in a triangle?",
                    "options": ["90", "180", "270", "360"],
                    "correct_answer": 1,
                    "explanation": "The sum of all angles in a triangle is always 180 degrees."
                },
                {
                    "id": 4,
                    "question": "What is 2 to the power of 8?",
                    "options": ["128", "256", "512", "1024"],
                    "correct_answer": 1,
                    "explanation": "2^8 = 2 × 2 × 2 × 2 × 2 × 2 × 2 × 2 = 256."
                },
                {
                    "id": 5,
                    "question": "What is the next number in the sequence: 2, 4, 8, 16, __?",
                    "options": ["20", "24", "32", "64"],
                    "correct_answer": 2,
                    "explanation": "Each number is multiplied by 2, so 16 × 2 = 32."
                }
            ]
        },
        "Space and Astronomy": {
            "title": f"{topic} Quiz",
            "description": f"A {difficulty} difficulty quiz about {topic}",
            "questions": [
                {
                    "id": 1,
                    "question": "What is the closest planet to the Sun?",
                    "options": ["Venus", "Mercury", "Earth", "Mars"],
                    "correct_answer": 1,
                    "explanation": "Mercury is the closest planet to the Sun in our solar system."
                },
                {
                    "id": 2,
                    "question": "How many moons does Earth have?",
                    "options": ["0", "1", "2", "3"],
                    "correct_answer": 1,
                    "explanation": "Earth has one natural satellite - the Moon."
                },
                {
                    "id": 3,
                    "question": "What is the largest planet in our solar system?",
                    "options": ["Saturn", "Jupiter", "Neptune", "Uranus"],
                    "correct_answer": 1,
                    "explanation": "Jupiter is the largest planet in our solar system."
                },
                {
                    "id": 4,
                    "question": "What galaxy do we live in?",
                    "options": ["Andromeda", "Milky Way", "Triangulum", "Large Magellanic Cloud"],
                    "correct_answer": 1,
                    "explanation": "We live in the Milky Way galaxy."
                },
                {
                    "id": 5,
                    "question": "What is a light year?",
                    "options": ["Time", "Distance", "Speed", "Energy"],
                    "correct_answer": 1,
                    "explanation": "A light year is a unit of distance - the distance light travels in one year."
                }
            ]
        }
    }
    
    # Return a fallback quiz based on the topic, or default to Historical Events
    if topic in fallback_quizzes:
        quiz_data = fallback_quizzes[topic]
        # Limit to requested number of questions
        quiz_data["questions"] = quiz_data["questions"][:num_questions]
        return QuizResponse(**quiz_data)
    else:
        # Default to Historical Events if topic not found
        quiz_data = fallback_quizzes["Historical Events"]
        quiz_data["questions"] = quiz_data["questions"][:num_questions]
        return QuizResponse(**quiz_data)

@app.get("/")
async def root():
    return {"message": "Quiz Generator API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "quiz-generator"}

@app.post("/api/generate-quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    """Generate a quiz using the local Qwen model"""
    try:
        quiz = generate_quiz_with_qwen(
            topic=request.topic,
            difficulty=request.difficulty,
            num_questions=request.num_questions
        )
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/topics")
async def get_topics():
    """Get a list of suggested quiz topics"""
    topics = [
        "Historical Events",
        "World Geography", 
        "Science and Technology",
        "Literature and Authors",
        "Art and Artists",
        "Mathematics",
        "Space and Astronomy",
        "Ancient Civilizations",
        "Modern Politics",
        "Environmental Science",
        "Music History",
        "Sports Legends",
        "Famous Inventors",
        "World Religions",
        "Oceanography"
    ]
    return {"topics": topics}

@app.get("/api/difficulties")
async def get_difficulties():
    """Get available difficulty levels"""
    difficulties = ["easy", "medium", "hard"]
    return {"difficulties": difficulties}

if __name__ == "__main__":
    print("Starting Quiz Generator API...")
    print("Make sure your Qwen server is running on http://localhost:8080")
    print("API will be available at http://localhost:8000")
    
    uvicorn.run(
        "quiz-server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 