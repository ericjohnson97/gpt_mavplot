# GPT_MAVPlot

MAVPlot is a Python-based project which uses Gradio as an interface and GPT-X powered by OpenAI as a chatbot to generate and plot MAVLink data. It provides an easy-to-use, chatbot-like interface for users to describe the plot they would like to generate.

## Installation

1. Clone the repository:

```shell
git clone https://github.com/yourusername/mavplot.git
```

2. Install the requirements:

```shell
pip install -r requirements.txt
```

## Usage

After installing all dependencies, run the main script using:

```shell
python llm_plot.py
```

A web-based Gradio interface will launch. You can then input the description of the plot you would like to generate in the textbox, or upload a file.

The chatbot will process your request and generate the corresponding plot, which will be displayed in the chat interface.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
