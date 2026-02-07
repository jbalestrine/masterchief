from echo.chat_bot import get_chat_bot


def main():
    bot = get_chat_bot()
    model = bot._find_gguf_model()
    print('Selected model:', model)
    try:
        out = bot._generate_with_llm('Say hello in one short sentence.', max_tokens=64, temperature=0.2)
        print('LLM output:', out)
    except Exception:
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
