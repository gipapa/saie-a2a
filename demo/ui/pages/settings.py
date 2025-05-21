import asyncio
import json # Added import for json

import mesop as me

from components.header import header
from components.page_scaffold import page_frame, page_scaffold
from state.host_agent_service import UpdateApiKey
from state.state import AppState, SettingsState
from ..service.server.user_service import update_agent_settings # Added import for user_service


def on_selection_change_output_types(e: me.SelectSelectionChangeEvent):
    s = me.state(SettingsState)
    s.output_mime_types = e.values


def on_api_key_change(e: me.InputBlurEvent):
    s = me.state(AppState)
    s.api_key = e.value


@me.stateclass
class UpdateStatus:
    """Status for API key update"""

    show_success: bool = False

@me.stateclass
class AgentSettingsUpdateStatus:
    """Status for agent settings update."""
    message: str = ""
    is_error: bool = False
    # To hold the text area content before saving
    current_settings_text: str = "" 


async def update_api_key(e: me.ClickEvent):
    yield  # Allow UI to update

    state = me.state(AppState)
    update_status = me.state(UpdateStatus)

    if state.api_key.strip():
        success = await UpdateApiKey(state.api_key)
        if success:
            update_status.show_success = True

            # Hide success message after 3 seconds
            yield
            await asyncio.sleep(3)
            update_status.show_success = False

    yield  # Allow UI to update after operation completes

def on_agent_settings_input(e: me.InputEvent | me.InputBlurEvent):
    """Handles input changes in the agent settings textarea."""
    agent_settings_status = me.state(AgentSettingsUpdateStatus)
    agent_settings_status.current_settings_text = e.value

async def on_save_agent_settings_click(e: me.ClickEvent):
    """Handles the save agent settings button click."""
    yield # Allow UI to update (e.g. button click visual feedback)
    app_state = me.state(AppState)
    agent_settings_status = me.state(AgentSettingsUpdateStatus)

    if not app_state.current_username:
        agent_settings_status.message = "Error: No user logged in."
        agent_settings_status.is_error = True
        yield
        return

    new_settings_str = agent_settings_status.current_settings_text
    try:
        # Validate and reformat JSON
        parsed_settings = json.loads(new_settings_str)
        # Re-serialize to ensure consistent formatting (e.g. spacing)
        formatted_settings_str = json.dumps(parsed_settings, indent=2) 
    except json.JSONDecodeError:
        agent_settings_status.message = "Error: Invalid JSON format."
        agent_settings_status.is_error = True
        yield
        return

    success = update_agent_settings(app_state.current_username, formatted_settings_str)

    if success:
        app_state.agent_settings = formatted_settings_str # Update app_state with the new settings
        agent_settings_status.message = "Agent settings updated successfully!"
        agent_settings_status.is_error = False
    else:
        agent_settings_status.message = "Error: Failed to update agent settings on the server."
        agent_settings_status.is_error = True
    
    yield # Update UI with status

    # Optionally, hide message after some time
    await asyncio.sleep(5)
    agent_settings_status.message = ""
    yield


def settings_page_content():
    """Settings Page Content."""
    settings_state = me.state(SettingsState)
    app_state = me.state(AppState)
    update_status = me.state(UpdateStatus)
    agent_settings_status = me.state(AgentSettingsUpdateStatus)

    # Initialize current_settings_text from app_state if it's empty or not yet set by user input
    # This ensures the textarea is populated on first load or if user navigates away and back
    if not agent_settings_status.current_settings_text and app_state.agent_settings:
        try:
            # Try to pretty-print if it's valid JSON
            parsed = json.loads(app_state.agent_settings)
            agent_settings_status.current_settings_text = json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            agent_settings_status.current_settings_text = app_state.agent_settings


    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():
            with header('Settings', 'settings'):
                pass
            with me.box(
                style=me.Style(
                    display='flex',
                    justify_content='space-between',
                    flex_direction='column',
                    gap=30,
                )
            ):
                # API Key Settings Section
                if not app_state.uses_vertex_ai:
                    with me.box(
                        style=me.Style(
                            display='flex',
                            flex_direction='column',
                            margin=me.Margin(bottom=30),
                        )
                    ):
                        me.text(
                            'Google API Key',
                            type='headline-6',
                            style=me.Style(
                                margin=me.Margin(bottom=15),
                                font_family='Google Sans',
                            ),
                        )

                        with me.box(
                            style=me.Style(
                                display='flex',
                                flex_direction='row',
                                gap=10,
                                align_items='center',
                                margin=me.Margin(bottom=5),
                            )
                        ):
                            me.input(
                                label='API Key',
                                value=app_state.api_key,
                                on_blur=on_api_key_change,
                                type='password',
                                appearance='outline',
                                style=me.Style(width='400px'),
                            )

                            me.button(
                                'Update',
                                type='raised',
                                on_click=update_api_key,
                                style=me.Style(
                                    color=me.theme_var('primary'),
                                ),
                            )

                        # Success message
                        if update_status.show_success:
                            with me.box(
                                style=me.Style(
                                    background=me.theme_var(
                                        'success-container'
                                    ),
                                    padding=me.Padding(
                                        top=10, bottom=10, left=10, right=10
                                    ),
                                    border_radius=4,
                                    margin=me.Margin(top=10),
                                    display='flex',
                                    flex_direction='row',
                                    align_items='center',
                                    width='400px',
                                )
                            ):
                                me.icon(
                                    'check_circle',
                                    style=me.Style(
                                        color=me.theme_var(
                                            'on-success-container'
                                        ),
                                        margin=me.Margin(right=10),
                                    ),
                                )
                                me.text(
                                    'API Key updated successfully',
                                    style=me.Style(
                                        color=me.theme_var(
                                            'on-success-container'
                                        ),
                                    ),
                                )

                    # Add spacing instead of divider with style
                    with me.box(
                        style=me.Style(margin=me.Margin(top=10, bottom=10))
                    ):
                        me.divider()
                
                # Agent Settings Section
                with me.box(
                    style=me.Style(
                        display='flex',
                        flex_direction='column',
                        margin=me.Margin(top=20, bottom=30), # Added top margin
                    )
                ):
                    me.text(
                        'Agent Settings',
                        type='headline-6',
                        style=me.Style(
                            margin=me.Margin(bottom=15),
                            font_family='Google Sans',
                        ),
                    )
                    me.textarea(
                        label='Agent Settings (JSON format)',
                        value=agent_settings_status.current_settings_text, # Bind to temporary state
                        on_input=on_agent_settings_input,
                        on_blur=on_agent_settings_input, # Update on blur as well
                        style=me.Style(width='100%', height='200px', margin=me.Margin(bottom=10)),
                        textarea_style=me.Style(font_family='monospace') # Monospace for JSON
                    )
                    me.button(
                        'Save Agent Settings',
                        type='raised',
                        on_click=on_save_agent_settings_click,
                        style=me.Style(
                            color=me.theme_var('primary'),
                        ),
                    )
                    if agent_settings_status.message:
                        me.text(
                            agent_settings_status.message,
                            style=me.Style(
                                color="red" if agent_settings_status.is_error else "green",
                                margin=me.Margin(top=10)
                            )
                        )

                # Divider before Output Types Section
                with me.box(
                    style=me.Style(margin=me.Margin(top=10, bottom=10))
                ):
                    me.divider()

                # Output Types Section
                me.select(
                    label='Supported Output Types',
                    options=[
                        me.SelectOption(label='Image', value='image/*'),
                        me.SelectOption(
                            label='Text (Plain)', value='text/plain'
                        ),
                    ],
                    on_selection_change=on_selection_change_output_types,
                    style=me.Style(width=500),
                    multiple=True,
                    appearance='outline',
                    value=settings_state.output_mime_types,
                )
