from crewai import Engine
from workflows.blog_workflow import workflow

if __name__ == "__main__":
    # Run the workflow
    engine = Engine()
    result = engine.run(workflow)
    print("Final Output:", result)
