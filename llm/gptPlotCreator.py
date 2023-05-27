import re
import random
import linecache
import subprocess
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
import os
from dotenv import load_dotenv
from PIL import Image



class PlotCreator:

    last_code = ""

    def __init__(self):
        load_dotenv()
        self.model = os.getenv("OPENAI_MODEL")
        # llm = ChatOpenAI(model_name="gpt-3.5-turbo", max_tokens=2000, temperature=0)
        llm = ChatOpenAI(model_name=self.model, max_tokens=2000, temperature=0)

        
        mavlink_data_prompt = PromptTemplate(
            input_variables=["history", "human_input", "file"],
            template="You are an AI conversation agent that will be used for generating python scripts to plot mavlink data provided by the user. Please create a python script using matplotlib and pymavlink's mavutil to plot the data provided by the user. Please do not explain the code just return the script. Please plot each independent variable over time in seconds. Please save the plot to file named plot.png in the same directory as plot.py with at least 400 dpi. Also be careful not to write a script that gets stuck in an endless loop.\n\nChat History:\n{history} \n\nHUMAN: {human_input} \n\nplease read this data from the file {file}.",
        )
        self.chain = LLMChain(verbose=True, llm=llm, prompt=mavlink_data_prompt)

    @staticmethod
    def sample_lines(filename, num_lines=5):
        with open(filename) as f:
            total_lines = sum(1 for _ in f)
        
        if total_lines < num_lines:
            raise ValueError("File has fewer lines than the number of lines requested.")
        
        line_numbers = random.sample(range(1, total_lines + 1), num_lines)
        lines = [linecache.getline(filename, line_number).rstrip() for line_number in line_numbers]
        
        return '\n'.join(lines)

    @staticmethod
    def extract_code_snippets(text):
        pattern = r'```.*?\n(.*?)```'
        snippets = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
        if len(snippets) == 0:
            snippets = [text]
        return snippets

    @staticmethod
    def write_plot_script(filename, text):
        with open(filename, 'w') as file:
            file.write(text)

    def attempt_to_fix_sctript(self, filename, error_message):
        # llm = ChatOpenAI(model_name="gpt-3.5-turbo", max_tokens=2000, temperature=0)
        llm = ChatOpenAI(model_name=self.model , max_tokens=2000, temperature=0)

        fix_plot_script_template = PromptTemplate(
            input_variables=["error", "script"],
            template="You are an AI agent that is designed to debug scripts created to plot mavlink data using matplotlib and pymavlink's mavutil. the following script produced this error: \n\n{script}\n\nThe error is: \n\n{error}\n\nPlease fix the script so that it produces the correct plot. please return the fixed script in a markdown code block.",
        )

        # read script from file
        with open(filename, 'r') as file:
            script = file.read()
        
        chain = LLMChain(verbose=True, llm=llm, prompt=fix_plot_script_template)
        response = chain.run({"error": error_message, "script": script})
        print(response)
        code = PlotCreator.extract_code_snippets(response)
        PlotCreator.write_plot_script("plot.py", code[0])

        # run the script 
        try:
            subprocess.check_output(["python", "plot.py"], stderr=subprocess.STDOUT)
        except:
            code[0] = "Sorry I was unable to fix the script.\nThis is my attempt to fix it:\n\n" + code[0]
        return code

    def set_logfile_name(self, filename):
        self.logfile_name = filename

    def create_plot(self, human_input, history):

        if self.last_code != "":
            history = history + "\n\nLast script generated:\n\n" + self.last_code


        response = self.chain.run({"history" : history, "file": self.logfile_name, "human_input": human_input})
        print(response)

        # parse the code from the response 
        code = self.extract_code_snippets(response)
        self.write_plot_script("plot.py", code[0])

        # run the script if it doesn't work capture output and call attempt_to_fix_script
        try:
            subprocess.check_output(["python", "plot.py"], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print(e.output.decode())
            code = self.attempt_to_fix_sctript("plot.py", e.output.decode())
        except Exception as e:
            print(e)
            code = self.attempt_to_fix_sctript("plot.py", str(e))

        self.last_code = code[0]

        return [("plot.png", None), code[0]]
