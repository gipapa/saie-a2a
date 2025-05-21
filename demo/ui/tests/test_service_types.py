import unittest
from typing import Any

from demo.ui.service.types import RegisterAgentRequest

class TestServiceTypes(unittest.TestCase):

    def test_register_agent_request_with_string_params(self):
        """Test RegisterAgentRequest with string params."""
        params_str = "http://localhost:1234/agent-card"
        request = RegisterAgentRequest(params=params_str)
        self.assertEqual(request.method, "agent/register")
        self.assertEqual(request.params, params_str)

    def test_register_agent_request_with_dict_params(self):
        """Test RegisterAgentRequest with dictionary params."""
        params_dict: dict[str, Any] = {
            "name": "MyManualAgent",
            "address": "manual_agent_id_123", # Or an actual address if applicable
            "description": "A manually configured agent.",
            "input_modes": ["text", "voice"],
            "output_modes": ["text"],
            "stream_supported": True,
            "push_notifications_supported": False,
            "framework_type": "CustomFramework",
            "manual_input": True,
            "test_connection": False
        }
        request = RegisterAgentRequest(params=params_dict)
        self.assertEqual(request.method, "agent/register")
        self.assertEqual(request.params, params_dict)

    def test_register_agent_request_with_none_params(self):
        """Test RegisterAgentRequest with None params."""
        request = RegisterAgentRequest(params=None)
        self.assertEqual(request.method, "agent/register")
        self.assertIsNone(request.params)

if __name__ == '__main__':
    unittest.main()
