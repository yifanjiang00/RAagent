import gradio as gr
from agent.retriever import Retriever
from agent.summarizer import Summarizer
from agent.explainer import Explainer
from agent.comparer import Comparer
from agent.outline_generator import OutlineGenerator

# Initialize the AI agents
retriever = Retriever()
summarizer = Summarizer()
explainer = Explainer()
comparer = Comparer()
outline_generator = OutlineGenerator()

def process_request(topic, action):
    if action == "Retrieve Information":
        return retriever.retrieve_information(topic)
    elif action == "Summarize Text":
        text = retriever.retrieve_information(topic)
        return summarizer.summarize_text(text)
    elif action == "Explain Concept":
        return explainer.explain_concept(topic)
    elif action == "Compare Views":
        return comparer.compare_views(topic)
    elif action == "Generate Outline":
        return outline_generator.generate_outline(topic)
    else:
        return "Invalid action selected."

with gr.Blocks() as iface:
    gr.Markdown("# Intelligent Research Assistant\nAn AI assistant to help with research tasks.")
    topic = gr.Textbox(label="Enter Topic")
    action = gr.Radio(
        label="Select Action",
        choices=["Retrieve Information", "Summarize Text", "Explain Concept", "Compare Views", "Generate Outline"]
    )
    output = gr.Textbox(label="Output")
    btn = gr.Button("Submit")
    btn.click(process_request, inputs=[topic, action], outputs=output)

if __name__ == "__main__":
    iface.launch()