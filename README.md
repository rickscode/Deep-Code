# ai-code: Open Source CLI Coding Agent

## What is this?
A free, open-source alternative to proprietary AI coding assistants (like Claude Code). Deep Code is a CLI tool that lets you:
- Build, edit, and analyze code and apps using open-source LLMs (Groq API, DeepSeek, Llama, etc.)
- Automatically generate and save code files/folders for your requests—no more copy-paste!
- Use a privacy-first, community-driven, extensible coding agent.

## Why?
- Proprietary tools are expensive and closed-source ($17–$200/month)
- You deserve full control, privacy, and transparency
- Open-source means no vendor lock-in and community-driven improvements

## Progress So Far
- [x] Project structure, MIT license, and CI/CD
- [x] Python virtual environment support
- [x] CLI with config, chat, and version commands
- [x] Interactive config: set API key and select model (DeepSeek, Llama, etc.)
- [x] Multi-turn coding chat: ask for an app, code is saved to files/folders automatically
- [x] Clean output: only assistant replies, not raw API responses
- [x] Error handling and user feedback

## Improvements Still To Be Made
- [ ] Smarter folder and file naming (e.g., use app name, language, or user intent)
- [ ] Fewer commands: after config, launch coding chat automatically (no extra command needed)
- [ ] One-step startup: auto-create/activate venv and install dependencies if missing
- [ ] Global CLI install (e.g., just type `ai-code` anywhere)
- [ ] More robust multi-file project support
- [ ] Plugin system for extensibility
- [ ] Git integration, code analysis, and more

## Supported Models
- deepseek-r1-distill-llama-70b
- meta-llama/llama-4-maverick-17b-128e-instruct
- meta-llama/llama-4-scout-17b-16e-instruct
- llama3-70b-8192
- llama-3.3-70b-versatile

## Quick Start
1. **Clone the repo and enter the directory:**
   ```bash
   git clone <repo-url>
   cd ai-code
   ```
2. **Create and activate a Python venv:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install python-slugify
   ```
3. **Configure your API key and model:**
   ```bash
   python3 src/cli/main.py config --set
   # (Select your model and enter your Groq API key)
   ```
4. **Start coding! (multi-turn chat, code is saved automatically):**
   ```bash
   python3 src/cli/main.py chat
   ```
   - Just type your request (e.g., "build me a calculator web app").
   - The agent will create a folder and files for your app automatically.
   - Type `/exit` to quit.

**Tip:**
- You can run all commands from your project root after activating the venv.
- If you see an error about `slugify`, run: `pip install python-slugify`

## Roadmap
- [ ] Smarter file/folder naming
- [ ] Fewer startup steps
- [ ] Global CLI install
- [ ] Plugins, git, and more

## License
MIT
