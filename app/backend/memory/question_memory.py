class QuestionMemory:
    """
    Simple in-memory cache for questions and answers
    """

    def __init__(self):
        self._memory = {}

    def get(self, question: str):
        return self._memory.get(question)

    def store(self, question: str, answer: str):
        self._memory[question] = answer
