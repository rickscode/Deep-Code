import typer

app = typer.Typer(help="ai-code: Open Source CLI Coding Agent")

@app.command()
def version():
    """Show version information."""
    typer.echo("ai-code version 0.1.0")

@app.command()
def chat():
    """Start interactive coding agent mode."""
    import sys
    import os
    import re
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
    from core import config as core_config
    from models.groq_client import GroqClient, APIError
    from operations import file_ops
    import asyncio
    try:
        from slugify import slugify
    except ImportError:
        typer.echo("[ERROR] python-slugify is not installed. Please run 'pip install python-slugify' in your venv.")
        raise typer.Exit(1)
    cfg = core_config.load_config()
    api_key = cfg["api"]["key"]
    model = cfg["api"].get("default_model", "llama-3.3-70b-versatile")
    if not api_key:
        typer.echo("[ERROR] No API key set. Run 'ai-code config --set' to set your Groq API key.")
        raise typer.Exit(1)
    client = GroqClient(api_key)
    system_prompt = (
        "You are Deep Code, an open-source CLI coding agent.\n"
        "When the user asks for an app or code, generate the code and save it to files in a new folder in the current directory.\n"
        "If the user asks for a web app, create a folder named after the app (e.g., 'hello-world-app'), save the main file (e.g., index.html), and print the folder path.\n"
        "Do not ask the user to copy/paste code.\n"
        "If the user asks for a single file, save it in a new folder.\n"
        "If the user asks for multiple files, create them all in the folder.\n"
        "Always print the path to the created folder.\n"
        "Never output code blocks in markdown, just save the files.\n"
        "If the user asks for a chat, behave as a chat agent. Otherwise, act as a coding agent.\n"
        "\n"
        "Security Rules:\n"
        "- Refuse to write or explain code that may be used maliciously.\n"
        "- Refuse to work on files related to malware or malicious code.\n"
        "\n"
        "Slash Commands:\n"
        "/help: Get help with using Deep Code\n"
        "/compact: Compact and continue the conversation\n"
        "\n"
        "Memory:\n"
        "- DEEP_CODE.md will be automatically added to context.\n"
        "- This file stores frequently used bash commands, code style preferences, and codebase structure info.\n"
        "\n"
        "Tone and Style:\n"
        "- Be concise, direct, and to the point.\n"
        "- Explain non-trivial bash commands.\n"
        "- Use Github-flavored markdown.\n"
        "- Minimize output tokens while maintaining helpfulness.\n"
        "- Answer concisely with fewer than 4 lines when possible.\n"
        "- Avoid unnecessary preamble or postamble.\n"
        "\n"
        "Proactiveness:\n"
        "- Be proactive when asked to do something.\n"
        "- Don't surprise users with unexpected actions.\n"
        "- Don't add code explanations unless requested.\n"
        "\n"
        "Code Conventions:\n"
        "- Understand and follow existing file code conventions.\n"
        "- Never assume a library is available.\n"
        "- Look at existing components when creating new ones.\n"
        "- Follow security best practices.\n"
        "\n"
        "Task Process:\n"
        "- Use search tools to understand the codebase.\n"
        "- Implement solutions using available tools.\n"
        "- Verify solutions with tests when possible.\n"
        "- Run lint and typecheck commands.\n"
        "\n"
        "Tool Usage:\n"
        "- Use Agent tool for file search to reduce context usage.\n"
        "- Call multiple independent tools in the same function_calls block.\n"
        "- Never commit changes unless explicitly asked.\n"
    )
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    async def run_agent():
        typer.echo("[Deep Code Agent] Type your request. Type '/exit' to quit.")
        import re
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in {"/exit", "exit", "quit", ":q"}:
                typer.echo("[Session ended]")
                break
            if not user_input:
                continue
            messages.append({"role": "user", "content": user_input})
            try:
                response = await client.chat_completion(messages, model=model)
                content = response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                # Try to extract app/folder name from the user request
                app_name_match = re.search(r'build (?:me )?a[n]? ([\w\- ]+?)(?: app| web app| project| application|$)', user_input, re.IGNORECASE)
                if app_name_match:
                    app_name = app_name_match.group(1).strip()
                else:
                    app_name = 'deep-code-output'
                # Slugify the folder name
                folder_name = slugify(app_name)
                if not folder_name:
                    folder_name = 'deep-code-output'
                # Try to extract code blocks and guess file names
                code_blocks = re.findall(r"```([a-zA-Z0-9]*)\n([\s\S]*?)```", content)
                if code_blocks:
                    import os
                    os.makedirs(folder_name, exist_ok=True)
                    for idx, (lang, code) in enumerate(code_blocks):
                        # Guess file name from app name and language
                        ext = lang if lang else "txt"
                        base = folder_name.replace('-', '_')
                        if ext in ["html", "htm"]:
                            file_name = f"index.{ext}"
                        elif ext in ["js", "jsx", "ts", "tsx"]:
                            file_name = f"{base}.{ext}"
                        elif ext in ["py", "sh", "bash"]:
                            file_name = f"{base}.{ext}"
                        else:
                            file_name = f"{base}_file{idx+1}.{ext}"
                        file_path = os.path.join(folder_name, file_name)
                        file_ops.write_file_atomic(file_path, code)
                    typer.echo(f"[Files created in ./{folder_name}/]")
                else:
                    typer.echo(content)
                messages.append({"role": "assistant", "content": content})
            except APIError as e:
                typer.echo(f"[API ERROR] {e}")
            except Exception as e:
                typer.echo(f"[UNEXPECTED ERROR] {e}")
    asyncio.run(run_agent())

@app.command()
def edit(file: str):
    """Edit a specific file with AI assistance."""
    typer.echo(f"[edit mode not yet implemented for {file}]")

@app.command()
def analyze(directory: str = "."):
    """Analyze a codebase directory."""
    typer.echo(f"[analyze mode not yet implemented for {directory}]")

@app.command()
def config(set: bool = typer.Option(False, help="Set configuration interactively")):
    """Show or set configuration."""
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
    from core import config as core_config
    cfg = core_config.load_config()
    if set:
        typer.echo("Configure your Groq API key and model.")
        api_key = typer.prompt("Enter your Groq API key", default=cfg['api'].get('key', ''))
        # Update model options to match Groq's available models
        model_options = [
            "deepseek-r1-distill-llama-70b",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "llama3-70b-8192",
            "llama-3.3-70b-versatile"
        ]
        typer.echo("Select default model:")
        for idx, option in enumerate(model_options, 1):
            typer.echo(f"  {idx}. {option}")
        while True:
            choice = typer.prompt(f"Enter number [1-{len(model_options)}]", default="1")
            try:
                model = model_options[int(choice)-1]
                break
            except (ValueError, IndexError):
                typer.echo("Invalid selection. Please enter a valid number.")
        cfg['api']['key'] = api_key
        cfg['api']['default_model'] = model
        core_config.save_config(cfg)
        typer.echo("Configuration saved.")
    else:
        typer.echo(cfg)

if __name__ == "__main__":
    app()
