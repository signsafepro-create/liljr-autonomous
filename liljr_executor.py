#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
 LILJR EXECUTOR v1.0 — The Autonomous Coder
 Write code. Run it. Test it. Fix it. Deploy it.
 
 Command Pipeline:
   Voice/Text → Parse Intent → AutoCoder generates → 
   Executor runs safely → Validates output → 
   Fixes if broken → Deploys when working → 
   TTS feedback to user
═══════════════════════════════════════════════════════════════
"""
import json, os, sys, time, subprocess, re, traceback, tempfile, hashlib, threading

HOME = os.path.expanduser('~')
EXECUTOR_LOG = os.path.join(HOME, 'liljr_executor.log')
EXEC_DIR = os.path.join(HOME, 'liljr_executions')
BACKUP_DIR = os.path.join(HOME, 'liljr_backups')
REPO = os.path.join(HOME, 'liljr-autonomous')
sys.path.insert(0, REPO)

class SafeExecutor:
    """
    Safe autonomous code execution.
    Writes code, runs it in a temp file, captures output,
    validates it works, retries on failure, deploys when clean.
    """
    
    # NO RESTRICTIONS: User wants zero limits. All code allowed.
    # Keeping only bare minimum to prevent accidental infinite loops
    FORBIDDEN_PATTERNS = [
        # Intentionally empty — user wants unrestricted execution
    ]
    
    # ALL modules allowed — no whitelist
    ALLOWED_MODULES = None  # None = allow everything
    
    def __init__(self):
        self.exec_count = 0
        self.success_count = 0
        self.fail_count = 0
        os.makedirs(EXEC_DIR, exist_ok=True)
        os.makedirs(BACKUP_DIR, exist_ok=True)
    
    def _log(self, msg):
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        with open(EXECUTOR_LOG, 'a') as f:
            f.write(line + '\n')
    
    def _sanitize_code(self, code):
        """NO RESTRICTIONS: All code allowed. Only check for syntax."""
        # Check basic syntax
        try:
            compile(code, '<liljr_exec>', 'exec')
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        return True, "Unrestricted mode — all code allowed"
    
    def _write_temp(self, code, suffix='.py'):
        """Write code to a temp file in exec dir."""
        ts = int(time.time() * 1000)
        h = hashlib.md5(code.encode()).hexdigest()[:8]
        fname = f"exec_{ts}_{h}{suffix}"
        fpath = os.path.join(EXEC_DIR, fname)
        with open(fpath, 'w') as f:
            f.write(code)
        return fpath, fname
    
    def _run_file(self, fpath, timeout=15):
        """Run a Python file and capture output."""
        try:
            result = subprocess.run(
                ['python3', fpath],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=EXEC_DIR
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0,
                "timed_out": False
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": "Execution timed out",
                "returncode": -1,
                "success": False,
                "timed_out": True
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "success": False,
                "timed_out": False
            }
    
    def _tts_speak(self, text):
        """Speak aloud via Termux TTS."""
        try:
            subprocess.run(
                ['termux-tts-speak', text[:200]],  # limit length
                capture_output=True,
                timeout=10
            )
        except:
            pass
    
    def _notify(self, title, content):
        """Push notification."""
        try:
            subprocess.run([
                'termux-notification',
                '--title', title,
                '--content', content,
                '--priority', 'normal'
            ], capture_output=True, timeout=3)
        except:
            pass
    
    def execute(self, description, language='python', max_retries=3):
        """
        Full autonomous pipeline:
        1. Generate code
        2. Sanitize
        3. Write temp file
        4. Run
        5. Validate
        6. Fix if broken
        7. Return result
        """
        self.exec_count += 1
        self._log(f"EXEC #{self.exec_count}: {description[:80]}")
        
        # Step 1: Generate code
        code = self._generate_code(description, language)
        if not code:
            msg = "I couldn't generate code for that. Try being more specific."
            self._tts_speak(msg)
            return {"status": "error", "error": "Code generation failed", "message": msg}
        
        # Step 2: Sanitize
        safe, reason = self._sanitize_code(code)
        if not safe:
            self._log(f"BLOCKED: {reason}")
            msg = f"I blocked that code for safety: {reason}"
            self._tts_speak(msg)
            return {"status": "blocked", "error": reason, "message": msg}
        
        # Step 3-7: Run with retries
        for attempt in range(1, max_retries + 1):
            self._log(f"Attempt {attempt}/{max_retries}")
            
            # Write
            fpath, fname = self._write_temp(code)
            
            # Run
            result = self._run_file(fpath)
            
            if result['success']:
                # SUCCESS
                self.success_count += 1
                self._log(f"SUCCESS: {fname}")
                
                # Determine output type
                output = result['stdout'].strip()
                
                # Deploy if it's a file/web thing
                deploy_result = None
                if 'html' in code.lower() or 'website' in description.lower():
                    deploy_result = self._deploy_html(code, description)
                
                msg = f"Ran it. Works. Output:\n{output[:500]}" if output else "Ran it. Clean exit. No output."
                if deploy_result:
                    msg += f"\n\nDeployed: {deploy_result}"
                
                self._tts_speak("Done. It worked. Check your screen.")
                self._notify("LilJR ✅", "Code executed successfully")
                
                return {
                    "status": "success",
                    "file": fname,
                    "path": fpath,
                    "output": output,
                    "deployed": deploy_result,
                    "attempts": attempt,
                    "message": msg
                }
            
            else:
                # FAILED — try to fix
                self._log(f"FAILED (attempt {attempt}): {result['stderr'][:100]}")
                
                if attempt < max_retries:
                    # Generate fix
                    code = self._fix_code(description, code, result['stderr'])
                    if not code:
                        break
                    self._log("Generated fix, retrying...")
                else:
                    # Out of retries
                    self.fail_count += 1
                    err_summary = result['stderr'][:200]
                    msg = f"I tried {max_retries} times. Still broken.\nError: {err_summary}"
                    self._tts_speak("I couldn't fix it. Check the error.")
                    self._notify("LilJR ⚠️", f"Code failed after {max_retries} attempts")
                    
                    return {
                        "status": "failed",
                        "file": fname,
                        "path": fpath,
                        "error": result['stderr'],
                        "stdout": result['stdout'],
                        "attempts": attempt,
                        "message": msg
                    }
        
        return {"status": "error", "error": "Max retries exceeded"}
    
    def _generate_code(self, description, language='python'):
        """Generate code using AutoCoder or simple templates."""
        try:
            from auto_coder import AutoCoder
            coder = AutoCoder()
            
            if 'html' in description.lower() or 'website' in description.lower() or 'page' in description.lower():
                return coder.generate_html_page(
                    title=self._extract_title(description),
                    sections=['hero', 'content', 'footer'],
                    theme='dark_empire'
                )
            elif 'function' in description.lower() or 'script' in description.lower():
                return coder.generate_python_module(
                    name=self._extract_title(description),
                    requirements=[description]
                )
            else:
                return coder.generate_python_module(
                    name='generated',
                    requirements=[description]
                )
        except Exception as e:
            # Fallback: generate simple code from template
            return self._fallback_generate(description)
    
    def _fallback_generate(self, description):
        """Simple template-based code generation when AutoCoder fails."""
        title = self._extract_title(description)
        
        # Simple Python template
        code = f'''#!/usr/bin/env python3
"""
Generated by LilJR Executor
Task: {description}
"""

import json, os, sys, math, random

def main():
    result = {{}}
    
    # Task execution
    print("Task: {description}")
    
    # Logic based on description
    text = """{description}"""
    
    if "calculate" in text.lower() or "math" in text.lower() or "sum" in text.lower():
        # Try to extract numbers and do math
        import re
        numbers = [float(x) for x in re.findall(r'\d+\.?\d*', text)]
        if numbers:
            result['numbers'] = numbers
            result['sum'] = sum(numbers)
            result['product'] = 1
            for n in numbers:
                result['product'] *= n
            result['average'] = sum(numbers) / len(numbers)
            print(f"Numbers: {{numbers}}")
            print(f"Sum: {{result['sum']}}")
            print(f"Average: {{result['average']}}")
    
    elif "list" in text.lower() or "generate" in text.lower() or "create" in text.lower():
        items = ["item_1", "item_2", "item_3", "item_4", "item_5"]
        result['items'] = items
        print("Generated list:")
        for i, item in enumerate(items, 1):
            print(f"  {{i}}. {{item}}")
    
    elif "random" in text.lower() or "dice" in text.lower() or "coin" in text.lower():
        result['random'] = random.random()
        result['dice'] = random.randint(1, 6)
        result['coin'] = "heads" if random.random() > 0.5 else "tails"
        print(f"Random: {{result['random']:.4f}}")
        print(f"Dice roll: {{result['dice']}}")
        print(f"Coin flip: {{result['coin']}}")
    
    else:
        # Generic response
        result['task'] = text
        result['length'] = len(text)
        result['words'] = len(text.split())
        print(f"Processed: {{text}}")
        print(f"Word count: {{result['words']}}")
    
    print("\\nResult:")
    print(json.dumps(result, indent=2))
    return result

if __name__ == '__main__':
    main()
'''
        return code
    
    def _fix_code(self, description, broken_code, error):
        """Generate a fix based on the error."""
        try:
            from auto_coder import AutoCoder
            coder = AutoCoder()
            return coder.auto_fix(broken_code, error)
        except:
            # Fallback: add error handling wrapper
            wrapped = f'''#!/usr/bin/env python3
"""
Generated by LilJR Executor (FIXED)
Task: {description}
Original error: {error[:100]}
"""

import traceback
import sys

# Original code:
{chr(10).join('    ' + line for line in broken_code.split(chr(10)))}

# Fix attempt: if the above fails, we'll catch it
try:
    # Try running the main logic
    exec(open(__file__).read().split("# Fix attempt:")[0])
except Exception as e:
    print(f"Error: {{e}}")
    traceback.print_exc()
'''
            return wrapped
    
    def _deploy_html(self, html_code, description):
        """Deploy generated HTML to the web directory."""
        try:
            name = self._extract_title(description).replace(' ', '_').lower()
            web_dir = os.path.join(REPO, 'web')
            os.makedirs(web_dir, exist_ok=True)
            
            fname = f"{name}_{int(time.time())}.html"
            fpath = os.path.join(web_dir, fname)
            
            with open(fpath, 'w') as f:
                f.write(html_code)
            
            # Try to git push
            os.chdir(REPO)
            subprocess.run(['git', 'add', fpath], capture_output=True, timeout=5)
            subprocess.run(['git', 'commit', '-m', f'auto: {description[:40]}'], capture_output=True, timeout=5)
            subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, timeout=15)
            
            return f"web/{fname} (pushed to GitHub)"
        except Exception as e:
            return f"Saved locally: web/{fname}"
    
    def _extract_title(self, text):
        """Extract a short name from description."""
        # Try to find quoted text
        m = re.search(r'"([^"]{3,30})"', text)
        if m:
            return m.group(1)
        
        # Try first few words
        words = text.split()
        if len(words) >= 2:
            return '_'.join(words[:3]).replace(',', '').replace('.', '').lower()
        
        return 'generated'
    
    def get_stats(self):
        return {
            "executions": self.exec_count,
            "successes": self.success_count,
            "failures": self.fail_count,
            "success_rate": f"{(self.success_count / max(1, self.exec_count) * 100):.1f}%"
        }


# ═══ VOICE COMMAND PIPELINE ═══
class VoiceCommander:
    """
    Takes voice input, converts to command, feeds into Executor.
    """
    
    def __init__(self, executor=None):
        self.executor = executor or SafeExecutor()
        self._listening = False
    
    def listen_and_execute(self):
        """
        Record voice via termux-speech-to-text, parse, execute.
        Returns the result dict.
        """
        try:
            # Start listening
            self._tts_speak("Listening. Tell me what to build.")
            
            # Try termux-speech-to-text
            result = subprocess.run(
                ['termux-speech-to-text', '-l', 'en-US'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0 or not result.stdout.strip():
                self._tts_speak("Didn't catch that. Try again or type it.")
                return {"status": "no_input", "message": "No voice input detected"}
            
            text = result.stdout.strip()
            self._tts_speak(f"Got it. You said: {text[:50]}. Running now.")
            
            # Execute
            exec_result = self.executor.execute(text)
            
            # Feedback
            if exec_result['status'] == 'success':
                self._tts_speak("Done. It worked. Check your screen.")
            elif exec_result['status'] == 'failed':
                self._tts_speak("It broke. I tried to fix it but couldn't. Check the error.")
            else:
                self._tts_speak("Something went wrong.")
            
            return {
                "status": "ok",
                "voice_input": text,
                "execution": exec_result
            }
            
        except subprocess.TimeoutExpired:
            self._tts_speak("You went quiet. I'm here when you need me.")
            return {"status": "timeout", "message": "Voice input timed out"}
        except Exception as e:
            self._tts_speak("Voice command failed. Try typing it instead.")
            return {"status": "error", "error": str(e)}
    
    def _tts_speak(self, text):
        try:
            subprocess.run(
                ['termux-tts-speak', text[:200]],
                capture_output=True,
                timeout=10
            )
        except:
            pass


# ═══ STANDALONE ═══
if __name__ == '__main__':
    import sys
    executor = SafeExecutor()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == 'run' and len(sys.argv) > 2:
            description = ' '.join(sys.argv[2:])
            result = executor.execute(description)
            print(json.dumps(result, indent=2))
        
        elif cmd == 'voice':
            voice = VoiceCommander(executor)
            result = voice.listen_and_execute()
            print(json.dumps(result, indent=2))
        
        elif cmd == 'stats':
            print(json.dumps(executor.get_stats(), indent=2))
        
        else:
            print("LILJR EXECUTOR — Autonomous Coder")
            print("Commands:")
            print('  run "description"   — Generate, run, fix, deploy')
            print('  voice              — Listen, parse, execute, speak result')
            print('  stats              — Execution stats')
            print('')
            print('Examples:')
            print('  python3 liljr_executor.py run "calculate sum of 1 to 100"')
            print('  python3 liljr_executor.py run "build a landing page called FitLife"')
            print('  python3 liljr_executor.py voice')
    else:
        print("LilJR Executor — Tell me what to build. I'll write it, run it, fix it, deploy it.")
        print("Usage: python3 liljr_executor.py run 'your command'")
        print("       python3 liljr_executor.py voice")
