import pytest
import json
from unittest.mock import MagicMock, patch, AsyncMock
from src.brain import Brain

@pytest.fixture
def mock_brain_client():
    with patch('src.brain.genai.Client') as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        yield mock_client

def test_brain_initialization(mock_brain_client):
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
        brain = Brain()
        assert brain.client is not None
        assert brain.gemini_ready is True

@pytest.mark.asyncio
async def test_brain_process_command(mock_brain_client):
    # Mock local LLM to succeed and not hit network
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': json.dumps({
                "speech": "Hello!", "command": "ls", "thought": "user wants to list files"
            })}}]
        }
        mock_post.return_value = mock_response

        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            brain = Brain()
            # Force local mode via initialization
            result = await brain.process_command("hi")
            
            assert result['speech'] == "Hello!"
            assert result['command'] == "ls"
            assert "user wants to list files" in result['thought']

@pytest.mark.asyncio
async def test_brain_error_handling(mock_brain_client):
    # Mock local LLM to fail
    with patch('requests.post', side_effect=Exception("Local LLM failed")):
        # Mock Gemini success
        mock_gemini_response = MagicMock()
        mock_gemini_response.text = json.dumps({
            "speech": "Hello from Gemini!", 
            "command": "ls", 
            "thought": "Gemini fallback success"
        })
        mock_brain_client.models.generate_content.return_value = mock_gemini_response

        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            brain = Brain()
            result = await brain.process_command("hi")
            
            assert result['speech'] == "Hello from Gemini!"
            assert result['command'] == "ls"
