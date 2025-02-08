from openai import OpenAI


def query_deepseek(
    messages,
    api_key,
    model="Pro/deepseek-ai/DeepSeek-R1",
    max_tokens=8192,
    temperature=0.7,
    top_p=0.7,
    frequency_penalty=0.5,
    stop=["null"],
    n=1,
    verbose=True,
    prefix=None,
    updates_queue=None,
    limit=None,
    stop_event=None,
):
    """Query the DeepSeek API with the given parameters."""
    client = OpenAI(base_url="https://api.siliconflow.cn/v1", api_key=api_key)

    completion_params = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "stop": stop,
        "n": n,
        "stream": True,
    }

    if prefix:
        completion_params["extra_body"] = {"prefix": prefix}

    try:
        response = client.chat.completions.create(**completion_params)

        reasoning, answer = "", ""
        for chunk in response:
            # Check stop event first
            if stop_event and stop_event.is_set():
                # Send immediate stop notification
                if updates_queue:
                    updates_queue.put({"type": "stopped"})
                return reasoning, answer

            if chunk.choices[0].delta.reasoning_content:
                content = chunk.choices[0].delta.reasoning_content
                reasoning += content
                # Send updates immediately
                if updates_queue:
                    updates_queue.put({"type": "thinking", "message": content})
                if verbose:
                    print(content, end="", flush=True)  # Flush output immediately
            elif chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                answer += content
                if verbose:
                    print(content, end="", flush=True)

            if limit and len(reasoning) > limit:
                stop_str = "...\nI've been thinking too much, let's stop here. <try>"
                reasoning += stop_str
                if updates_queue:
                    updates_queue.put({"type": "thinking", "message": stop_str})
                break

        return reasoning, answer

    except Exception as e:
        print(f"Error in query_deepseek: {str(e)}")
        if updates_queue:
            updates_queue.put({"type": "error", "message": str(e)})
        return "", None
