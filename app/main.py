import sqlite3
import replicate
import sys
import os

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

def chat_function(prompt):
    """Custom function to use replicate for text generation"""
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
                "system_prompt": """You are a helpful agent embodied in a sql database. Please evaluate the following prompt""",
                "length_penalty": 1,
                "max_new_tokens": 512,
                "stop_sequences": "<|end_of_text|>,<|eot_id|>",
                "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
                "presence_penalty": 0,
                "log_performance_metrics": False
            },
        ):
            chunk = str(event)
            response += chunk
          #  print(chunk, end="", flush=True)  # Optional: print in real-time with flush
        
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
    print('\n'+result[0]+'\n')
    conn.close()



    
def main():
    # Check for -re flag
    if len(sys.argv) > 1 and sys.argv[1] == '-re':
        drop_db()
    
    init_db()
    register_chat()
    init_triggers()

    
    while True:
        command = input("Enter prompt: ").strip().lower()


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
                print()
            conn.close()


        else:
            add_task(command)
            print("\n")

if __name__ == "__main__":

    main()


