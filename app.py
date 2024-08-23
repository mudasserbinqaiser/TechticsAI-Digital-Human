import gradio as gr
import requests
import base64

# Function to handle chat responses and video generation
def handle_chat(user_input, chat_history):
    api_url = "http://localhost:8000/process_input/"  # Replace with your actual FastAPI URL
    try:
        response = requests.post(api_url, json={"input_text": user_input})
        response_data = response.json()

        if response.status_code != 200:
            raise Exception(response_data.get("error", "An unknown error occurred"))

        assistant_response = response_data.get("assistant_text")
        video_file_path = response_data.get("video_bytes")

        # Append the new messages to the chat history
        chat_history.append((user_input, assistant_response))

        # Return the updated chat history and the video path
        return chat_history, video_file_path

    except Exception as e:
        # Handle any exceptions and display an error message in the chat window
        chat_history.append((user_input, f"Error: {str(e)}"))
        return chat_history, None

# Gradio UI layout
def chatbot_ui():
    with gr.Blocks() as demo:
        # Video container at the top
        with gr.Row():
            video = gr.Video(autoplay=True, format="mp4", height = 250, width = 250, container = False, show_download_button= False, show_share_button=False)

        # Chat window in the middle
        with gr.Row():
            chat_window = gr.Chatbot(label="Chat History")

        # Text input box with send icon at the bottom
        with gr.Row():
            with gr.Column(scale=12):
                user_input = gr.Textbox(show_label=False, placeholder="Type your message...")
            with gr.Column(scale=1):
                send_button = gr.Button(value="Send", variant="primary", scale= 1)

        # Define interactions
        send_button.click(handle_chat, inputs=[user_input, chat_window], outputs=[chat_window, video])

    return demo

# Launch the Gradio UI
chatbot_ui().launch()
    