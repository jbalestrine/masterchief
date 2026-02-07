from llama_cpp import Llama

model_path = r"c:\Users\Echo\masterchief\models\Phi-3-mini-4k-instruct-q4.gguf"
print('Attempting to load model at', model_path)
try:
    m = Llama(model_path=model_path, n_ctx=4096, n_threads=4)
    print('GGUF loaded OK')
    # quick generation
    out = m.create(prompt='Say hello', max_tokens=16, temperature=0.2)
    print('Generation:', getattr(out, 'text', out))
except Exception as e:
    print('Model load failed:', e)
    raise
