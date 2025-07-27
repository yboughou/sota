from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
import requests
from typing import List, Optional
import os
import re

# New imports for LangChain and Hugging Face
from langchain.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.chat_models import ChatOpenAI  # <-- New import for ChatOpenAI

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

# Initialize Hugging Face LLM via LangChain
def initialize_huggingface_llm():
    # Use a higher-accuracy model tailored for your RTX 3050 Ti (e.g. EleutherAI/gpt-neo-2.7B)
    model_name = "EleutherAI/gpt-neo-2.7B"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    hf_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, max_length=1024)
    return HuggingFacePipeline(pipeline=hf_pipeline)

def initialize_chatopenai_llm():
    # Use ChatOpenAI with a specific model (e.g. gpt-3.5-turbo) and parameters
    return ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2, api_key=os.getenv("OPENAI_API_KEY"))

llm = initialize_chatopenai_llm()

def extract_json(text: str) -> str:
    """Extracts the valid JSON substring from a text containing extra data."""
    start = text.find('{')
    if start == -1:
        raise ValueError("No JSON object found in text.")
    brace_count = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            brace_count += 1
        elif text[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                return text[start:i+1]
    raise ValueError("Could not extract complete JSON object from text.")

def generate_quiz_with_langchain(topic: str, difficulty: str, num_questions: int) -> QuizResponse:
    # Use a few-shot template with fallback examples incorporated into the prompt
    few_shot_examples = """
Example 1 (Historical Events):
{
    "title": "Historical Events Quiz",
    "description": "A medium difficulty quiz about Historical Events",
    "questions": [
        {
            "id": 1,
            "question": "When did World War II end?",
            "options": ["1943", "1944", "1945", "1946"],
            "correct_answer": 2,
            "explanation": "World War II ended in 1945 with the surrender of Germany and Japan."
        },
        {
            "id": 2,
            "question": "Who was the first President of the United States?",
            "options": ["Thomas Jefferson", "John Adams", "George Washington", "Benjamin Franklin"],
            "correct_answer": 2,
            "explanation": "George Washington served as the first President from 1789 to 1797."
        }
    ]
}

Example 2 (Science and Technology):
{
    "title": "Science and Technology Quiz",
    "description": "A medium difficulty quiz about Science and Technology",
    "questions": [
        {
            "id": 1,
            "question": "What is the chemical symbol for gold?",
            "options": ["Ag", "Au", "Fe", "Cu"],
            "correct_answer": 1,
            "explanation": "Au is the chemical symbol for gold."
        },
        {
            "id": 2,
            "question": "Which planet is known as the Red Planet?",
            "options": ["Venus", "Mars", "Jupiter", "Saturn"],
            "correct_answer": 1,
            "explanation": "Mars is known as the Red Planet due to its reddish appearance."
        }
    ]
}
"""
    prompt = f"""
You are provided with the following few-shot examples for quiz generation:
{few_shot_examples}

Now, generate a {difficulty} difficulty quiz about {topic} with {num_questions} multiple choice questions.
Replace all placeholder texts with real content.
Do NOT include any text before or after the JSON.
Return ONLY the JSON object with this exact structure:
{{
    "title": "Quiz Title",
    "description": "Quiz description",
    "questions": [
        {{
            "id": 1,
            "question": "Replace this with an actual question about {topic}.",
            "options": ["Real Option 1", "Real Option 2", "Real Option 3", "Real Option 4"],
            "correct_answer": 0,
            "explanation": "Replace this with an explanation."
        }}
    ]
}}

Requirements:
- Each question must have exactly 4 options.
- correct_answer must be the index (0-3) of the correct option.
- Questions should be engaging and educational.
- Explanations must be clear and informative.
- Ensure the JSON is valid.
"""
    try:
        # ChatOpenAI expects a list of messages; send the prompt as a user message.
        result = llm.invoke([{"role": "user", "content": prompt}])
        raw_output = result.content
        print("Raw LLM output:", raw_output)  # Log the raw response
        if isinstance(raw_output, str):
            json_str = extract_json(raw_output)
            result_obj = json.loads(json_str)
        if "questions" in result_obj and "title" in result_obj:
            return QuizResponse(**result_obj)
        else:
            raise ValueError("Invalid quiz format in response")
    except Exception as e:
        print("LLM generation error:", e)
        raise HTTPException(status_code=500, detail=f"LLM generation error: {str(e)}")

# (Optional) Keep your fallback quiz generation function in case of errors
def generate_fallback_quiz(topic: str, difficulty: str, num_questions: int) -> QuizResponse:
    fallback_quizzes = {
        "Historical Events": [
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
        ],
        "Science and Technology": [
            {
                "id": 1,
                "question": "What is the chemical symbol for gold?",
                "options": ["Ag", "Au", "Fe", "Cu"],
                "correct_answer": 1,
                "explanation": "Au is the chemical symbol for gold."
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
        ],
        "World Geography": [
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
        ],
        "Literature and Authors": [
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
        ],
        "Art and Artists": [
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
        ],
        "Mathematics": [
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
        ],
        "Space and Astronomy": [
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
    
    if topic in fallback_quizzes:
        questions = fallback_quizzes[topic][:num_questions]
        title = f"{topic} Quiz"
        description = f"A {difficulty} difficulty quiz about {topic}"
    else:
        # Dynamically create a fallback quiz with generic questions related to the topic
        questions = [
            {
                "id": 1,
                "question": f"What is a key fact about {topic}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0,
                "explanation": f"Option A is a notable fact about {topic}."
            }
        ] * num_questions  # Repeat the generic question for demonstration
        title = f"{topic} Quiz"
        description = f"A {difficulty} difficulty quiz about {topic}"

    quiz_data = {
        "title": title,
        "description": description,
        "questions": questions
    }
    return QuizResponse(**quiz_data)

@app.get("/")
async def root():
    return {"message": "Quiz Generator API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "quiz-generator"}

@app.post("/api/generate-quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    """Generate a quiz using LangChain and a Hugging Face model"""
    try:
        quiz = generate_quiz_with_langchain(
            topic=request.topic,
            difficulty=request.difficulty,
            num_questions=request.num_questions
        )
        return quiz
    except Exception as e:
        # You can optionally fall back to a predefined quiz
        return generate_fallback_quiz(request.topic, request.difficulty, request.num_questions)

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
    print("API will be available at http://localhost:8000")
    
    uvicorn.run(
        "quiz-server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )