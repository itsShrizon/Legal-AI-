from llama_cpp import Llama
import os

class QwenEngine:
    def __init__(self, model_path="models/qwen-3.gguf"):
        print(f"Loading Qwen GGUF from {model_path}...")
        
        if not os.path.exists(model_path):
            print(f"WARNING: Model file {model_path} not found. Using placeholder.")
            self.llm = None
            return

        self.llm = Llama(model_path=model_path, n_ctx=4096, n_gpu_layers=-1, verbose=False)

    def generate_response(self, context: str, user_query: str):
        if self.llm is None:
            return "Simulated AI Response: Model not loaded."

        prompt = f'''<|im_start|>system
You are a helpful Bangla Legal Assistant. Use the context below to answer.
Context: {context}<|im_end|>
<|im_start|>user
{user_query}<|im_end|>
<|im_start|>assistant
'''
        output = self.llm(prompt, max_tokens=512, stop=["<|im_end|>"], echo=False)
        return output['choices'][0]['text']
