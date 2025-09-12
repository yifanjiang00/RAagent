from utils.helpers import call_llm, RESEARCH_TASKS

class Retriever:
    def reply(self, topic, messages=None):
        # This method will implement the logic to retrieve information from the web
        # based on the provided topic. For now, it will return a placeholder response.
        system_prompt = RESEARCH_TASKS["information_retrieval"]["system_prompt"]
        retriever = call_llm(topic, prompt=system_prompt, messages=messages)
        return retriever