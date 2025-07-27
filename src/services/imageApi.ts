const API_BASE_URL = 'http://localhost:5001/api';

export interface ImageGenerationResponse {
  imageUrl: string;
}

export interface ImageGenerationRequest {
  prompt: string;
  provider?: 'openai' | 'placeholder';
}

export async function generateImage(request: ImageGenerationRequest): Promise<ImageGenerationResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/generate-image`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Image generation failed:', error);
    // Fallback to placeholder image
    return {
      imageUrl: `https://via.placeholder.com/512x512/667eea/ffffff?text=${encodeURIComponent(request.prompt)}`
    };
  }
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
} 