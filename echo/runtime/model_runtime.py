@classmethod
def load_model(cls, model_path):
    print(f"DEBUG: Loading model...")
    cls._instance = Llama(
        model_path=model_path,
        n_ctx=2048,      # This stops the repacking loop (was trying 32k!)
        n_batch=512,     # Processes data in smaller chunks
        n_threads=4,     # Good for laptop/USB performance
        verbose=False    # Keeps the logs clean
    )
    print("SUCCESS: Model ready.")
    return cls._instance