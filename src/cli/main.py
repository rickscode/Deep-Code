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
        "When the user asks for an app or code, ALWAYS output each file as a separate markdown code block, e.g., ```html ... ```, ```js ... ```, etc.\n"
        "Never output code as plain text or in lists—always use markdown code blocks for all code.\n"
        "Do NOT output file lists, plans, or explanations—ONLY output code blocks for each file.\n"
        "If you output anything other than code blocks, it will be ignored.\n"
        "Generate the code and save it to files in a new folder in the current directory.\n"
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
                # Fallback: If no code blocks, but a file list is detected, re-prompt for code
                if not code_blocks:
                    file_list = []
                    for line in content.splitlines():
                        m = re.match(r"[\*-]?\s*`?([\w\-/]+\.[a-zA-Z0-9]+)`?", line.strip())
                        if m:
                            file_list.append(m.group(1))
                    if file_list:
                        # Re-prompt the LLM to generate code for each file
                        followup = f"Please generate the full code for these files, each as a separate markdown code block: {', '.join(file_list)}. Do not output any lists or explanations, just the code blocks."
                        messages.append({"role": "user", "content": followup})
                        response = await client.chat_completion(messages, model=model)
                        content = response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                        code_blocks = re.findall(r"```([a-zA-Z0-9]*)\n([\s\S]*?)```", content)
                # Try to extract file names from the assistant's message
                file_names = {}
                # Look for lines like * `filename.ext` or - `filename.ext`
                for line in content.splitlines():
                    match = re.match(r"[\*-]\s+`([^`]+)`", line.strip())
                    if match:
                        idx = len(file_names)
                        file_names[idx] = match.group(1)
                if code_blocks:
                    import os
                    os.makedirs(folder_name, exist_ok=True)
                    # Build file map: {filename: (lang, code)}
                    file_map = {}
                    for idx, (lang, code) in enumerate(code_blocks):
                        if idx in file_names:
                            file_name = file_names[idx]
                        else:
                            ext = lang if lang else "txt"
                            base = folder_name.replace('-', '_')
                            if ext in ["html", "htm"]:
                                file_name = f"index.{ext}"
                            elif ext in ["js", "jsx", "ts", "tsx"]:
                                file_name = f"app.{ext}"
                            elif ext in ["py", "sh", "bash"]:
                                file_name = f"{base}.{ext}"
                            else:
                                file_name = f"{base}_file{idx+1}.{ext}"
                        file_map[file_name] = (lang, code)
                    # Harmonize file names and references before fixing dependencies
                    file_map = harmonize_file_names(file_map)
                    # Cross-file dependency fix
                    corrected_map = cross_file_dependency_fix(file_map)
                    # Save files
                    for fname, code in corrected_map.items():
                        file_path = os.path.join(folder_name, fname)
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

def harmonize_file_names(file_map):
        """
        Rename files to match standard references if possible, and update all references in all files.
        E.g., if HTML references style.css but only to_do_list_file3.css exists, rename the file and update all references.
        """
        import re
        # Standard names for common file types
        standard_names = {
            '.js': 'app.js',
            '.css': 'style.css',
            '.html': 'index.html',
        }
        # Collect all references in all files
        references = {'js': set(), 'css': set(), 'img': set()}
        for fname, (lang, code) in file_map.items():
            if lang.lower() in ["html", "htm"]:
                # <script src="..."></script>
                for m in re.findall(r'<script src=["\']([^"\']+)["\']></script>', code):
                    references['js'].add(m)
                # <link href="..." rel="stylesheet">
                for m in re.findall(r'<link href=["\']([^"\']+)["\'] rel="stylesheet">', code):
                    references['css'].add(m)
                # <img src="...">
                for m in re.findall(r'<img src=["\']([^"\']+)["\']>', code):
                    references['img'].add(m)
        # Map extensions to actual files, and allow for extension normalization (e.g., .javascript -> .js)
        ext_aliases = {'.javascript': '.js', '.js': '.js', '.css': '.css', '.html': '.html'}
        ext_to_files = {}
        for ext in ['.js', '.css', '.html', '.javascript']:
            ext_to_files[ext] = [f for f in file_map if f.endswith(ext)]
        # For each type, if a standard reference exists but the file is named differently or has a nonstandard extension, rename and update references
        rename_map = {}
        for ext, std_name in standard_names.items():
            # Accept alias extensions (e.g., .javascript for .js)
            candidates = ext_to_files.get(ext, [])
            if ext == '.js':
                candidates += ext_to_files.get('.javascript', [])
            if std_name not in file_map and len(candidates) == 1:
                referenced = False
                if ext == '.js' and std_name in references['js']:
                    referenced = True
                if ext == '.css' and std_name in references['css']:
                    referenced = True
                if ext == '.html':
                    referenced = True  # Always prefer index.html for html
                if referenced or ext != '.html':
                    old_name = candidates[0]
                    # Normalize extension if needed
                    if ext == '.js' and old_name.endswith('.javascript'):
                        rename_map[old_name] = std_name
                    else:
                        rename_map[old_name] = std_name
        # Apply renames and update all references in all files
        new_file_map = {}
        for fname, (lang, code) in file_map.items():
            # Update references in code
            for old, new in rename_map.items():
                code = code.replace(old, new)
            new_name = rename_map.get(fname, fname)
            # JS syntax fix: remove unmatched closing braces at end
            if new_name.endswith('.js'):
                # Remove extra closing braces at end
                code = re.sub(r'(\}\s*)+$', '', code)
            new_file_map[new_name] = (lang, code)
        return new_file_map

def cross_file_dependency_fix(file_map):
    """
    file_map: dict of {filename: (lang, code)}
    Returns: dict of {filename: corrected_code}
    """
    import re
    corrected = {}
    all_files = set(file_map.keys())

    # --- Registry of fixer functions ---
    def html_fixer(fname, lang, code, all_files):
        # Helper: get all files by extension
        def files_by_ext(ext):
            return [f for f in all_files if f.lower().endswith(ext)]
        # Fix <script src>, <link href>, <img src>
        def fix_script_src(match):
            src = match.group(1)
            if src not in all_files:
                # Try to find a close match (e.g., missing extension)
                for f in all_files:
                    if f.startswith(src.split(".")[0]):
                        return f'<script src="{f}"></script>'
                # Always use the only JS file if there is just one
                js_files = files_by_ext('.js')
                if len(js_files) == 1:
                    return f'<script src="{js_files[0]}"></script>'
            return f'<script src="{src}"></script>'
        code = re.sub(r'<script src=["\']([^"\']+)["\']></script>', fix_script_src, code)
        def fix_link_href(match):
            href = match.group(1)
            if href not in all_files:
                for f in all_files:
                    if f.startswith(href.split(".")[0]):
                        return f'<link href="{f}" rel="stylesheet">'
                # Always use the only CSS file if there is just one
                css_files = files_by_ext('.css')
                if len(css_files) == 1:
                    return f'<link href="{css_files[0]}" rel="stylesheet">'
            return f'<link href="{href}" rel="stylesheet">'
        code = re.sub(r'<link href=["\']([^"\']+)["\'] rel="stylesheet">', fix_link_href, code)
        def fix_img_src(match):
            src = match.group(1)
            if src not in all_files:
                for f in all_files:
                    if f.startswith(src.split(".")[0]):
                        return f'<img src="{f}">' 
                # Always use the only image file if there is just one
                img_files = [f for f in all_files if f.lower().endswith(('.png','.jpg','.jpeg','.gif','.svg'))]
                if len(img_files) == 1:
                    return f'<img src="{img_files[0]}">' 
            return f'<img src="{src}">' 
        code = re.sub(r'<img src=["\']([^"\']+)["\']>', fix_img_src, code)
        return code

    def js_fixer(fname, lang, code, all_files):
        # Fix import ... from '...'
        def fix_import(match):
            imp = match.group(1)
            if imp not in all_files:
                for f in all_files:
                    if f.startswith(imp.split(".")[0]):
                        return f"import ... from './{f}'"
            return match.group(0)
        code = re.sub(r"import [^;]+ from ['\"](.+?)['\"]", fix_import, code)
        return code

    def py_fixer(fname, lang, code, all_files):
        # Fix import ...
        def fix_py_import(match):
            mod = match.group(1)
            for f in all_files:
                if f.startswith(mod) and f.endswith('.py'):
                    return f"import {f[:-3]}"
            return match.group(0)
        code = re.sub(r"import ([a-zA-Z0-9_]+)", fix_py_import, code)
        return code

    def css_fixer(fname, lang, code, all_files):
        # Fix url('...')
        def fix_css_url(match):
            url = match.group(1)
            if url not in all_files:
                for f in all_files:
                    if f.startswith(url.split(".")[0]):
                        return f"url('{f}')"
            return match.group(0)
        code = re.sub(r"url\(['\"]?([^'\")]+)['\"]?\)", fix_css_url, code)
        return code

    def bash_fixer(fname, lang, code, all_files):
        # Fix source ... or ./...
        def fix_source(match):
            src = match.group(1)
            if src not in all_files:
                for f in all_files:
                    if f.startswith(src.split(".")[0]):
                        return f"source {f}"
            return match.group(0)
        code = re.sub(r"source ([^\s]+)", fix_source, code)
        return code

    # Registry: lang -> fixer
    fixers = {
        "html": html_fixer,
        "htm": html_fixer,
        "js": js_fixer,
        "jsx": js_fixer,
        "ts": js_fixer,
        "tsx": js_fixer,
        "py": py_fixer,
        "css": css_fixer,
        "bash": bash_fixer,
        "sh": bash_fixer,
    }

    for fname, (lang, code) in file_map.items():
        fixer = fixers.get(lang.lower())
        if fixer:
            corrected[fname] = fixer(fname, lang, code, all_files)
        else:
            corrected[fname] = code
    return corrected

if __name__ == "__main__":
    app()
