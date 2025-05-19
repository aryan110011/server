from flask import Flask, request, jsonify, Response
import time
import threading

app = Flask(__name__)

conversations = {}         # Stores ongoing conversations
resumable_conversations = {}  # Stores stopped/resumable conversations

def simulate_conversation(convo_data):
    name = convo_data['convo_name']
    delay = convo_data['delay']
    messages = convo_data['messages']
    group_ids = convo_data['group_ids']
    hatter_name = convo_data['hatter_name']

    for group in group_ids:
        for msg in messages:
            if name not in conversations:
                break  # Stop if convo was stopped
            log = f"[{group}] {hatter_name}: {msg}"
            conversations[name].append(log)
            time.sleep(delay)
    if name in conversations:
        resumable_conversations[name] = conversations.pop(name)

@app.route("/start_convo", methods=["POST"])
def start_convo():
    data = request.get_json()
    convo_name = data.get("convo_name")
    if convo_name in conversations:
        return f"Conversation '{convo_name}' already running.", 400

    conversations[convo_name] = []
    thread = threading.Thread(target=simulate_conversation, args=(data,))
    thread.start()
    return f"Conversation '{convo_name}' started."

@app.route("/view_convos", methods=["GET"])
def view_convos():
    return jsonify({"conversations": list(conversations.keys())})

@app.route("/stream_convo/<convo_name>", methods=["GET"])
def stream_convo(convo_name):
    def event_stream():
        seen = 0
        while convo_name in conversations:
            logs = conversations[convo_name]
            for log in logs[seen:]:
                yield f"data: {log}\n\n"
                seen += 1
            time.sleep(1)
    return Response(event_stream(), content_type="text/event-stream")

@app.route("/resume_convos", methods=["GET"])
def resume_convos():
    return jsonify({"resumable": list(resumable_conversations.keys())})

@app.route("/stream_resume/<convo_name>", methods=["GET"])
def stream_resume(convo_name):
    logs = resumable_conversations.get(convo_name, [])
    def event_stream():
        for log in logs:
            yield f"data: {log}\n\n"
    return Response(event_stream(), content_type="text/event-stream")

@app.route("/stop_convo", methods=["POST"])
def stop_convo():
    data = request.get_json()
    convo_name = data.get("convo_name")
    if convo_name in conversations:
        resumable_conversations[convo_name] = conversations.pop(convo_name)
        return f"Conversation '{convo_name}' stopped."
    return f"Conversation '{convo_name}' not found.", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
