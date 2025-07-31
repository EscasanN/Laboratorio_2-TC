import os

def tokenize(regex):
    tokens = []
    i = 0
    while i < len(regex):
        c = regex[i]
        if c == '\\':  # escape sequence
            if i + 1 < len(regex):
                tokens.append(regex[i : i + 2])
                i += 2
            else:
                tokens.append(c)
                i += 1
        elif c == '[':  # character class
            j = i + 1
            while j < len(regex) and regex[j] != ']':
                if regex[j] == '\\' and j + 1 < len(regex):
                    j += 2
                else:
                    j += 1
            if j < len(regex) and regex[j] == ']':
                tokens.append(regex[i : j + 1])
                i = j + 1
            else:
                tokens.append(regex[i:])
                break
        elif c in {'(', ')', '|', '*', '+', '?'}:
            tokens.append(c)
            i += 1
        else:
            tokens.append(c)
            i += 1
    return tokens

def pop_prev_atom(lst):
    if not lst:
        raise ValueError("No previous atom to pop")
    if lst[-1] == ')':
        depth = 1
        j = len(lst) - 2
        while j >= 0:
            if lst[j] == ')':
                depth += 1
            elif lst[j] == '(':
                depth -= 1
                if depth == 0:
                    atom = lst[j:]
                    del lst[j:]
                    return atom
            j -= 1
        raise ValueError("Unmatched parenthesis in expansion")
    else:
        return [lst.pop()]

def expand_plus_question(tokens):
    new_tokens = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == '+':
            atom = pop_prev_atom(new_tokens)
            # X+ -> X X*
            new_tokens.extend(atom)
            new_tokens.extend(atom)
            new_tokens.append('*')
            i += 1
        elif tok == '?':
            atom = pop_prev_atom(new_tokens)
            # X? -> (X|ε)
            new_tokens.append('(')
            new_tokens.extend(atom)
            new_tokens.append('|')
            new_tokens.append('ε')
            new_tokens.append(')')
            i += 1
        else:
            new_tokens.append(tok)
            i += 1
    return new_tokens

def insert_concatenation(tokens):
    result = []
    def is_atom(t):
        if t == 'ε':
            return True
        if t.startswith('\\'):
            return True
        if t.startswith('[') and t.endswith(']'):
            return True
        if t not in {'|', '(', ')', '*', '·'}:
            return True
        return False

    for i, tok in enumerate(tokens):
        result.append(tok)
        if i + 1 < len(tokens):
            t1 = tok
            t2 = tokens[i + 1]
            if (
                (is_atom(t1) or t1 == ')' or t1 == '*')
                and (is_atom(t2) or t2 == '(')
            ):
                result.append('·')  # concatenación explícita
    return result

def shunting_yard(tokens):
    output = []
    stack = []

    prec = {'|': 1, '·': 2, '*': 3}
    assoc = {'|': 'left', '·': 'left', '*': 'left'}

    for tok in tokens:
        if tok == ' ' or tok == '':
            continue
        if tok.startswith('\\') or (tok.startswith('[') and tok.endswith(']')) or tok == 'ε' or (tok not in {'|', '·', '*', '(', ')'}):
            output.append(tok)
        elif tok in {'|', '·', '*'}:
            while stack and stack[-1] != '(' and (
                (assoc[tok] == 'left' and prec[stack[-1]] >= prec[tok]) or
                (assoc[tok] == 'right' and prec[stack[-1]] > prec[tok])
            ):
                popped = stack.pop()
                output.append(popped)
            stack.append(tok)
        elif tok == '(':
            stack.append(tok)
        elif tok == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack and stack[-1] == '(':
                stack.pop()
            else:
                raise ValueError("Mismatched parentheses")
        else:
            raise ValueError(f"Unknown token '{tok}'")
    while stack:
        popped = stack.pop()
        if popped in {'(', ')'}:
            raise ValueError("Mismatched parentheses in final cleanup")
        output.append(popped)
    return output, []

def process_regex_line(line):
    original = line.strip()
    if not original:
        return {}
    tokens = tokenize(original)
    expanded = expand_plus_question(tokens)
    with_concat = insert_concatenation(expanded)
    postfix, _ = shunting_yard(with_concat)
    return {
        "original": original,
        "postfix": postfix,
    }

#Ejecucion del programa

def main():
    path = "expressions.txt"
    if not os.path.isfile(path):
        print(f"Archivo '{path}' no encontrado.")
        return
    with open(path, encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f if ln.strip()]
    for line in lines:
        try:
            res = process_regex_line(line)
            print(f"Infix: {res['original']}")
            print(f"Postfix: {' '.join(res['postfix'])}")
            print("-" * 60)
        except Exception as e:
            print(f"Error procesando '{line}': {type(e).__name__}: {e}")
            if line.startswith(r"if\("):
                print("  -> Revisa la ambigüedad en los escapes/agrupaciones de esa expresión.")

if __name__ == "__main__":
    main()
