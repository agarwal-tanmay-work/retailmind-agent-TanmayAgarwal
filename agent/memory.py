"""
Conversation Memory Module
============================
Manages multi-turn conversation history for the RetailMind AI Agent.
Stores messages as a list of role/content dicts, enabling context-aware
follow-up questions and drill-down capabilities.
"""


class ConversationMemory:
    """
    Manages conversation history for multi-turn interactions.
    
    The memory stores the full chat history and provides methods to add
    messages, retrieve context for the LLM, and clear the history.
    """
    
    def __init__(self, max_messages: int = 20):
        """
        Initialize conversation memory.
        
        Args:
            max_messages: Maximum number of message pairs to retain.
                          Older messages are trimmed to keep context window manageable.
        """
        self.messages = []
        self.max_messages = max_messages
    
    def add_message(self, role: str, content: str):
        """
        Add a message to the conversation history.
        
        Args:
            role: 'user' or 'assistant'
            content: The message content
        """
        self.messages.append({"role": role, "content": content})
        
        # Trim if exceeding max messages (keep most recent)
        if len(self.messages) > self.max_messages * 2:
            self.messages = self.messages[-(self.max_messages * 2):]
    
    def get_history(self) -> list[dict]:
        """Get the full conversation history as a list of message dicts."""
        return self.messages.copy()
    
    def get_context_string(self) -> str:
        """
        Get a formatted string of recent conversation history.
        Useful for providing context to the LLM router.
        """
        if not self.messages:
            return "No previous conversation."
        
        context_parts = []
        for msg in self.messages[-10:]:  # Last 10 messages for context
            role = "User" if msg["role"] == "user" else "Agent"
            context_parts.append(f"{role}: {msg['content'][:200]}")
        
        return "\n".join(context_parts)
    
    def clear(self):
        """Clear all conversation history."""
        self.messages = []
    
    def __len__(self):
        return len(self.messages)
