import unittest

from demo.ui.state.agent_state import AgentState

class TestAgentState(unittest.TestCase):

    def test_initial_defaults(self):
        """Test that AgentState initializes with correct default values."""
        state = AgentState()
        self.assertTrue(state.test_connection, "test_connection should default to True")
        self.assertFalse(state.manual_input, "manual_input should default to False")
        self.assertEqual(state.input_modes, [], "input_modes should default to an empty list")
        self.assertEqual(state.output_modes, [], "output_modes should default to an empty list")
        
        # Also check other relevant defaults for completeness, though not explicitly new
        self.assertEqual(state.agent_dialog_open, False)
        self.assertEqual(state.agent_address, "")
        self.assertEqual(state.agent_name, "")
        self.assertEqual(state.agent_description, "")
        self.assertEqual(state.stream_supported, False)
        self.assertEqual(state.push_notifications_supported, False)
        self.assertEqual(state.error, "")
        self.assertEqual(state.agent_framework_type, "")

if __name__ == '__main__':
    unittest.main()
