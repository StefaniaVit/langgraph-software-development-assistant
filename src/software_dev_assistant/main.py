from pprint import pprint
import software_dev_assistant.graph as graph_module


def run_demo():
    app = graph_module.build_graph()

    initial_state = {
        "task_id": "demo-001",
        "user_request": "Review this Python function, suggest tests, and improve documentation.",
        "code_snippet": "def add(a, b): return a + b",
        "language": "python",
        "completed_agents": [],
        "skipped_agents": [],
        "agent_status": {},
        "retry_counts": {},
        "error_log": [],
        "fallback_used": False,
        "telemetry_events": [],
    }

    result = app.invoke(initial_state)
    pprint(result)


if __name__ == "__main__":
    run_demo()