# AI Quiz Application

A modern quiz application that integrates with your local Qwen model to generate custom quizzes. Built with React, TypeScript, and FastAPI.

## Features

- **Built-in Quiz**: Pre-made historical events quiz
- **AI-Generated Quizzes**: Create custom quizzes using your local Qwen model
- **Multiple Topics**: Choose from various subjects like Science, History, Geography, etc.
- **Difficulty Levels**: Easy, Medium, and Hard difficulty options
- **Real-time Scoring**: Track your progress and score
- **Detailed Results**: Review your answers with explanations
- **Timer**: Track how long you take to complete quizzes

## Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Your Qwen Server

Make sure your Qwen server is running on `http://localhost:8080`. Based on your [Qwen repository](https://github.com/artemis283/quem), you can start it with:

```bash
# Navigate to your Qwen directory
cd /path/to/your/quem

# Start the Qwen server
python server.py
```

### 3. Start the Quiz API Server

```bash
python quiz-server.py
```

The API will be available at `http://localhost:8000`

### 4. Start the Frontend

```bash
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000` (or the next available port)

## How to Use

1. **Take the Built-in Quiz**: Start with the pre-made historical events quiz
2. **Generate Custom Quizzes**: Click "Generate Custom Quiz" to create AI-generated quizzes
3. **Choose Your Topic**: Select from various subjects like Science, History, Geography, etc.
4. **Set Difficulty**: Choose Easy, Medium, or Hard difficulty
5. **Answer Questions**: Click on your chosen answer
6. **Review Results**: See your score and detailed explanations

## API Endpoints

- `GET /` - API status
- `GET /health` - Health check
- `POST /api/generate-quiz` - Generate a new quiz
- `GET /api/topics` - Get available topics
- `GET /api/difficulties` - Get difficulty levels

## Quiz Generation

The application sends prompts to your local Qwen model to generate structured quiz questions. The prompt includes:

- Topic selection
- Difficulty level
- Number of questions
- Structured JSON format requirements

## File Structure

```
├── quiz-server.py          # FastAPI server for quiz generation
├── requirements.txt        # Python dependencies
├── quiz-data.json         # Built-in quiz data
├── src/
│   ├── App.tsx           # Main React component
│   ├── components/
│   │   ├── Quiz.tsx      # Quiz question component
│   │   └── QuizGenerator.tsx # AI quiz generator
│   ├── types.ts          # TypeScript interfaces
│   └── App.css           # Styling
└── QUIZ_README.md        # This file
```

## Customization

### Adding New Topics

Edit `quiz-server.py` and add new topics to the `topics` list in the `get_topics()` function.

### Modifying Quiz Format

Update the prompt in `generate_quiz_with_qwen()` function to change the quiz structure or add new fields.

### Styling

Modify `src/App.css` to customize the appearance of the quiz application.

## Troubleshooting

### Qwen Server Not Running
- Make sure your Qwen server is running on `http://localhost:8080`
- Check that the API endpoint `/generate` is available

### Quiz Generation Fails
- Check the console for error messages
- Verify that your Qwen model can generate structured JSON
- Try simpler topics or fewer questions

### Frontend Can't Connect
- Ensure the quiz server is running on port 8000
- Check CORS settings if needed
- Verify network connectivity

## Integration with Your Qwen Setup

This application is designed to work with your existing Qwen setup from [https://github.com/artemis283/quem](https://github.com/artemis283/quem). It expects:

1. A Qwen server running on `http://localhost:8080`
2. An endpoint that accepts POST requests with a `prompt` field
3. Returns JSON responses

If your Qwen setup uses different endpoints or formats, modify the `QWEN_API_URL` and request format in `quiz-server.py`. 