const express = require('express');
const cors = require('cors');
const OpenAI = require('openai');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Image generation endpoint
app.post('/api/generate-image', async (req, res) => {
  try {
    const { prompt, provider = 'openai' } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    let imageUrl;

    switch (provider) {
      case 'openai':
        imageUrl = await generateOpenAIImage(prompt);
        break;
      case 'placeholder':
        imageUrl = generatePlaceholderImage(prompt);
        break;
      default:
        return res.status(400).json({ error: 'Invalid provider' });
    }

    res.json({ imageUrl });
  } catch (error) {
    console.error('Image generation error:', error);
    res.status(500).json({ error: 'Failed to generate image' });
  }
});

// OpenAI DALL-E image generation
async function generateOpenAIImage(prompt) {
  try {
    const response = await openai.images.generate({
      model: "dall-e-3",
      prompt: prompt,
      n: 1,
      size: "1024x1024",
    });
    return response.data[0].url;
  } catch (error) {
    console.error('OpenAI error:', error);
    console.error('Error details:', error.message);
    throw new Error(`Failed to generate image with OpenAI: ${error.message}`);
  }
}



// Placeholder image generation
function generatePlaceholderImage(prompt) {
  const encodedPrompt = encodeURIComponent(prompt);
  return `https://via.placeholder.com/512x512/667eea/ffffff?text=${encodedPrompt}`;
}

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/api/health`);
  console.log(`Image generation: http://localhost:${PORT}/api/generate-image`);
}); 