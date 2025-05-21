import asyncio

import mesop as me
import mesop.labs as mel

from components.agent_list import agents_list
from components.dialog import dialog, dialog_actions
from components.header import header
from components.page_scaffold import page_frame, page_scaffold
from state.agent_state import AgentState # Assume AgentState will be updated with new fields
from state.host_agent_service import AddRemoteAgent, ListRemoteAgents
from state.state import AppState
from utils.agent_card import get_agent_card


def agent_list_page(app_state: AppState):
    """Agents List Page"""
    state = me.state(AgentState)
    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():
            with header('Remote Agents', 'smart_toy'):
                pass
            agents = asyncio.run(ListRemoteAgents())
            agents_list(agents)
            with dialog(state.agent_dialog_open):
                with me.box(
                    style=me.Style(
                        display='flex', flex_direction='column', gap=12
                    )
                ):
                    mel.checkbox(
                        "Test Connection Before Saving",
                        on_change=set_test_connection,
                        checked=state.test_connection,
                    )
                    mel.checkbox(
                        "Manual Input",
                        on_change=set_manual_input,
                        checked=state.manual_input,
                    )
                    me.input(
                        label='Agent Name (if no address)' if state.manual_input else 'Agent Address',
                        on_blur=set_agent_address,
                        placeholder='localhost:10000',
                    )
                    
                    if state.error != '':
                        me.text(state.error, style=me.Style(color='red'))

                    if state.manual_input:
                        # Editable fields for manual input
                        me.input(label='Agent Description', value=state.agent_description, on_blur=set_agent_description)
                        me.input(label='Agent Framework Type', value=state.agent_framework_type, on_blur=set_agent_framework_type)
                        me.input(label='Input Modes (comma-separated)', value=', '.join(state.input_modes), on_blur=set_input_modes)
                        me.input(label='Output Modes (comma-separated)', value=', '.join(state.output_modes), on_blur=set_output_modes)
                        mel.checkbox("Streaming Supported", on_change=set_stream_supported, checked=state.stream_supported)
                        mel.checkbox("Push Notifications Supported", on_change=set_push_notifications_supported, checked=state.push_notifications_supported)
                    else:
                        # Display fields for non-manual input (after reading from agent)
                        if state.agent_name != '':
                            me.text(f'Agent Name: {state.agent_name}')
                        if state.agent_description:
                            me.text(f'Agent Description: {state.agent_description}')
                        if state.agent_framework_type:
                            me.text(
                                f'Agent Framework Type: {state.agent_framework_type}'
                            )
                        if state.input_modes:
                            me.text(f'Input Modes: {", ".join(state.input_modes)}')
                        if state.output_modes:
                            me.text(f'Output Modes: {", ".join(state.output_modes)}')
                        if state.agent_name: # Show these only if agent details were successfully read
                            me.text(
                                f'Streaming Supported: {state.stream_supported}'
                            )
                            me.text(
                                f'Push Notifications Supported: {state.push_notifications_supported}'
                            )

                with dialog_actions():
                    if not state.manual_input and not state.agent_name:
                        me.button('Read', on_click=load_agent_info)
                    
                    # Save button should be available if manual input is true, or if agent details are loaded without error
                    if state.manual_input or (state.agent_name and not state.error):
                        me.button('Save', on_click=save_agent)
                    me.button('Cancel', on_click=cancel_agent_dialog)


def set_agent_address(e: me.InputBlurEvent):
    state = me.state(AgentState)
    state.agent_address = e.value

# Placeholder event handlers for new inputs
def set_test_connection(e: me.CheckboxChangeEvent):
    state = me.state(AgentState)
    state.test_connection = e.checked

def set_manual_input(e: me.CheckboxChangeEvent):
    state = me.state(AgentState)
    state.manual_input = e.checked

def set_agent_description(e: me.InputBlurEvent):
    state = me.state(AgentState)
    state.agent_description = e.value

def set_agent_framework_type(e: me.InputBlurEvent):
    state = me.state(AgentState)
    state.agent_framework_type = e.value

def set_input_modes(e: me.InputBlurEvent):
    state = me.state(AgentState)
    state.input_modes = [mode.strip() for mode in e.value.split(',')]

def set_output_modes(e: me.InputBlurEvent):
    state = me.state(AgentState)
    state.output_modes = [mode.strip() for mode in e.value.split(',')]

def set_stream_supported(e: me.CheckboxChangeEvent):
    state = me.state(AgentState)
    state.stream_supported = e.checked

def set_push_notifications_supported(e: me.CheckboxChangeEvent):
    state = me.state(AgentState)
    state.push_notifications_supported = e.checked

def load_agent_info(e: me.ClickEvent):
    state = me.state(AgentState)
    try:
        state.error = None
        agent_card_response = get_agent_card(state.agent_address)
        state.agent_name = agent_card_response.name
        state.agent_description = agent_card_response.description
        state.agent_framework_type = (
            agent_card_response.provider.organization
            if agent_card_response.provider
            else ''
        )
        state.input_modes = agent_card_response.defaultInputModes
        state.output_modes = agent_card_response.defaultOutputModes
        state.stream_supported = agent_card_response.capabilities.streaming
        state.push_notifications_supported = (
            agent_card_response.capabilities.pushNotifications
        )
    except Exception as e:
        print(e)
        state.agent_name = None
        state.error = f'Cannot connect to agent as {state.agent_address}'


def cancel_agent_dialog(e: me.ClickEvent):
    state = me.state(AgentState)
    state.agent_dialog_open = False
    # Reset all relevant fields to their defaults, similar to after saving
    state.agent_address = ''
    state.agent_name = ''
    state.agent_description = ''
    state.agent_framework_type = ''
    state.input_modes = []
    state.output_modes = []
    state.stream_supported = False
    state.push_notifications_supported = False
    state.error = ''
    state.manual_input = False # Default
    state.test_connection = True # Default


async def save_agent(e: me.ClickEvent):
    state = me.state(AgentState)
    agent_details = {}

    if state.manual_input:
        # In manual mode, state.agent_address holds the "Agent Name"
        agent_details = {
            "name": state.agent_address.strip(), # Primary identifier from the input field
            "address": state.agent_address.strip(), # Assuming name can also serve as address/unique ID
            "description": state.agent_description,
            "input_modes": state.input_modes,
            "output_modes": state.output_modes,
            "stream_supported": state.stream_supported,
            "push_notifications_supported": state.push_notifications_supported,
            "framework_type": state.agent_framework_type,
            "manual_input": True,
            "test_connection": state.test_connection # Pass this flag for the backend to potentially use
        }
        # If test_connection is false for manual input, it implies the user doesn't want the backend
        # to attempt to connect to an "address" if one were hypothetically derived or needed.
        # For a purely manual entry, "address" might be more of a unique ID.
        # If state.test_connection is False, we are explicitly saying "do not test".
        # If state.test_connection is True, backend MIGHT test if it makes sense for a manual entry.
        if not state.test_connection:
            # If not testing, ensure the address field is explicitly set,
            # as it might be used as a unique ID by the backend.
            # If it was meant to be optional if no actual network address, this needs backend agreement.
            pass # address is already set from state.agent_address

    else: # Not manual_input (auto-discovery mode)
        if state.agent_address and not state.error: # Ensure we have an address and no error from reading
            agent_details = {
                "address": state.agent_address.strip(),
                "name": state.agent_name,
                "description": state.agent_description,
                "input_modes": state.input_modes,
                "output_modes": state.output_modes,
                "stream_supported": state.stream_supported,
                "push_notifications_supported": state.push_notifications_supported,
                "framework_type": state.agent_framework_type,
                "manual_input": False,
                "test_connection": state.test_connection
            }
        elif state.agent_address and not state.test_connection: # Allow saving untested address
             agent_details = {
                "address": state.agent_address.strip(),
                "name": "", # No name if not read
                "description": "",
                "input_modes": [],
                "output_modes": [],
                "stream_supported": False,
                "push_notifications_supported": False,
                "framework_type": "",
                "manual_input": False,
                "test_connection": False # Explicitly false
            }
        else:
            # This case should ideally not be reached if "Save" button is correctly disabled.
            # If it is, do not proceed with saving.
            print("Save button was enabled incorrectly, or state is inconsistent.")
            return

    if agent_details: # Ensure there's something to save
        try:
            await AddRemoteAgent(details=agent_details)
        except Exception as ex:
            print(f"Error saving agent: {ex}")
            state.error = f"Failed to save agent: {ex}"
            # Do not close dialog or reset if save failed
            return 
    
    # Reset state after successful saving
    state.agent_address = ''
    state.agent_name = ''
    state.agent_description = ''
    state.input_modes = []
    state.output_modes = []
    state.stream_supported = False # Reset to default
    state.push_notifications_supported = False # Reset to default
    state.manual_input = False # Reset to default
    state.test_connection = True # Reset to default
    state.error = None
    state.agent_dialog_open = False
