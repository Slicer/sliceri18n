import ast

def walk (node):
    """ast.walk() skips the order, just walks, so tracing is not possible with it."""
    end = []
    end.append(node)
    for n in ast.iter_child_nodes(node):
        # Consider it a leaf:
        if isinstance(n, ast.Call) and n.func.id=="_":
            end.append(n)
            continue
        end += walk(n)
    return end

def calls (tree):
    """Prints out exactly where are the calls and what functions are called."""
    tree = walk(tree) # Arrange it into our list
    # First get all functions in our code:
    functions = {}
    for node in tree:
        # if isinstance(node, (ast.FunctionDef, ast.Lambda)):
        if isinstance(node, ast.Call):
          if node.func.id == "_": #mako modifié
            functions[node.func.id] = node
    # Find where are all called functions:
    stack = []
    for node in tree:
        if isinstance(node, (ast.FunctionDef, ast.Lambda)):
            # Entering function
            stack.append(node)
        elif stack and hasattr(node, "col_offset"):
            if node.col_offset<=stack[-1].col_offset:
                # Exit the function
                stack.pop()
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                fname = node.func.value.id+"."+node.func.attr+"()"
            else: fname = node.func.id+"()"
            print ("Line", node.lineno, "--> Call to", fname)
            if stack:
                print ("from within", stack[-1].name+"()", "that starts on line", stack[-1].lineno)
            else:
                print ("directly from root")

code = """
def _(text):
  return text
print (_("test function call"))
print (_("test function call"))
note = _("test")
"""

tree = ast.parse(code)

calls(tree)