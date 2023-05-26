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

# Load environment variables from .env file
load_dotenv()

def sample_lines(filename, num_lines=5):
    with open(filename) as f:
        total_lines = sum(1 for _ in f)
    
    if total_lines < num_lines:
        raise ValueError("File has fewer lines than the number of lines requested.")
    
    line_numbers = random.sample(range(1, total_lines + 1), num_lines)
    lines = [linecache.getline(filename, line_number).rstrip() for line_number in line_numbers]
    
    return '\n'.join(lines)


def extract_code_snippets(text):
    pattern = r'```(.*?)```'
    snippets = re.findall(pattern, text, re.DOTALL)
    if len(snippets) == 0:
        snippets = [text]
    return snippets

def write_plot_script(filename, text):
    with open(filename, 'w') as file:
        file.write(text)

def attempt_to_fix_sctript(filename, error_message):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", max_tokens=2000, temperature=0)

    fix_plot_script_template = PromptTemplate(
        input_variables=["error", "script"],
        template="You are an AI agent that is designed to debug scripts created to plot mavlink data using matplotlib and pymavlink's mavutil. the following script produced this error: \n\n{script}\n\nThe error is: \n\n{error}\n\nPlease fix the script so that it produces the correct plot.",
    )

    # read script from file
    with open(filename, 'r') as file:
        script = file.read()
    
    chain = LLMChain(verbose=True, llm=llm, prompt=fix_plot_script_template)
    response = chain.run({"error": error_message, "script": script})
    print(response)
    code = extract_code_snippets(response)
    write_plot_script("plot.py", code[0])

    # run the script 
    os.system("python plot.py")


if __name__ == "__main__":


    file = "data/2023-01-04 20-51-25.tlog"
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", max_tokens=2000, temperature=0)
    
    mavlink_data_prompt = PromptTemplate(
        input_variables=["human_input", "file"],
        template="You are an AI conversation agent that will be used for generating python scripts to plot mavlink data provided by the user. Please create a python script using matplotlib and pymavlink's mavutil to plot the data provided by the user. Please do not explain the code just return the script. Please plot each independent variable over time.  \n\nHUMAN: {human_input} \n\nplease read this data from the file {file}.",
    )
    
    chain = LLMChain(verbose=True, llm=llm, prompt=mavlink_data_prompt)

    # prompt the user for the what plot they would like to generate
    human_input = input("Please enter a description of the plot you would like to generate: ")

    # human_input = "Please create a script to plot x y and z from LOCAL_POSITION_NED from the following data."
    response = chain.run({"file": file, "human_input": human_input})
    print(response)

    # parse the code from the response 
    code = extract_code_snippets(response)
    write_plot_script("plot.py", code[0])

    # run the script if it doesn't work capture output and call attempt_to_fix_script
    try:
        subprocess.check_output(["python", "plot.py"], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(e.output.decode())
        attempt_to_fix_sctript("plot.py", e.output.decode())
    except Exception as e:
        print(e)
        attempt_to_fix_sctript("plot.py", str(e))