import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio
from typing import Any

# Correct the import path based on actual structure if needed
from demo.ui.state.host_agent_service import AddRemoteAgent
from demo.ui.service.types import RegisterAgentRequest

class TestHostAgentService(unittest.TestCase):

    @patch('demo.ui.state.host_agent_service.ConversationClient')
    def test_add_remote_agent_with_dict_details(self, MockConversationClient: MagicMock):
        """
        Test AddRemoteAgent when 'details' is a dictionary (manual input or detailed auto-discovery).
        """
        mock_client_instance = MockConversationClient.return_value
        mock_client_instance.register_agent = AsyncMock()

        details_dict: dict[str, Any] = {
            "name": "TestAgent",
            "address": "test_agent_address_or_id",
            "description": "A test agent.",
            "manual_input": True,
            # ... other fields as expected by RegisterAgentRequest params dict
        }

        async def run_test():
            await AddRemoteAgent(details=details_dict)

        asyncio.run(run_test())

        # Verify that register_agent was called once
        mock_client_instance.register_agent.assert_called_once()
        
        # Get the actual call arguments
        args, kwargs = mock_client_instance.register_agent.call_args
        
        # Check that the first argument is an instance of RegisterAgentRequest
        self.assertIsInstance(args[0], RegisterAgentRequest, "Should be called with RegisterAgentRequest instance")
        
        # Check the params of the RegisterAgentRequest instance
        sent_request: RegisterAgentRequest = args[0]
        self.assertEqual(sent_request.method, "agent/register")
        self.assertEqual(sent_request.params, details_dict, "Params in request should match the details dictionary")

    @patch('demo.ui.state.host_agent_service.ConversationClient')
    def test_add_remote_agent_with_string_details(self, MockConversationClient: MagicMock):
        """
        Test AddRemoteAgent when 'details' is a string (simple URL for auto-discovery).
        """
        mock_client_instance = MockConversationClient.return_value
        mock_client_instance.register_agent = AsyncMock()

        details_str = "http://localhost:8000/agent-card"

        async def run_test():
            await AddRemoteAgent(details=details_str)

        asyncio.run(run_test())
        
        mock_client_instance.register_agent.assert_called_once()
        args, kwargs = mock_client_instance.register_agent.call_args
        self.assertIsInstance(args[0], RegisterAgentRequest)
        sent_request: RegisterAgentRequest = args[0]
        self.assertEqual(sent_request.method, "agent/register")
        self.assertEqual(sent_request.params, details_str, "Params in request should match the details string")

    @patch('demo.ui.state.host_agent_service.ConversationClient')
    def test_add_remote_agent_exception_handling(self, MockConversationClient: MagicMock):
        """
        Test that AddRemoteAgent re-raises exceptions from client.register_agent.
        """
        mock_client_instance = MockConversationClient.return_value
        mock_client_instance.register_agent = AsyncMock(side_effect=RuntimeError("Registration failed"))

        details_str = "http://localhost:8000/agent-card"

        async def run_test():
            with self.assertRaises(RuntimeError) as context:
                await AddRemoteAgent(details=details_str)
            self.assertEqual(str(context.exception), "Registration failed")

        asyncio.run(run_test())
        mock_client_instance.register_agent.assert_called_once()


if __name__ == '__main__':
    unittest.main()
