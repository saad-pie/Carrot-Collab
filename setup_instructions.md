# Browser Automation Video Generator Setup

## Prerequisites

1. **Python 3.8+**
2. **Chrome/Chromium browser** (for Playwright and Selenium)
3. **API Keys** for LLM providers (optional but recommended)

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browsers
```bash
playwright install chromium
```

### 3. Install ChromeDriver for Selenium
```bash
# On Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# On macOS with Homebrew
brew install chromedriver

# On Windows, download from https://chromedriver.chromium.org/
```

## Environment Variables

Create a `.env` file in your project directory:

```env
# OpenAI (for GPT-4o-mini)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic (for Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google (for Gemini)
GOOGLE_API_KEY=your_google_api_key_here
```

## Configuration

### LLM Provider Priority
The system will use providers in this order:
1. OpenAI (GPT-4o-mini) - if API key is set
2. Anthropic (Claude) - if API key is set  
3. Google (Gemini) - if API key is set
4. Fallback to simple text generation

### Browser Automation
- **Playwright**: Primary browser automation (faster, more reliable)
- **Selenium**: Backup browser automation
- **Headless Mode**: Set `headless=True` in `browser_agent.py` for production

## Usage

### 1. Start the Flask App
```bash
python app.py
```

### 2. Open Browser
Go to: `http://127.0.0.1:5000/`

### 3. Generate Video
1. Enter a topic
2. The system will:
   - Use browser agent to generate subtopics
   - Generate scripts for each subtopic
   - Create images using SDXL
   - Generate videos from images
   - Add TTS narration
   - Combine into final video

## Features

### Browser Agent Capabilities
- **Multi-LLM Support**: GPT-4o, Claude, Gemini
- **Web Research**: Automatically research topics
- **Smart Prompting**: Generate engaging video content
- **Fallback System**: Works even without API keys

### Video Generation Pipeline
1. **Topic Analysis** → Browser agent researches and splits topic
2. **Script Generation** → AI creates engaging narration
3. **Visual Creation** → SDXL generates relevant images
4. **Video Assembly** → Combine images into video segments
5. **Audio Narration** → TTS adds professional voiceover
6. **Final Assembly** → Concatenate all segments

## Troubleshooting

### Common Issues

1. **"No module named 'playwright'"**
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **ChromeDriver not found**
   - Install ChromeDriver for your OS
   - Ensure it's in your PATH

3. **API Key Errors**
   - Check your `.env` file
   - Verify API keys are valid
   - System will fallback to simple generation

4. **Browser Automation Fails**
   - Check if Chrome/Chromium is installed
   - Try running with `headless=False` for debugging

### Performance Tips

1. **For CPU-only systems:**
   - Reduce `num_inference_steps` in SDXL (default: 20)
   - Use fewer subtopics (3-5 instead of 7)
   - Consider using smaller models

2. **For faster generation:**
   - Use API keys for all providers
   - Run browser in headless mode
   - Use SSD storage for temp files

## Advanced Configuration

### Custom LLM Models
Edit `browser_agent.py` to change models:
```python
# For different OpenAI models
self.llm_providers["openai"] = ChatOpenAI(
    model="gpt-4o",  # or "gpt-4o-mini"
    temperature=0.7
)

# For different Claude models
self.llm_providers["anthropic"] = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",  # or "claude-3-haiku-20240307"
    temperature=0.7
)
```

### Browser Settings
```python
# In browser_agent.py
self.browser = await self.playwright.chromium.launch(
    headless=False,  # Set to True for production
    args=['--no-sandbox', '--disable-dev-shm-usage']
)
```