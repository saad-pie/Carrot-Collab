import os
import asyncio
from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from playwright.async_api import async_playwright
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import requests

class BrowserAutomationAgent:
    def __init__(self):
        self.llm_providers = {}
        self.playwright_browser = None
        self.selenium_driver = None
        self.setup_llm_providers()
        
    def setup_llm_providers(self):
        """Initialize different LLM providers"""
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.llm_providers["openai"] = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.7
            )
        
        # Anthropic
        if os.getenv("ANTHROPIC_API_KEY"):
            self.llm_providers["anthropic"] = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.7
            )
        
        # Google Gemini
        if os.getenv("GOOGLE_API_KEY"):
            self.llm_providers["google"] = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                temperature=0.7
            )
    
    async def init_browser(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
    
    def init_selenium(self):
        """Initialize Selenium WebDriver"""
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.selenium_driver = webdriver.Chrome(options=chrome_options)
    
    async def generate_topic_subtopics(self, main_topic: str, provider: str = "openai") -> List[str]:
        """Generate subtopics for a main topic using specified LLM provider"""
        if provider not in self.llm_providers:
            raise ValueError(f"Provider {provider} not available")
        
        llm = self.llm_providers[provider]
        
        prompt = f"""
        Given the main topic: "{main_topic}"
        
        Generate 5-7 engaging subtopics that would make good video segments for a 10-minute YouTube video.
        Each subtopic should be:
        - Specific and focused
        - Engaging for viewers
        - Suitable for 1-2 minute video segments
        - Related to the main topic
        
        Return only a JSON array of subtopic strings, like:
        ["Subtopic 1", "Subtopic 2", "Subtopic 3", "Subtopic 4", "Subtopic 5"]
        """
        
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        
        try:
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\[.*\]', response.content)
            if json_match:
                subtopics = json.loads(json_match.group())
            else:
                # Fallback: split by lines and clean up
                subtopics = [line.strip().strip('"').strip("'") for line in response.content.split('\n') 
                           if line.strip() and not line.startswith('[') and not line.startswith(']')]
                subtopics = [s for s in subtopics if s]
        except:
            # Final fallback
            subtopics = [f"{main_topic} - Part {i+1}" for i in range(5)]
        
        return subtopics[:7]  # Limit to 7 subtopics
    
    async def generate_script_for_subtopic(self, subtopic: str, provider: str = "openai") -> str:
        """Generate a video script for a subtopic"""
        if provider not in self.llm_providers:
            raise ValueError(f"Provider {provider} not available")
        
        llm = self.llm_providers[provider]
        
        prompt = f"""
        Create a short, engaging video script for the subtopic: "{subtopic}"
        
        Requirements:
        - 30-60 seconds of narration (about 50-100 words)
        - Engaging and conversational tone
        - Include a hook at the beginning
        - End with a call to action or transition
        - Suitable for a YouTube video segment
        
        Write only the script text, no formatting or instructions.
        """
        
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        return response.content.strip()
    
    async def research_topic(self, topic: str) -> Dict[str, Any]:
        """Research a topic using web search and return relevant information"""
        if not self.page:
            await self.init_browser()
        
        # Search for the topic
        search_query = f"{topic} latest information 2024"
        await self.page.goto(f"https://www.google.com/search?q={search_query}")
        
        # Extract search results
        results = await self.page.query_selector_all("h3")
        search_results = []
        for result in results[:5]:
            text = await result.text_content()
            if text:
                search_results.append(text.strip())
        
        # Visit first result and extract content
        first_link = await self.page.query_selector("a[href]")
        if first_link:
            href = await first_link.get_attribute("href")
            if href and href.startswith("http"):
                await self.page.goto(href)
                content = await self.page.text_content("body")
                return {
                    "search_results": search_results,
                    "main_content": content[:1000],  # First 1000 chars
                    "source_url": href
                }
        
        return {
            "search_results": search_results,
            "main_content": "",
            "source_url": ""
        }
    
    async def get_ai_summary(self, content: str, provider: str = "openai") -> str:
        """Get AI summary of researched content"""
        if provider not in self.llm_providers:
            raise ValueError(f"Provider {provider} not available")
        
        llm = self.llm_providers[provider]
        
        prompt = f"""
        Summarize the following content in 2-3 sentences for a video script:
        
        {content}
        
        Make it engaging and suitable for video narration.
        """
        
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        return response.content.strip()
    
    async def close(self):
        """Clean up resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        if self.selenium_driver:
            self.selenium_driver.quit()

# Global agent instance
browser_agent = None

async def get_browser_agent():
    """Get or create browser agent instance"""
    global browser_agent
    if browser_agent is None:
        browser_agent = BrowserAutomationAgent()
        await browser_agent.init_browser()
    return browser_agent