from utils.helpers import call_llm, RESEARCH_TASKS

class Comparer:
    def reply(self, topic, messages=None):
        # This method will retrieve different viewpoints on the given topic
        # and compare them for the user.
        system_prompt = RESEARCH_TASKS["viewpoint_comparison"]["system_prompt"]
        comparison = call_llm(topic, prompt=system_prompt, messages=messages)
        return comparison