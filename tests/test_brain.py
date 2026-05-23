import pytest
import json
from unittest.mock import MagicMock, patch
from src.brain import Brain

@pytest.fixture
def mock_brain_deps():
    # Patch the new genai.Client
    with patch('google.genai.Client') as mock_client:
        # Setup mock generate_content with AG-UI Protocol
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "version": "1.0",
            "status": "Online",
            "speech": "Hello!",
            "command": "ls",
            "thought": "Mocking response",
            "ui": {"type": "none"}
        })
        mock_client.return_value.models.generate_content.return_value = mock_response
        yield mock_client

@pytest.mark.asyncio
async def test_brain_initialization(mock_brain_deps):
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
        brain = Brain()
        assert brain.gemini_ready is True
        assert brain.client is not None

@pytest.mark.asyncio
async def test_brain_process_command(mock_brain_deps):
    # Mock local LLM failure to trigger Gemini fallback in test
    with patch('requests.post') as mock_post:
        # Mocking an HTML response (Ngrok offline)
        mock_post.return_value.headers = {"Content-Type": "text/html"}
        mock_post.return_value.status_code = 200
        
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            brain = Brain()
            # Process command triggers fallback to Gemini because local is "offline"
            result = await brain.process_command("hi")
            
            assert result['version'] == "1.0"
            assert result['status'] == "Online"
            assert result['speech'] == "Hello!"
            assert result['command'] == "ls"
            assert "Mocking response" in result['thought']

@pytest.mark.asyncio
async def test_brain_error_handling(mock_brain_deps):
    mock_brain_deps.return_value.models.generate_content.side_effect = Exception("API Error")
    
    with patch('requests.post') as mock_post:
        # Trigger fallback by having local brain return error
        mock_post.return_value.headers = {"Content-Type": "application/json"}
        mock_post.return_value.status_code = 500 
        
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            brain = Brain()
            result = await brain.process_command("hi")
            
            assert result['status'] == "Error"
            assert "cognitive snag" in result['speech']
            assert result['command'] is None
            assert "API Error" in result['thought']
