import pytest
import json
from unittest.mock import MagicMock, patch
from src.brain import Brain

@pytest.fixture
def mock_brain_deps():
    # Patch the new genai.Client
    with patch('google.genai.Client') as mock_client:
        # Setup mock generate_content
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "speech": "Hello!",
            "command": "ls",
            "thought": "Mocking response"
        })
        mock_client.return_value.models.generate_content.return_value = mock_response
        yield mock_client

@pytest.mark.asyncio
async def test_brain_initialization(mock_brain_deps):
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
        brain = Brain()
        # In new Brain, we don't start chat on init, we just configure client
        assert brain.gemini_ready is True
        assert brain.client is not None

@pytest.mark.asyncio
async def test_brain_process_command(mock_brain_deps):
    # Mock local LLM failure to trigger Gemini fallback in test
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 400 # Trigger fallback
        
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            brain = Brain()
            # Process command triggers fallback to Gemini
            result = await brain.process_command("hi")
            
            assert result['speech'] == "Hello!"
            assert result['command'] == "ls"
            assert "Mocking response" in result['thought']

@pytest.mark.asyncio
async def test_brain_error_handling(mock_brain_deps):
    mock_client = mock_brain_deps
    mock_client.return_value.models.generate_content.side_effect = Exception("API Error")
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 400 # Trigger fallback
        
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            brain = Brain()
            result = await brain.process_command("hi")
            
            assert "connection issue" in result['speech']
            assert result['command'] is None
            assert "Server Error 400" in result['thought']
