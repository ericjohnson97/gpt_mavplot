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
        
        history[-1][1] = "I am figuring out what data types are relevant for the plot...\n"
        yield history
        data_types_str = plot_creator.find_relevant_data_types(user_input)

        history[-1][1] += "I am now generating a script to plot the data...\n"
        yield history
        plot_creator.create_plot(user_input, data_types_str)
        
        history[-1][1] += "I am now running the script I just Generated...\n"
        yield history
        response = plot_creator.run_script()
        
        history = history + [(None, f"Here is the code used to generate the plot:")]
        history = history + [(None, f"{response[1]}")]
        history = history + response[0]
        
        
        yield history
    else:
        file_path = user_input[0]
        plot_creator.set_logfile_name(file_path)
        
        # get only base name
        filename, extension = os.path.splitext(os.path.basename(file_path))
        
        history[-1][0] = f"user uploaded file: {filename}{extension}"
        history[-1][1] = "processing file..."
        yield history

        data_types = plot_creator.parse_mavlink_log()
        history = history + [(None, f"I am done processing the file. Now you can ask me to generate a plot.")]
        yield history

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
            btn = gr.UploadButton("📁", file_types=["file"])
            
    txt.submit(add_text, [chatbot, txt], [chatbot, txt]).then(
        bot, chatbot, chatbot
    )
    btn.upload(add_file, [chatbot, btn], [chatbot]).then(
        bot, chatbot, chatbot
    )

if __name__ == "__main__":
    demo.queue()
    demo.launch()
