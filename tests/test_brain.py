import pytest
from unittest.mock import MagicMock, patch
from src.brain import Brain

@pytest.fixture
def mock_brain_deps():
    with patch('google.generativeai.GenerativeModel') as mock_model:
        with patch('google.generativeai.configure'):
            # Setup mock chat
            mock_chat = MagicMock()
            mock_model.return_value.start_chat.return_value = mock_chat
            yield mock_model, mock_chat

def test_brain_initialization(mock_brain_deps):
    mock_model, mock_chat = mock_brain_deps
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
        brain = Brain()
        assert brain.model is not None
        mock_model.return_value.start_chat.assert_called_once()
        mock_chat.send_message.assert_called_once() # System prompt

@pytest.mark.asyncio
async def test_brain_process_command(mock_brain_deps):
    mock_model, mock_chat = mock_brain_deps
    # Mock the API response for the user message
    mock_response = MagicMock()
    mock_response.text = '{"speech": "Hello!", "command": "ls", "thought": "user wants to list files"}'
    # The first call is system prompt, second is the actual message
    mock_chat.send_message.side_effect = [MagicMock(), mock_response]

    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
        brain = Brain()
        result = await brain.process_command("hi")
        
        assert result['speech'] == "Hello!"
        assert result['command'] == "ls"
        assert "user wants to list files" in result['thought']

@pytest.mark.asyncio
async def test_brain_error_handling(mock_brain_deps):
    mock_model, mock_chat = mock_brain_deps
    # System prompt succeeds, user message fails
    mock_chat.send_message.side_effect = [MagicMock(), Exception("API Error")]

    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
        brain = Brain()
        result = await brain.process_command("hi")
        
        assert "cognitive snag" in result['speech']
        assert result['command'] is None
        assert "API Error" in result['thought']
