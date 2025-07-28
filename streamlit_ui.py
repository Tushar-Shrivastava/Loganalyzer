import nest_asyncio
import streamlit as st
import asyncio
import json

nest_asyncio.apply()

if 'result' not in st.session_state:
    st.session_state.result = None

st.title('MCP Log Analyzer')
st.markdown("Upload a JSON log file to analyze errors and receive fixes.")


def display_results(result):
    """Display the agent results in a clear format"""
    st.subheader("🔍 Analysis Results")

    if not result:
        st.warning("⚠️ No results received")
        return

    if isinstance(result, dict) and "error" in result:
        st.error("❌ Error occurred:")
        st.code(result.get("details", result["error"]))
        return

    # Try to parse messages if they exist
    if isinstance(result, dict) and "messages" in result:
        st.subheader("💬 Conversation Messages")

        messages = result["messages"]

        for i, message in enumerate(messages):
            # Handle different message formats
            if hasattr(message, 'content'):
                # LangChain message object
                message_type = type(message).__name__
                content = message.content

                if 'Human' in message_type:
                    st.info(f"👤 **User:** {content}")
                elif 'AI' in message_type:
                    st.success(f"🤖 **AI:** {content}")
                elif 'Tool' in message_type:
                    tool_name = getattr(message, 'name', 'Unknown Tool')
                    st.warning(f"🛠️ **{tool_name}:** {content}")
                else:
                    st.write(f"📝 **{message_type}:** {content}")

            elif isinstance(message, dict):
                # Dictionary format
                st.json(message)
            else:
                # String or other format
                st.code(str(message))
    else:
        st.warning("⚠️ No conversation messages found in result")


uploaded_file = st.file_uploader('Upload a log file', type='json')

if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    st.success("✅ File uploaded successfully")

    # Show preview of logs
    try:
        logs = json.loads(content)
        st.info(f"📊 Found {len(logs)} log entries")

        with st.expander("👀 Preview logs"):
            st.json(logs[:2])  # Show first 2 entries
    except:
        st.error("❌ Invalid JSON format")

    if st.button("🧪 Analyze Log File"):
        with st.spinner("🔄 Running analysis..."):
            try:
                from streamlit_client import run_agent

                logs = json.loads(content)

                # Run the agent
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(run_agent(logs))
                loop.close()

                st.success("✅ Analysis complete!")

                # Store and display results
                st.session_state.result = result
                display_results(result)

            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                import traceback

                st.code(traceback.format_exc())