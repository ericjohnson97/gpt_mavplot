import gradio as gr
import os
from llm.gptPlotCreator import PlotCreator

plot_creator = PlotCreator()

def add_text(history, text):
    history = history + [(text, None)]
    return history, ""

def add_file(history, file):
    history = history + [((file.name,), None)]
    return history

def format_history(history):
    return "\n".join([f"Human: {entry[0]}\nAI: {entry[1]}" for entry in history ])

def bot(history):
    # Get the last input from the user
    user_input = history[-1][0] if history and history[-1][0] else None

    print(user_input)

    # Check if it is a string
    if isinstance(user_input, str):
        # Generate the plot

        print(history)

        history_str = format_history(history)
        response = plot_creator.create_plot(user_input, history_str)
        print(response)
        history[-1][1] = response[0]
        history = history + [(None, f"Here is the code used to generate the plot:")]
        history = history + [(None, f"{response[1]}")]
    else:
        file_path = user_input[0]
        plot_creator.set_logfile_name(file_path)
        
        # get only base name
        filename, extension = os.path.splitext(os.path.basename(file_path))
        
        history[-1][0] = f"user uploaded file: {filename}{extension}"
        history[-1][1] = "I will be using the file you uploaded to generate the plot. Please describe the plot you would like to generate."
    
    return history


with gr.Blocks() as demo:
    gr.Markdown("# GPT MAVPlot\n\nThis web-based tool allows users to upload mavlink tlogs in which the chat bot will use to generate plots from. It does this by creating a python script using pymavlink and matplotlib. The output includes the plot and the code used to generate it. ")
    chatbot = gr.Chatbot([], elem_id="chatbot").style(height=750)
    
    with gr.Row():
        with gr.Column(scale=0.85):
            txt = gr.Textbox(
                show_label=False,
                placeholder="Enter text and press enter, or upload an image",
            ).style(container=False)
        with gr.Column(scale=0.15, min_width=0):
            btn = gr.UploadButton("📁", file_types=["image", "video", "audio"])
            
    txt.submit(add_text, [chatbot, txt], [chatbot, txt]).then(
        bot, chatbot, chatbot
    )
    btn.upload(add_file, [chatbot, btn], [chatbot]).then(
        bot, chatbot, chatbot
    )

if __name__ == "__main__":
    demo.launch()
