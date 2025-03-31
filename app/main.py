
import sqlite3
import replicate
import sys
import os

# Initialize the database
def init_db():
    conn = sqlite3.connect('agent_tasks.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks';")
    if cursor.fetchone() is None:
        with open(os.path.join('sql', 'setup_table_tasks.sql'), 'r') as file:
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
                "system_prompt": "You are a helpful agent embodied in a sql database",
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
    conn = sqlite3.connect('agent_tasks.db')
    cursor = conn.cursor()
    with open(os.path.join('sql', 'setup_triggers.sql'), 'r') as file:
        cursor.executescript(file.read())
    conn.commit()
    conn.close()

# Add a new task
def add_task(goal):
    conn = sqlite3.connect('agent_tasks.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (goal, is_active) VALUES (?, ?)', (goal, 1))
    conn.commit()
    conn.close()

    
def main():
    init_db()
    register_chat()
    init_triggers()
    while True:
        command = input("Enter task (add/list/exit): ").strip().lower()
        if command == 'add':
            goal = input("Enter task goal: ")
            add_task(goal)
            print("Task added.")
        elif command == 'exit':
            print("Exiting the application.")
            sys.exit()
        else:
            print("Unknown command. Please try again.")

if __name__ == "__main__":

    main()


