import dspy
from dspy import Signature, InputField, OutputField, Module, Predict
from src.core.config import settings
import os

# 1. DSPy Adapter for llama-cpp-python
class LlamaCppLM(dspy.LM):
    def __init__(self, model_path: str, context_window: int = 4096, **kwargs):
        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError("llama-cpp-python is required for local LLM. Please install it.")
            
        super().__init__(model="llama-cpp", **kwargs)
        self.model_path = model_path
        
        if not os.path.exists(model_path):
             print(f"WARNING: Local model not found at {model_path}. Calls will fail.")
             self.llm = None
        else:
             print(f"Loading Local GGUF Model: {model_path}")
             self.llm = Llama(
                model_path=model_path,
                n_ctx=context_window,
                n_gpu_layers=-1, # Try to offload all to GPU if available/supported, or 0 for CPU
                verbose=False
             )

    def basic_request(self, prompt, **kwargs):
        if not self.llm:
            return ["Error: Model not loaded."]
            
        # Standard generation parameters
        max_tokens = kwargs.get("max_tokens", 512)
        temperature = kwargs.get("temperature", 0.7)
        
        output = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["User:", "\n\nUser"], # Stop tokens to prevent hallucinating next turn
            echo=False
        )
        return [output['choices'][0]['text']]
    


# 2. Signature
class LegalQASignature(Signature):
    """Answer legal questions based on the provided context in Bengali."""
    
    context = InputField(desc="Relevant legal documents and sections")
    question = InputField(desc="The user's legal question")
    answer = OutputField(desc="Detailed answer in Bengali. Must cite sources from context.")

# 3. Module
class BanglaRAG(Module):
    def __init__(self):
        super().__init__()
        self.generate_answer = Predict(LegalQASignature)
    
    def forward(self, context, question):
        return self.generate_answer(context=context, question=question)

# 4. Main Wrapper Class
class BanglaLLM:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.lm = None
        self._configure_dspy()
        
        self.rag_module = BanglaRAG()

    def _configure_dspy(self):
        if self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                 print("WARNING: OpenAI API Key not set.")
                 return
            model_id = f"openai/{settings.LLM_MODEL_NAME}"
            self.lm = dspy.LM(model=model_id, api_key=settings.OPENAI_API_KEY)
            print(f"Configured DSPy with OpenAI: {settings.LLM_MODEL_NAME}")
            
        elif self.provider == "local":
            self.lm = LlamaCppLM(model_path=settings.LLM_MODEL_FILE)
            print(f"Configured DSPy with Local Model: {settings.LLM_MODEL_FILE}")
            
        else:
            print(f"Unknown LLM Provider: {self.provider}")
            
        if self.lm:
            dspy.settings.configure(lm=self.lm)

    def generate_response(self, context: str, query: str) -> str:
        if not self.lm:
            return "Error: LLM not configured or model missing."
            
        # Ensure context is being used
        # dspy.settings.configure(lm=self.lm) # Ensure context is set (globally or locally?)
        # Global is fine for this single-threaded/simple app, but for async/concurrency we might need contexts
        
        try:
            response = self.rag_module(context=context, question=query)
            return response.answer
        except Exception as e:
            print(f"LLM Generation Error: {e}")
            return "Thinking..." # Fallback or error message
