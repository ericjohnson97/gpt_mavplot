import gradio as gr
from llm.gptPlotCreator import PlotCreator

plot_creator = PlotCreator()

def add_text(history, text):
    history = history + [(text, None)]
    return history, ""

def add_file(history, file):
    history = history + [((file.name,), None)]
    return history

def bot(history):
    # Get the last input from the user
    user_input = history[-1][0]
    
    # Check if it is a string
    if isinstance(user_input, str):
        # Generate the plot
        img = plot_creator.create_plot(user_input)
        response = img
    else:
        response = "**That's cool!**"

    history[-1][1] = ('plot.png', None)
    return history

with gr.Blocks() as demo:
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
