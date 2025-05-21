## Demo Web App

This demo application showcases agents talking to other agents over A2A.

![image](./a2a_demo_arch.png)

- The frontend is a [mesop](https://github.com/mesop-dev/mesop) web application that renders conversations as content between the end user and the "Host Agent". This app can render text content, thought bubbles, web forms (requests for input from agents), and images. More content types coming soon

- The [Host Agent](/samples/python/hosts/multiagent/host_agent.py) is a Google ADK agent which orchestrates user requests to Remote Agents.

- Each [Remote Agent](/samples/python/hosts/multiagent/remote_agent_connection.py) is an A2AClient running inside a Google ADK agent. Each remote agent will retrieve the A2AServer's [AgentCard](https://google.github.io/A2A/#documentation?id=agent-card) and then proxy all requests using A2A.

## Features

<need quick gif>

### Dynamically add agents

Clicking on the robot icon in the web app lets you add new agents. Enter the address of the remote agent's AgentCard and the app will fetch the card and add the remote agent to the local set of known agents.

### Speak with one or more agents

Click on the chat button to start or continue an existing conversation. This conversation will go to the Host Agent which will then delegate the request to one or more remote agents.

If the agent returns complex content - like an image or a web-form - the frontend will render this in the conversation view. The Remote Agent will take care of converting this content between A2A and the web apps native application representation.

### Explore A2A Tasks

Click on the history to see the messages sent between the web app and all of the agents (Host agent and Remote agents).

Click on the task list to see all the A2A task updates from the remote agents

## Prerequisites

- Python 3.13 or higher
- UV
- Agent servers speaking A2A ([use these samples](/samples/python/agents/README.md))
- Authentication credentials (API Key or Vertex AI)

## Running the Examples

1. Navigate to the demo ui directory:
   ```bash
   cd demo/ui
   ```
2. Create an environment file with your API key or enter it directly in the UI when prompted:

   **Option A: Google AI Studio API Key**

   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" >> .env
   ```

   Or enter it directly in the UI when prompted.

   **Option B: Google Cloud Vertex AI**

   ```bash
   echo "GOOGLE_GENAI_USE_VERTEXAI=TRUE" >> .env
   echo "GOOGLE_CLOUD_PROJECT=your_project_id" >> .env
   echo "GOOGLE_CLOUD_LOCATION=your_location" >> .env
   ```

   Note: Ensure you've authenticated with gcloud using `gcloud auth login` first.

   For detailed instructions on authentication setup, see the [ADK documentation](https://google.github.io/adk-docs/get-started/quickstart/#set-up-the-model).

3. **Initialize the user database**:
   ```bash
   # Ensure you are in the demo/ui directory
   uv run service/server/database_setup.py
   ```
   This will create a `users.db` file in the `demo/ui/service/server/` directory to store user accounts and settings.

4. **Run the front end example**:

   ```bash
   uv run main.py
   ```

   The application runs on port 12000 by default. Open your browser to `http://localhost:12000`. You will be greeted with a login/registration page.

5. **Interact with the demo**:

   When you first access the application at `http://localhost:12000`, you'll need to create a user account.
   - Use the **Registration Form** to set up your username and password. You can leave the "Agent Settings" field blank during initial registration if you wish.
   - After successful registration, **log in** using your new credentials.

   Once logged in, you can navigate to the **Settings** page from the side navigation. Here, you can manage your personal agent-related preferences (these are stored as a JSON string in your user profile). Note that global API keys for services like Google AI Studio or Vertex AI are still configured via the `.env` file (as described in Step 2).

   After logging in, you can start interacting with the Host Agent on the main page.
   You can ask the Host Agent _"What remote agents do you have access to?"_ It should initially report none.

   Next, to add a remote agent, go start up **any** sample agent. For example, to run the Google ADK sample agent:
   ```bash
   # From the project root
   cd samples/python/agents/google_adk/
   # Copy the .env file if your agent needs API keys
   cp ../../../../demo/ui/.env ./
   uv run .
   ```

   Back in the demo UI (ensure you are logged in), navigate to the **Agents** tab. Add the address of the sample agent you just started, for example:
   ```
   localhost:10002
   ```
   (The port may vary depending on the sample agent you run.)

   Now, when you converse with the Host Agent, it should have access to the newly added remote agent (e.g., the _Reimbursement Agent_ if you ran the Google ADK sample).
   You can try asking it to _"reimburse lunch for 20 EUR but needs to be converted to USD ahead of time."_

   Answer its questions. If you need help converting currency, try adding the LangGraph sample agent too (following a similar process to start it and add its AgentCard address).

   Review the events and task list to see the A2A communication details.