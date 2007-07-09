import inspect

"""
Rough first pass at shard constructor: aims to treat shard objects,
named functions and lists of strings (code) equivalently

Current thought is to subclass shard to create Connectors,
e.g. ifshard(shard) can construct if-statements as shards,
functionshard(shard) can replace the current makefunction, etc.
Would replace the more '2-stage' approaches so far by making
everything a shard from import.

TODO:
check indentation defaults are sensible
"""

def namegen(name = 'shard'):
        """
        Generates names for anonymous shards
        """
        
        i = 0
        while True:
            yield name+str(i)
            i += 1
    
def iscode(c):
    """
    Tests if argument type could be lines of code,
    i.e. list of strings
    """
    if type(c) == type([]):
        return type(c[0]) == type('') if c else True
    else: return False
    
def isfunction(f):
    """
    Tests if argument is a function
    """
    
    return callable(f)


indentation = "    "
nl = "\n"

class shard(object):
    namer = namegen()
    
    def __init__(self, name = None, indent = 0, annotate = False, function = None, code = None, shards = []):
        """
        Initialisation to create shards from lines of code, existing functions,
        or a combination of these and existing shard objects
        
        Arguments:
        name = name of new shard, default None. If no name is specified
                     a default name will be generated (except where shard is
                     created from a single function, where the function's name
                     will be used)
        indent = level of indentation to add to imported code, default 0
        annotate = whether to add annotations for imported code into
                           new shard's generated code, default False
        function = if shard is being made from a single function, it can be
                         entered here. Used mainly internally to initialise function
                         objects passed into *shards. If present, any following
                         arguments are ignored, default is None
        code = as function, but if initialisation is for single code block
        shards = the shards that will compose the body of the new shard,
                       in the order in which they will be added. Arguments here
                       can be any combination of existing shard objects, function
                       objects, and lists of code lines (e.g. as imported by
                       getshard); these will be initialised as necessary
        
        Returns:
        shard object containing the name and code of the new shard
        """
        
        super(shard, self).__init__()
        
        self.indent = indent
        # need to indent generated code
        if function:
            self.name = function.func_name
            self.code = self.addindent(self.getshard(function), indent)
        elif code:
            self.name = name if name else self.namer.next()
            self.code = self.addindent(code, indent)
        else:
            self.name = name if name else self.namer.next()
            self.code = []
            for s in shards:
                if isfunction(s):
                    s = shard(function = s)
                elif iscode(s):
                    s = shard(name = name, code = s)
                
                self.code += self.addindent(s.annotate() if annotate else s.code, indent)
    
    
    def getshard(self, function):
        """
        Gets shard code for generation
        
        Arguments:
        function = shard function to get
        
        Returns:
        list of lines of code, indented as specified
        """
        
        # get code, throwaway def line
        lines = inspect.getsource(function).splitlines(True)[1:]
        
        # remove any whitespace lines at start
        while lines[0].isspace(): lines.pop(0)
        
        # remove docstrings
        doctag = r'"""'
        while True:
            if lines[0].count(doctag) % 2 == 1:
                lines.pop(0)                            # remove line with opening doctag
                while lines[0].count(doctag) % 2 == 0:
                    lines.pop(0)                        # remove lines till tag match
                lines.pop(0)                            # remove matching tag
            
            if lines[0].count(doctag) == 0:
                break                                     # no docstring, start of code
            else:                                          # docstring tags closed, continue till code line found
                lines.pop(0)
        
        return [c[len(lines[0]) - len(lines[0].lstrip()):] for c in lines] # remove leading indentation
    
    
    def annotate(self, delimchar = '-'):
        """
        Marks out start and end of shard code with comments
        
        Arguments:
        delimchar = single character string containing character to be used
                            in marking out shard limit across the page
        
        Returns:
        list of lines of code surrounded by delimiter comments as specified
        """
        
        start = r"# START SHARD: " + self.name + " "
        start = self.addindent([start], self.indent)[0]
        start = start.ljust(80, delimchar) + nl
        
        end = r"# END SHARD: " + self.name + " "
        end = self.addindent([end], self.indent)[0]
        end = end.ljust(80, delimchar) + nl
        
        return [start] + self.code + [end] + [nl]
    
    
    def addindent(self, lines = None, level = 1):
        """
        Indents code with spaces
        
        Arguments:
        level = number of levels to be indented, defaults to 1
        
        Returns:
        object's code attribute prefixed by specified amount of whitespace
        """
        if lines == None:
            lines = self.code
        
        if level < 0: # remove indentation
            level = -level
            return [ line[len(indentation*level):] for line in lines ]
        
        elif level == 0:
            return lines
        
        elif level > 0: # add indentation
            return [indentation*level + line for line in lines]
