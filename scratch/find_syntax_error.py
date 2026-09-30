import ast

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1, len(lines)):
    try:
        content = "".join(lines[:i])
        # Add dummy pass or matching indent block if needed
        # Just compile to see where it breaks first
        compile(content, 'app.py', 'exec')
    except SyntaxError as e:
        print(f"First syntax error at line {e.lineno}: {e.msg}")
        print(f"Line content: {lines[e.lineno-1]}")
        break
