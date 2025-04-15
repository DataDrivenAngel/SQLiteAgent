import sqlite3
import replicate
import sys
import os
from rich.console import Console
from rich.table import Table

replicate_api_token = os.getenv('REPLICATE_API_TOKEN')
console = Console()


def drop_db():

    if os.path.exists('agent_tasks.db'):
        os.remove('agent_tasks.db')
        print("Database dropped successfully.")

# Initialize the database
def init_db():
    conn = sqlite3.connect('agent_tasks.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks';")
    if cursor.fetchone() is None:
        with open(os.path.join('sql', 'setup_table_tasks.sql'), 'r') as file:
            cursor.executescript(file.read())
        conn.commit()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tools';")
    if cursor.fetchone() is None:
        with open(os.path.join('sql', 'setup_table_tools.sql'), 'r') as file:
            cursor.executescript(file.read())
        conn.commit()

        with open(os.path.join('data', 'tools.sql'), 'r') as file:
            cursor.executescript(file.read())
        conn.commit()
    conn.close()



 

def register_chat():

    conn = sqlite3.connect('agent_tasks.db')
    conn.create_function("chat", 1, chat_function)
    
    return conn


def get_tools():
    conn = sqlite3.connect('agent_tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, description FROM tools")
    tools = cursor.fetchall()

    tool_text = ''
    for tool in tools:
        
        tool_text = tool_text + f"Name: {tool[0]}"
        tool_text = tool_text + f"Description: {tool[1]}\n"

    return tool_text



def chat_function(prompt):
    """Custom function to use replicate for text generation"""

    sys_prompt = f"""

         You are a helpful agent embodied in a sql database. 

        """
    
        # Pick a single tool from the list of tools to best handle the prompt:
        # {get_tools()}

        # Respond only with a single tool name
        
        # """
    


    try:
        response = ""
        for event in replicate.stream(
            "meta/meta-llama-3-8b-instruct",
            input={
                "top_k": 0,
                "top_p": 0.95,  
                "prompt": prompt,
                "max_tokens": 512,
                "temperature": 0.7,
                "system_prompt": sys_prompt,
                "length_penalty": 1,
                "max_new_tokens": 512,
                "stop_sequences": "<|end_of_text|>,<|eot_id|>",
                "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
                "presence_penalty": 0,
                "log_performance_metrics": False,
                "API": replicate_api_token
            },
        ):
            chunk = str(event)
            response += chunk
            print(chunk, end="", flush=True)  # Optional: print in real-time with flush
        
        return response
    except Exception as e:
        return f"Error: {str(e)}"
    
def chat_function(prompt):
    """Custom function to use replicate for text generation"""




    sys_prompt = f"""

        You are a helpful agent embodied in a sql database. 

        Evaluate the following prompt
        
        Pick a single tool from the list of tools to best handle the prompt:
        {get_tools()}

        Respond only with a single tool name"""
    


    try:
        response = ""
        for event in replicate.stream(
            "meta/meta-llama-3-8b-instruct",
            input={
                "top_k": 0,
                "top_p": 0.95,  
                "prompt": prompt,
                "max_tokens": 512,
                "temperature": 0.7,
                "system_prompt": sys_prompt,
                "length_penalty": 1,
                "max_new_tokens": 512,
                "stop_sequences": "<|end_of_text|>,<|eot_id|>",
                "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
                "presence_penalty": 0,
                "log_performance_metrics": False,
                "API": replicate_api_token
            },
        ):
            chunk = str(event)
            response += chunk
            print(chunk, end="", flush=True)  # Optional: print in real-time with flush
        
        return response
    except Exception as e:
        return f"Error: {str(e)}"



def init_triggers():
    conn = register_chat()
    cursor = conn.cursor()
    with open(os.path.join('sql', 'setup_triggers.sql'), 'r') as file:
        cursor.executescript(file.read())
    conn.commit()
    conn.close()

# Add a new task
def add_task(goal):
    conn = register_chat()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (goal, is_active, iteration_limit, iterations) VALUES (?, ?, ?, ?)', (goal, 1, 10 , 0))
    conn.commit()


    # Get the response for the task we just added
    task_id = cursor.lastrowid
    cursor.execute('SELECT response FROM tasks WHERE goal = ?', (goal,))
    result = cursor.fetchone()
    conn.close()
    return result



    
def main():
    # Check for -re flag
    if len(sys.argv) > 1 and sys.argv[1] == '-re':
        drop_db()
        


    init_db()
    register_chat()
    init_triggers()

    
    while True:
        # Create a flashing prompt using Rich
        console.print("[bold cyan]>>>[/bold cyan] ", end="")
        command = input("Enter Prompt: ").strip().lower()


        if command == 'exit':
            print("Exiting the application.")
            sys.exit()

        elif command == 'list':
            print("List of tools / protocols:")
            conn = register_chat()
            cursor = conn.cursor()
            cursor.execute("SELECT name, description FROM tools")
            tools = cursor.fetchall()
            for tool in tools:
                print(f"Name: {tool[0]}")
                print(f"Description: {tool[1]}")

        elif command == 'query':
            print("Query the database:")
            conn = register_chat()
            cursor = conn.cursor()
            query = input("Query: ")
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Get column names from cursor description
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                
                # Create a Rich table
                table = Table(title="Query Results", show_header=True, header_style="bold magenta")
                
                # Add columns to the table
                for column in columns:
                    table.add_column(column, style="cyan")
                
                # Add rows to the table
                for row in results:
                    table.add_row(*[str(value) for value in row])
                
                # Print the table
                console.print(table)
                console.print(f"[bold green]Total rows: {len(results)}[/bold green]")
            else:
                print("Query executed successfully (no results returned)")
                
            conn.close()


        else:
            add_task(command)
            print("\n")

if __name__ == "__main__":

    main()


