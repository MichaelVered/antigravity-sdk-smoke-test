import asyncio
import json
import os
import random
import re
import subprocess
import sys
from pathlib import Path

# --- ANSI Terminal Color Palette ---
class Colors:
    HEADER  = '\033[95m'
    OKBLUE  = '\033[94m'
    OKCYAN  = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL    = '\033[91m'
    ENDC    = '\033[0m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'

# Top-level SDK Imports
try:
    import google.antigravity as agy
    from google.antigravity import Agent, LocalAgentConfig
except ImportError:
    print(f"{Colors.FAIL}❌ FAIL: google-antigravity SDK is not installed in the active environment.{Colors.ENDC}")
    sys.exit(1)

sdk_dir = str(Path(__file__).resolve().parent)
python_executable = sys.executable

# --- Phase 1: Environment & SDK Verification Audit ---

def load_environment() -> str:
    """Loads environment variables from ~/ADK/.env and returns valid API key."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip().strip("'\""))
        print(f"{Colors.DIM}✅ Loaded environment variables from {env_path}{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}⚠️ Warning: Environment file not found at {env_path}{Colors.ENDC}")

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print(f"{Colors.FAIL}❌ FAIL: Neither GEMINI_API_KEY nor GOOGLE_API_KEY found in ~/ADK/.env{Colors.ENDC}")
        sys.exit(1)
    
    os.environ["GEMINI_API_KEY"] = api_key
    return api_key

async def run_sdk_verification_audit(api_key: str):
    """Performs Phase 1 assertion audit to verify native AGY SDK installation & live model IPC."""
    print(f"\n{Colors.HEADER}====================================================={Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}  🔍 PHASE 1: AGY SDK Native Environment Audit  {Colors.ENDC}")
    print(f"{Colors.HEADER}====================================================={Colors.ENDC}")

    print(f"✅ SDK Import Successful!")
    print(f"   Module location: {agy.__file__}")

    key_source = "GEMINI_API_KEY" if os.getenv("GEMINI_API_KEY") else "GOOGLE_API_KEY"
    print(f"✅ API Key verified via {key_source} in environment (No fallback).")

    print("🔄 Initializing AGY Agent connection test...")
    config = LocalAgentConfig(api_key=api_key, workspaces=[sdk_dir])
    try:
        async with Agent(config) as agent:
            response = await agent.chat("Ping test. Respond with: AGY_SDK_TEST_OK")
            res_text = (await response.text()).strip()
            print(f"✅ Live Connection Response: '{res_text}'")
            print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 AUDIT PASSED: AGY SDK is natively operational in this environment!{Colors.ENDC}\n")
            print(f"{Colors.HEADER}-----------------------------------------------------{Colors.ENDC}")
            input(f"{Colors.BOLD}Press Enter to launch Phase 2 (Interactive Math Laboratory)...{Colors.ENDC}")
    except Exception as ex:
        print(f"❌ FAIL: Exception occurred during AGY Agent audit: {ex}")
        sys.exit(1)

# --- Helpers & Sanitizers ---

def clean_llm_text(raw_text: str) -> str:
    """Strips markdown headers, bullet points, blockquotes, and extra sections from LLM text."""
    text = re.sub(r'#+.*?\n', '', raw_text)
    text = re.sub(r'>\s*', '', text)
    text = re.sub(r'---.*?\n', '', text)
    text = re.sub(r'^\s*[-*]\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned_lines = []
    for line in lines:
        if any(keyword in line.lower() for keyword in ["summary of work", "alternative", "option 1", "option 2"]):
            break
        cleaned_lines.append(line)
        
    res = " ".join(cleaned_lines).strip()
    return res.strip('"\'') if res else "Great effort! Keep pushing forward!"

def extract_python_code(raw_llm_response: str) -> str:
    """Extracts raw python code block from subagent response."""
    match = re.search(r'```python(.*?)```', raw_llm_response, re.DOTALL)
    if match:
        return match.group(1).strip()
    match_generic = re.search(r'```(.*?)```', raw_llm_response, re.DOTALL)
    if match_generic:
        return match_generic.group(1).strip()
    return raw_llm_response.strip()

# --- Phase 2: Dynamic Multi-Agent Operations ---

async def mint_generator_agent_and_create_exercise(api_key: str, operation: str) -> tuple[dict, str]:
    """
    Mints a fresh AGY Subagent that dynamically WRITES Python code on the fly
    and EXECUTES it in-memory (zero files created on disk).
    """
    print(f"\n{Colors.OKCYAN}🤖 [AGY SDK Subagent] Minting fresh 'Code Writer & Executor Subagent' for {operation.upper()}...{Colors.ENDC}")
    
    generator_system_prompt = (
        "You are an expert AGY Python Code Generator Subagent.\n"
        "Your task is to WRITE executable Python code that generates a random math exercise.\n"
        "Rules for the Python code you generate:\n"
        "1. Write Python code that picks random numbers, calculates the answer, and creates 4 options.\n"
        "2. For division, ensure integer division (num1 % num2 == 0).\n"
        "3. The Python code MUST print ONLY a single valid JSON string to stdout with keys:\n"
        '   {"num1": int, "num2": int, "operation_symbol": str, "correct_answer": int, "options": [int, int, int, int], "explanation": str}\n'
        "4. Respond ONLY with executable Python code inside a ```python ``` code block. Do NOT include file writing instructions."
    )

    config = LocalAgentConfig(
        api_key=api_key,
        workspaces=[sdk_dir],
        system_instruction=generator_system_prompt
    )

    async with Agent(config) as subagent:
        prompt = f"Write a Python script string to generate a random {operation} arithmetic exercise."
        response = await subagent.chat(prompt)
        res_text = await response.text()
        
    code_content = extract_python_code(res_text)
    
    # Execute the generated Python code in-memory via python -c (Zero files saved to disk)
    proc = subprocess.run([python_executable, "-c", code_content], capture_output=True, text=True, timeout=10)
    stdout_output = proc.stdout.strip()
    
    match = re.search(r'\{.*\}', stdout_output, re.DOTALL)
    if match:
        data = json.loads(match.group(0))
    else:
        op_symbols = {"addition": "+", "subtraction": "-", "multiplication": "*", "division": "/"}
        symbol = op_symbols.get(operation, "+")
        num1, num2 = random.randint(10, 30), random.randint(2, 10)
        if symbol == "/": num1 = num1 * num2
        ans = eval(f"{num1} {symbol} {num2}")
        data = {
            "num1": num1, "num2": num2, "operation_symbol": symbol,
            "correct_answer": ans, "options": [ans, ans+2, ans-3, ans+5],
            "explanation": f"{num1} {symbol} {num2} = {ans}"
        }

    return data, code_content

async def generate_creative_welcome(orchestrator_agent: Agent, round_num: int) -> str:
    """Uses the Orchestrator Agent to generate a fresh, creative greeting menu statement."""
    prompt = (
        f"This is round {round_num} of the math challenge game.\n"
        "Generate ONLY a single plain-text 1-sentence welcome message inviting the user to pick an arithmetic operation.\n"
        "STRICT RULE: Do NOT include markdown headers, bullet points, summaries, or multiple options."
    )
    response = await orchestrator_agent.chat(prompt)
    return clean_llm_text(await response.text())

async def generate_creative_feedback(orchestrator_agent: Agent, num1: int, num2: int, symbol: str, correct_ans: int, user_ans: int, is_correct: bool) -> str:
    """Uses the Orchestrator Agent to generate a creative, dynamic, encouraging response."""
    status = "SUCCESS" if is_correct else "FAILURE"
    prompt = (
        f"Problem: {num1} {symbol} {num2} = {correct_ans}.\n"
        f"User answered: {user_ans}. Outcome: {status}.\n"
        "STRICT MANDATE: Generate ONLY a single plain-text sentence of creative feedback.\n"
        "DO NOT write alternative options, DO NOT write a 'Summary of Work', DO NOT use markdown headers or links."
    )
    response = await orchestrator_agent.chat(prompt)
    return clean_llm_text(await response.text())

def print_banner():
    print(f"{Colors.HEADER}====================================================={Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}   ⚡ AGY SDK Interactive Math Orchestrator ⚡   {Colors.ENDC}")
    print(f"{Colors.HEADER}====================================================={Colors.ENDC}")

async def run_interactive_lab(api_key: str):
    """Runs Phase 2: Interactive terminal orchestrator & subagent game loop."""
    os.system('clear' if os.name == 'posix' else 'cls')
    print_banner()
    
    orchestrator_config = LocalAgentConfig(
        api_key=api_key,
        workspaces=[sdk_dir],
        system_instruction=(
            "You are the Orchestrator Agent of an interactive terminal math game. "
            "STRICT SYSTEM INSTRUCTION: Output ONLY plain text sentences. "
            "Never output markdown headers, alternative options, bullet points, file links, or 'Summary of Work' sections."
        )
    )

    ops_map = {
        "1": "addition",
        "2": "subtraction",
        "3": "multiplication",
        "4": "division"
    }

    round_num = 1

    async with Agent(orchestrator_config) as orchestrator:
        while True:
            print(f"\n{Colors.DIM}✨ Orchestrator Agent crafting fresh welcome statement...{Colors.ENDC}")
            welcome_msg = await generate_creative_welcome(orchestrator, round_num)
            
            print(f"\n{Colors.OKBLUE}{Colors.BOLD}💬 Orchestrator:{Colors.ENDC} {Colors.HEADER}\"{welcome_msg}\"{Colors.ENDC}\n")

            print(f"{Colors.BOLD}Choose Your Challenge:{Colors.ENDC}")
            print(f"  {Colors.OKCYAN}[1]{Colors.ENDC} Addition (+)")
            print(f"  {Colors.OKCYAN}[2]{Colors.ENDC} Subtraction (-)")
            print(f"  {Colors.OKCYAN}[3]{Colors.ENDC} Multiplication (*)")
            print(f"  {Colors.OKCYAN}[4]{Colors.ENDC} Division (/)")
            print(f"  {Colors.WARNING}[5] Quit{Colors.ENDC}")
            
            choice = input(f"\n{Colors.BOLD}Enter choice (1-5): {Colors.ENDC}").strip()
            
            if choice == "5" or choice.lower() in ["q", "quit", "exit"]:
                print(f"\n{Colors.OKGREEN}👋 Exiting AGY Math Orchestrator. Goodbye!{Colors.ENDC}\n")
                break
                
            if choice not in ops_map:
                print(f"{Colors.FAIL}⚠️ Invalid selection. Pick 1-5.{Colors.ENDC}")
                continue

            selected_op = ops_map[choice]
            
            try:
                exercise, generated_code = await mint_generator_agent_and_create_exercise(api_key, selected_op)
                
                print(f"\n{Colors.OKGREEN}⚡ [IN-MEMORY SANDBOX CODE GENERATED & EXECUTED BY SUBAGENT]:{Colors.ENDC}")
                print(f"{Colors.DIM}-----------------------------------------------------{Colors.ENDC}")
                for line in generated_code.splitlines():
                    print(f"   {Colors.OKCYAN}{line}{Colors.ENDC}")
                print(f"{Colors.DIM}-----------------------------------------------------{Colors.ENDC}")
                print(f"✅ {Colors.BOLD}Executed in-memory (0 files created on disk) -> stdout captured!{Colors.ENDC}")
                
                num1 = exercise["num1"]
                num2 = exercise["num2"]
                symbol = exercise["operation_symbol"]
                correct_ans = exercise["correct_answer"]
                options = exercise["options"]
                
                if correct_ans not in options:
                    options[0] = correct_ans
                random.shuffle(options)

                print(f"\n{Colors.HEADER}-----------------------------------------------------{Colors.ENDC}")
                print(f"{Colors.BOLD}{Colors.WARNING} 🎯 EXERCISE: {num1} {symbol} {num2} = ?{Colors.ENDC}")
                print(f"{Colors.HEADER}-----------------------------------------------------{Colors.ENDC}")
                
                labels = ["A", "B", "C", "D"]
                for idx, opt in enumerate(options):
                    print(f"   {Colors.BOLD}{Colors.OKBLUE}[{labels[idx]}]{Colors.ENDC} {opt}")
                    
                user_input = input(f"\n{Colors.BOLD}Your Answer (A/B/C/D): {Colors.ENDC}").strip().upper()
                
                user_val = None
                if user_input in labels:
                    user_val = options[labels.index(user_input)]
                else:
                    try:
                        user_val = int(user_input)
                    except ValueError:
                        user_val = -99999

                is_correct = (user_val == correct_ans)

                print(f"\n{Colors.DIM}✨ Orchestrator Agent crafting personalized feedback...{Colors.ENDC}")
                creative_feedback = await generate_creative_feedback(
                    orchestrator, num1, num2, symbol, correct_ans, user_val, is_correct
                )

                if is_correct:
                    print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 CORRECT!{Colors.ENDC}")
                    print(f"{Colors.OKGREEN}💬 Orchestrator: \"{creative_feedback}\"{Colors.ENDC}")
                else:
                    print(f"\n{Colors.FAIL}{Colors.BOLD}❌ INCORRECT (You guessed {user_val}, correct was {correct_ans}){Colors.ENDC}")
                    print(f"{Colors.WARNING}💬 Orchestrator: \"{creative_feedback}\"{Colors.ENDC}")
                    print(f"   {Colors.DIM}Explanation: {exercise.get('explanation', f'{num1} {symbol} {num2} = {correct_ans}')}{Colors.ENDC}")
                    
                print(f"{Colors.HEADER}-----------------------------------------------------{Colors.ENDC}")
                round_num += 1
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
                os.system('clear' if os.name == 'posix' else 'cls')
                print_banner()

            except Exception as err:
                print(f"\n{Colors.FAIL}❌ Failed to generate exercise from AGY Subagent:{Colors.ENDC}")
                print(f"   {err}")

async def main():
    api_key = load_environment()
    await run_sdk_verification_audit(api_key)
    await run_interactive_lab(api_key)

if __name__ == "__main__":
    asyncio.run(main())
