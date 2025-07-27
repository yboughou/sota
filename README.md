# Historical Events Matching Game

An educational matching game where students match historical terms with their visual representations.

## 🎮 Features

- **Interactive Card Game**: Flip cards to match historical terms with images
- **Real-time Image Generation**: AI-powered images for each historical event
- **Timer & Score Tracking**: Monitor game progress and performance
- **Responsive Design**: Works on desktop and mobile devices
- **Multiple Image Providers**: OpenAI DALL-E or placeholder images

## 🚀 Quick Start

### Frontend (React + Vite)

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Open in browser**: http://localhost:3001

### Backend (Image Generation API)

1. **Navigate to server directory**:
   ```bash
   cd server
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your API key:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   PORT=5000
   ```

4. **Start the API server**:
   ```bash
   npm run dev
   ```

## 🔧 Image Generation Setup

### Option 1: OpenAI DALL-E (Recommended)
1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Add to `.env`: `OPENAI_API_KEY=your_key_here`
3. In `src/components/Card.tsx`, change `provider: 'placeholder'` to `provider: 'openai'`

### Option 2: Placeholder Images (No Setup Required)
- Uses placeholder.com for simple text-based images
- No API keys needed
- Good for testing and development

## 🎯 How to Play

1. Click any card to start the game
2. Try to match historical terms with their corresponding images
3. Complete all 5 pairs to win
4. Track your moves and time
5. Click "New Game" to play again

## 📁 Project Structure

```
├── src/
│   ├── components/
│   │   └── Card.tsx          # Individual card component
│   ├── services/
│   │   └── imageApi.ts       # Image generation API calls
│   ├── types.ts              # TypeScript type definitions
│   ├── utils.ts              # Game utility functions
│   ├── App.tsx               # Main game component
│   ├── main.tsx              # React entry point
│   └── index.css             # Styling
├── server/
│   ├── server.js             # Express API server
│   ├── package.json          # Backend dependencies
│   └── env.example          # Environment variables template
├── historical_events_matching_game.json  # Game data
└── package.json              # Frontend dependencies
```

## 🛠️ Customization

### Adding New Topics
1. Create a new JSON file with the same structure as `historical_events_matching_game.json`
2. Update the import in `src/App.tsx` to use your new data file

### Changing Image Providers
Edit `src/components/Card.tsx` and change the `provider` parameter:
- `'openai'` - AI-generated images (requires API key)
- `'placeholder'` - Simple text images (no setup required)

## 🔍 API Endpoints

- `GET /api/health` - Health check
- `POST /api/generate-image` - Generate images
  - Body: `{ "prompt": "description", "provider": "openai" }`
  - Response: `{ "imageUrl": "https://..." }`

## 🎨 Styling

The game uses modern CSS with:
- Gradient backgrounds
- Smooth animations
- Responsive grid layout
- Card flip effects
- Hover animations

## 🚀 Deployment

### Frontend
```bash
npm run build
# Deploy the dist/ folder to your hosting service
```

### Backend
```bash
cd server
npm start
# Deploy to your preferred hosting service (Heroku, Vercel, etc.)
```

## 📝 License

MIT License - feel free to use and modify for educational purposes!