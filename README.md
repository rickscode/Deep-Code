# Deep-Code: Open Source CLI Coding Agent

![Screenshot from 2025-06-08 23-35-07](https://github.com/user-attachments/assets/7c71830a-6b9e-4fdb-b2b1-3d3cf2c1a016)

## What is this?
A free, open-source alternative to proprietary AI coding assistants (like Claude Code). Deep Code is a CLI tool that lets you:
- Build, edit, and analyze code and apps using DeepSeek via Groq API
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
- [x] Interactive config: set API key and DeepSeek model
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

## Quick Start

### **1. Clone and Install:**
```bash
git clone <repo-url>
cd ai-code
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### **2. Configure API Key:**
```bash
deep-code config --set
# (Enter your Groq API key for DeepSeek)
```

### **3. Start Coding:**
```bash
deep-code
```

That's it! Just type `deep-code` anywhere and start building apps. The AI will:
- Generate code automatically 
- Save files to folders
- Validate and fix errors
- Create working applications

**Examples:**
- `"build me a todo list web app"`
- `"create a calculator with buttons"`
- `"make a responsive landing page"`

Type `/exit` to quit.

## Roadmap
- [ ] Smarter file/folder naming
- [ ] Fewer startup steps
- [ ] Global CLI install
- [ ] Plugins, git, and more

## License
MIT
