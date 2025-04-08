from typing import Dict, Any, Optional, Union
from openai import OpenAI
import logging
import json
import os
import requests
from enum import Enum
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMProvider(Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"

class LLMAgent:
    """Base class for LLM interactions that can be used by different analytics services"""
    
    def __init__(self, 
                 provider: LLMProvider = LLMProvider.ANTHROPIC,
                 openai_api_key: Optional[str] = None,
                 anthropic_api_key: Optional[str] = None,
                 ollama_url: str = "http://localhost:11434",
                 ollama_model: str = "llama2"):
        self.provider = provider
        self.ollama_url = ollama_url
        self.ollama_model = ollama_model
        
        if provider == LLMProvider.OPENAI:
            self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
            if not self.openai_api_key:
                logging.warning("No OpenAI API key provided in environment or constructor. LLM functionality will be disabled.")
                self.enabled = False
            else:
                self.client = OpenAI(api_key=self.openai_api_key)
                self.enabled = True
        elif provider == LLMProvider.ANTHROPIC:
            self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
            if not self.anthropic_api_key:
                logging.warning("No Anthropic API key provided in environment or constructor. LLM functionality will be disabled.")
                self.enabled = False
            else:
                self.client = Anthropic(api_key=self.anthropic_api_key)
                self.enabled = True
        else:  # OLLAMA
            self.enabled = True
            try:
                # Test Ollama connection
                response = requests.get(f"{ollama_url}/api/tags")
                if response.status_code == 200:
                    logging.info("Successfully connected to Ollama")
                else:
                    logging.warning("Could not connect to Ollama")
                    self.enabled = False
            except Exception as e:
                logging.warning(f"Could not connect to Ollama: {str(e)}")
                self.enabled = False

    def generate_response(self, 
                         prompt: str, 
                         model: str = "claude-3-haiku-20240307",
                         temperature: float = 0.4,
                         max_tokens: int = 1500) -> Dict[str, Any]:
        """
        Generate a response from the LLM
        """
        if not self.enabled:
            return {"error": "LLM functionality is disabled"}

        try:
            if self.provider == LLMProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return {
                    "content": response.choices[0].message.content.strip(),
                    "success": True
                }
            elif self.provider == LLMProvider.ANTHROPIC:
                response = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                return {
                    "content": response.content[0].text.strip(),
                    "success": True
                }
            else:  # OLLAMA
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                return {
                    "content": result["response"].strip(),
                    "success": True
                }
        except Exception as e:
            logging.error(f"Error generating LLM response: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }

    def parse_json_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a JSON response from the LLM
        """
        if not response.get("success"):
            return response

        try:
            return {
                "data": json.loads(response["content"]),
                "success": True
            }
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse JSON response",
                "raw_text": response["content"],
                "success": False
            }
            