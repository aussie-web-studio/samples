import streamlit as st
import os
from dotenv import load_dotenv
from agentcore_client import AgentCoreClient, AgentCoreRuntime
from typing import Optional

# Load environment variables
load_dotenv()

def init_client(region: str) -> Optional[AgentCoreClient]:
    """Initialize AgentCore client with selected region"""
    try:
        return AgentCoreClient(region=region)
    except Exception as e:
        st.error(f"Failed to initialize client: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="AgentCore Chatbot", page_icon="🤖", layout="wide")
    
    st.title("🤖 AgentCore Runtime Chatbot")
    st.markdown("Connect to your AgentCore runtimes and start chatting!")

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'selected_runtime' not in st.session_state:
        st.session_state.selected_runtime = None

    # Check if connected (define early for UI state)
    is_connected = (
        'selected_runtime' in st.session_state and 
        st.session_state.selected_runtime is not None and 
        hasattr(st.session_state.selected_runtime, 'status') and
        st.session_state.selected_runtime.status == "ACTIVE"
    )
    
    # Sidebar for runtime selection
    with st.sidebar:
        st.header("🔧 Runtime Selection")
        
        # Region selection
        selected_region = st.selectbox(
            "Select Region:",
            ["us-west-2", "us-east-1", "ap-southeast-2"],
            index=0,
            disabled=is_connected
        )
        
        # Initialize client with selected region
        client = init_client(selected_region)
        if not client:
            st.error("❌ Failed to initialize AgentCore client.")
            st.stop()
        
        # Load runtimes button
        if st.button("🔄 Load Runtimes", disabled=is_connected):
            with st.spinner("Loading runtimes..."):
                try:
                    st.session_state.runtimes = client.list_runtimes()
                    if not st.session_state.runtimes:
                        st.warning("No runtimes found in this region")
                except Exception as e:
                    st.error(f"❌ Error loading runtimes: {str(e)}")
                    st.session_state.runtimes = []
        
        # Runtime selection dropdown
        if 'runtimes' in st.session_state and st.session_state.runtimes:
            runtime_options = {f"{r.name} ({r.status})": r for r in st.session_state.runtimes}
            selected_name = st.selectbox("Select Runtime:", list(runtime_options.keys()), disabled=is_connected)
            
            if selected_name:
                selected_runtime = runtime_options[selected_name]
                st.info(f"**ARN:** {selected_runtime.arn}")
                
                # Connect button
                if st.button("🔗 Connect", disabled=is_connected):
                    with st.spinner("Connecting to runtime..."):
                        try:
                            runtime, session_id = client.connect_to_runtime(selected_runtime.arn)
                            st.session_state.selected_runtime = runtime
                            st.session_state.session_id = session_id
                            if runtime.status == "ACTIVE":
                                st.rerun()  # Refresh to update button states
                        except Exception as e:
                            st.error(f"❌ Connection failed: {str(e)}")
        else:
            st.info("👆 Click 'Load Runtimes' to discover available runtimes")

        # Display connection status
        if 'selected_runtime' in st.session_state and st.session_state.selected_runtime:
            runtime = st.session_state.selected_runtime
            
            if runtime.status == "ACTIVE":
                st.success("✅ Runtime is ready")
                if 'session_id' in st.session_state and st.session_state.session_id:
                    st.info(f"🆔 Session ID: {st.session_state.session_id}")
                
                # Disconnect button
                if st.button("❌ Disconnect"):
                    st.session_state.selected_runtime = None
                    if 'session_id' in st.session_state:
                        del st.session_state.session_id
                    st.rerun()  # Refresh to update button states
            elif runtime.status == "ERROR":
                st.error("❌ Runtime error (500) - Check CloudWatch logs")
            elif runtime.status == "NOT_FOUND":
                st.error("❌ Runtime not found")
            else:
                st.error("❌ Runtime is not active")
        else:
            st.info("👆 Load runtimes and click Connect")

    # Main chat interface
    if st.session_state.selected_runtime and st.session_state.selected_runtime.status.lower() == 'active':
        st.subheader(f"💬 Chat with {st.session_state.selected_runtime.name}")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Type your message here..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get bot response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = client.send_message(st.session_state.selected_runtime.arn, prompt)
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    else:
        st.info("👈 Please select an active runtime from the sidebar to start chatting.")

    # Footer
    st.markdown("---")
    st.markdown("Built with Streamlit and AgentCore Runtime")

if __name__ == "__main__":
    main()