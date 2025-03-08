# Random Article Generator for WordPress

This script automatically generates and publishes random articles to WordPress using AI. It creates both the title and content in a single API call, producing engaging articles on diverse and surprising topics.

## Features

- Generates unique article topics and content using AI
- Automatically formats content with proper HTML structure for WordPress
- Supports both publishing and draft modes
- Handles tags automatically
- Properly formats headings, lists, bold text, and italics
- Includes error handling and JSON response validation

## Prerequisites

- Python 3.x
- WordPress site with REST API enabled
- API key from OpenAI or OpenRouter
- WordPress application password

## Installation

1. Clone the repository
2. Install required dependencies:
```bash
pip install openai python-dotenv requests
```

## Configuration

Create a `.env` file in the same directory as the script with the following variables:

```env
# WordPress Configuration
WP_USERNAME=your_wordpress_username
WP_PASSWORD=your_wordpress_application_password
WP_API_URL=https://your-site.com/wp-json/wp/v2/posts
WORDPRESS_ENV=production  # or development

# AI Provider Configuration
AI_PROVIDER=openai  # or openrouter
API_KEY=your_api_key
AI_MODEL=gpt-3.5-turbo  # or other supported model
MAX_TOKENS=800
TEMPERATURE=0.7

# Optional OpenRouter Configuration (if using OpenRouter)
API_BASE_URL=https://openrouter.ai/api/v1  # optional, defaults based on AI_PROVIDER
YOUR_SITE_URL=https://your-site.com  # required for OpenRouter
YOUR_SITE_NAME=Your Site Name  # required for OpenRouter
```

### Important Notes About .env Variables:

- `WP_USERNAME`: Your WordPress username
- `WP_PASSWORD`: Application password from WordPress (not your login password)
- `WP_API_URL`: Your WordPress REST API endpoint for posts
- `API_KEY`: Your OpenAI API key or OpenRouter API key
- `AI_MODEL`: The AI model to use (e.g., gpt-3.5-turbo)
- `TEMPERATURE`: Controls randomness of the output (0.0 to 1.0)
- `MAX_TOKENS`: Maximum length of generated content

## Usage

### Basic Usage
```bash
python random_article.py
```

### Create Draft Instead of Publishing
```bash
python random_article.py --draft
```

## How It Works

1. **Topic Generation**: The script uses a list of example topics as inspiration but generates entirely new topics for each article.

2. **Content Generation**: Using AI, it creates:
   - A unique topic
   - A catchy title (limited to 10 words)
   - Comprehensive article content with proper formatting

3. **Content Formatting**: The script automatically formats the content with:
   - Proper HTML structure
   - WordPress-compatible headings (H2, H3)
   - Bulleted lists
   - Bold and italic text
   - Proper paragraph spacing

4. **Publishing**: The formatted article is published to WordPress via the REST API with:
   - Automatic tag handling
   - Support for draft/publish modes
   - Error handling and validation

## Error Handling

The script includes comprehensive error handling for:
- Missing environment variables
- API communication issues
- JSON parsing errors
- WordPress publishing failures

## Customization

You can customize the article generation by modifying:
- `EXAMPLE_TOPICS` list in the script for different topic inspiration
- `ARTICLE_TAGS` list for default article tags
- Environment variables for AI parameters (temperature, max tokens, etc.) 
