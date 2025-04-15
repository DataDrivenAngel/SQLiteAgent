DROP TRIGGER IF EXISTS task_completion_trigger;


CREATE TRIGGER IF NOT EXISTS task_completion_trigger
AFTER INSERT ON tasks
WHEN NEW.is_active = 1
BEGIN
  UPDATE tasks
  SET is_active = 0, results = 'task completed', response = chat(goal)
  WHERE id = NEW.id;
END;
