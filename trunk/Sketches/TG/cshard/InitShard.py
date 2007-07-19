from FunctionShard import functionShard

class initShard(functionShard):
    
    def __init__(self, clsname, args = [], kwargs = {}, exarg = None,
                        exkwarg = None, docstring = '', shards = []):
        superinit = ["super(" + clsname+", self).__init__()\n"]
        
        super(initShard, self).__init__(funcname = '__init__', indent = 0, args = ['self']+ args,
                                           kwargs = kwargs, exarg = exarg, exkwarg = exkwarg,
                                           docstring = docstring, shards = [superinit] + shards)