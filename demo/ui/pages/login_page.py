import mesop as me
from ..state.state import AppState
from ..service.server.user_service import create_user, verify_password, get_agent_settings

@me.stateclass
class LoginPageState:
    """State for the login page."""
    reg_username: str = ""
    reg_password: str = ""
    reg_agent_settings: str = ""
    registration_status: str = ""

    login_username: str = ""
    login_password: str = ""
    login_status: str = ""

def on_register_click(event: me.ClickEvent):
    """Handles the registration button click."""
    page_state = me.state(LoginPageState)
    app_state = me.state(AppState)

    if not page_state.reg_username or not page_state.reg_password:
        page_state.registration_status = "Username and password are required."
        return

    success = create_user(
        username=page_state.reg_username,
        password=page_state.reg_password,
        agent_settings=page_state.reg_agent_settings
    )
    if success:
        page_state.registration_status = f"User '{page_state.reg_username}' created successfully! You can now log in."
        # Clear registration fields after successful registration
        page_state.reg_username = ""
        page_state.reg_password = ""
        page_state.reg_agent_settings = ""
    else:
        page_state.registration_status = f"Failed to create user '{page_state.reg_username}'. Username might already exist."

def on_login_click(event: me.ClickEvent):
    """Handles the login button click."""
    page_state = me.state(LoginPageState)
    app_state = me.state(AppState)

    if not page_state.login_username or not page_state.login_password:
        page_state.login_status = "Username and password are required."
        return

    if verify_password(username=page_state.login_username, password=page_state.login_password):
        app_state.current_username = page_state.login_username
        agent_settings_str = get_agent_settings(page_state.login_username)
        app_state.agent_settings = agent_settings_str # Storing as string, can be parsed later if needed
        page_state.login_status = "Login successful!"
        # Clear login fields
        page_state.login_username = ""
        page_state.login_password = ""
        me.navigate("/")
    else:
        page_state.login_status = "Login failed. Please check your username and password."
        app_state.current_username = "" # Clear any previous username
        app_state.agent_settings = ""


@me.page(path="/login", title="Login/Register")
def login_page():
    app_state = me.state(AppState)
    page_state = me.state(LoginPageState)

    with me.box(style=me.Style(
        display="flex",
        flex_direction="column",
        align_items="center",
        gap="20px",
        padding=me.Padding.all(20)
    )):
        # Registration Section
        with me.box(style=me.Style(
            width="300px",
            padding=me.Padding.all(20),
            border=me.Border.all(me.BorderSide(width=1, style="solid", color="#ccc")),
            border_radius=me.BorderRadius.all(5)
        )):
            me.text("Register New User", type="headline-5", style=me.Style(text_align="center"))
            me.input(
                label="Username",
                value=page_state.reg_username,
                on_input=lambda e: setattr(page_state, 'reg_username', e.value),
                style=me.Style(margin=me.Margin(bottom=10))
            )
            me.input(
                label="Password",
                type="password",
                value=page_state.reg_password,
                on_input=lambda e: setattr(page_state, 'reg_password', e.value),
                style=me.Style(margin=me.Margin(bottom=10))
            )
            me.textarea(
                label="Agent Settings (Optional, JSON format e.g. {\"theme\": \"dark\"})",
                value=page_state.reg_agent_settings,
                on_input=lambda e: setattr(page_state, 'reg_agent_settings', e.value),
                style=me.Style(margin=me.Margin(bottom=10), height="80px")
            )
            me.button("Register", on_click=on_register_click, type="raised")
            if page_state.registration_status:
                me.text(page_state.registration_status, style=me.Style(
                    margin=me.Margin(top=10),
                    color="green" if "successfully" in page_state.registration_status.lower() else "red"
                ))

        # Login Section
        with me.box(style=me.Style(
            width="300px",
            padding=me.Padding.all(20),
            border=me.Border.all(me.BorderSide(width=1, style="solid", color="#ccc")),
            border_radius=me.BorderRadius.all(5),
            margin=me.Margin(top=20) # Add some space between the forms
        )):
            me.text("Login", type="headline-5", style=me.Style(text_align="center"))
            me.input(
                label="Username",
                value=page_state.login_username,
                on_input=lambda e: setattr(page_state, 'login_username', e.value),
                style=me.Style(margin=me.Margin(bottom=10))
            )
            me.input(
                label="Password",
                type="password",
                value=page_state.login_password,
                on_input=lambda e: setattr(page_state, 'login_password', e.value),
                style=me.Style(margin=me.Margin(bottom=10))
            )
            me.button("Login", on_click=on_login_click, type="raised")
            if page_state.login_status:
                me.text(page_state.login_status, style=me.Style(
                    margin=me.Margin(top=10),
                    color="green" if "successful" in page_state.login_status.lower() else "red"
                ))

        # Display current app state for debugging (optional)
        # me.text(f"Current AppState Username: {app_state.current_username}")
        # me.text(f"Current AppState Agent Settings: {app_state.agent_settings}")
