#!/usr/bin/python
#
# This program generates Kamaelia's documentation directly from the
# source. I am currently running this as follows:
#
# mkdir ./pydoc/
# ./DocExtractor.py
#
# documentation is placed into the "pydoc" subdirectory

import textwrap
import inspect
import pprint
import time
from docutils import core
from docutils import nodes
#import Kamaelia.Support.Data.Repository
import Repository


from renderHTML      import RenderHTML
from renderPlaintext import RenderPlaintext

from Nodes import boxright

class DocGenConfig(object):
    """Configuration object for documentation generation."""
    def __init__(self):
        super(DocGenConfig,self).__init__()
        # NOTE: These settings are overridden in __main__ - modify them there,
        #       not here
        self.repository = None
        self.debug=False
        self.filterPattern=""
        self.docdir="pydoc"
        self.docroot="Kamaelia"
        self.treeDepth=99
        self.tocDepth=99
        self.includeMethods=False
        self.includeModuleDocString=False
        self.includeNonKamaeliaStuff=False
        self.showComponentsOnIndices=False
        self.promoteModuleTitles=False
        self.deemphasiseTrails=False
        self.pageFooter=""

class docFormatter(object):
    def __init__(self, renderer=RenderPlaintext, config=DocGenConfig(), debug=False):
        super(docFormatter,self).__init__()
        self.renderer = renderer
        self.debug = debug
        self.config = config

    uid = 0

    def genUniqueRef(self):
        uid = str(self.uid)
        self.uid+=1
        return uid

    def boxes(self,componentName, label, boxes):
        items = []
        for box in boxes:
            try:
                description = boxes[box]
            except KeyError:
                description = ""
            except TypeError:
                description = "Code uses old style inbox/outbox description - no metadata available"
            items.append((str(box), str(description)))

        docTree= nodes.section('',
                ids   = ["component-"+componentName+"-"+label],
                names = ["component-"+componentName+"-"+label],
                *[ nodes.title('', label),
                   nodes.bullet_list('',
                      *[ nodes.list_item('', nodes.paragraph('', '',
                                                 nodes.strong('', boxname),
                                                 nodes.Text(" : "+boxdesc))
                                             )
                         for (boxname,boxdesc) in items
                       ]
                   ),
                ]
            )
        return docTree
    
    def docString(self,docstring, main=False):
        if docstring is None:
            docstring = " "
        lines = docstring.split("\n")
        if len(lines)>1:
            line1 = textwrap.dedent(lines[0])
            rest = textwrap.dedent("\n".join(lines[1:]))
            docstring = line1+"\n"+rest
        else:
            docstring=textwrap.dedent(docstring)

        while len(docstring)>0 and docstring[0] == "\n":
            docstring = docstring[1:]
        while len(docstring)>0 and docstring[-1] == "\n":
            docstring = docstring[:-1]
            
        return nodes.section('', *core.publish_doctree(docstring).children)

    def formatArgSpec(self, argspec):
        return pprint.pformat(argspec[0]).replace("[","(").replace("]",")").replace("'","")

    def formatMethodDocStrings(self,X):
        docTree = nodes.section('') #self.emptyTree()
        
        methods = X.methods
        methods.sort()
        
        
        for method in methods:
            methodHead = method.name + "(" + method.argString + ")"
            
            docTree.append( nodes.section('',
                                ids   = ["component-"+X.name+"-method-"+method.name],
                                names = ["component-"+X.name+"-method-"+method.name],
                                * [ nodes.title('', methodHead) ]
                                  + self.docString(method.docString)
                            )
                          )

        return docTree

    def formatClassStatement(self, name, bases):
        return "class "+ name+"("+",".join([str(base)[8:-2] for base in bases])+")"
    
    def formatPrefabStatement(self, name):
        return "prefab: "+name
    
    def formatComponent(self, X):
        # no class bases available from repository scanner 
        CLASSNAME = self.formatClassStatement(X.name, []) #X.__bases__)
        CLASSDOC = self.docString(X.docString)
        INBOXES = self.boxes(X.name,"Inboxes", X.inboxes)
        OUTBOXES = self.boxes(X.name,"Outboxes", X.outboxes)
        
        if self.config.includeMethods and len(X.methods):
            METHODS = [ nodes.section('',
                          nodes.title('', 'Methods defined here'),
                          boxright('',
                              nodes.paragraph('', '',
                                  nodes.strong('', nodes.Text("Warning!"))
                              ),
                              nodes.paragraph('', '',
                                  nodes.Text("You should be using the inbox/outbox interface, not these methods (except construction). This documentation is designed as a roadmap as to their functionalilty for maintainers and new component developers.")
                              ),
                          ),
                          * self.formatMethodDocStrings(X)
                        )
                      ]
        else:
            METHODS = []
            
        return \
                nodes.section('',
                * [ nodes.title('', CLASSNAME, ids=["component-"+X.name]) ]
                  + CLASSDOC
                  + [ INBOXES, OUTBOXES ]
                  + METHODS
                )
        
    def formatPrefab(self, X):
        CLASSNAME = self.formatPrefabStatement(X.name)
        CLASSDOC = self.docString(X.docString)
        
        return nodes.section('',
                * [ nodes.title('', CLASSNAME, ids=["component-"+X.name]) ]
                  + CLASSDOC
            )
        
    def formatFunction(self, X):
        functionHead = X.name + "(" + X.argString + ")"
        return nodes.section('',
                    ids   = ["function-"+X.name],
                    names = ["function-"+X.name],
                    * [ nodes.title('', functionHead) ]
                        + self.docString(X.docString)
                    )
                            

    def formatClass(self, X):
        # no class bases available from repository scanner 
        CLASSNAME = self.formatClassStatement(X.name, []) #X.__bases__)

        if len(X.methods)>0:
            METHODS = [ nodes.section('',
                            nodes.title('', 'Methods defined here'),
                            * self.formatMethodDocStrings(X)
                        )
                      ]
        else:
            METHODS = []
        return \
                nodes.section('',
                    nodes.title('', CLASSNAME, ids=["class-"+X.name]),
                    self.docString(X.docString),
                    *METHODS
                )
        
    def formatTrail(self, moduleName):
        path = moduleName.split(".")
        
        trail = nodes.paragraph('')
        line = trail
        
        accum = ""
        firstPass=True
        for element in path:
            if not firstPass:
                accum += "."
            accum += element
            
            if not firstPass:
                line.append(nodes.Text("."))
            URI = self.renderer.makeURI(accum)
            line.append( nodes.reference('', element, refuri=URI) )
            
            firstPass=False
        
        return trail

    def formatTrailAsTitle(self, moduleName):
        trailTree = self.formatTrail(moduleName)
        title = nodes.title('', '', *trailTree.children)
        if self.config.deemphasiseTrails:
            title = nodes.section('', title)

        return title
        
    def componentList(self, components):
        uris = {}
        for component in components:
            fullname = component.module + "." + component.name
            uris[component.name] = self.renderer.makeURI(fullname)

        componentNames = uris.keys()
        componentNames.sort()
        
        return nodes.container('',
            nodes.bullet_list('',
                *[ nodes.list_item('',
                       nodes.paragraph('', '',
                         nodes.strong('', '',
                           nodes.reference('', NAME, refuri=uris[NAME]))
                         )
                       )
                   for NAME in componentNames
                 ]
                )
            )

    def formatComponentPage(self,moduleName, component):
        return self.formatDeclarationPage(moduleName, self.formatComponent, component)
        
    def formatPrefabPage(self,moduleName, prefab):
        return self.formatDeclarationPage(moduleName, self.formatPrefab, prefab)
        
    def formatClassPage(self,moduleName, cls):
        return self.formatDeclarationPage(moduleName, self.formatClass, cls)
        
    def formatFunctionPage(self,moduleName, function):
        return self.formatDeclarationPage(moduleName, self.formatFunction, function)
        
    def formatDeclarationPage(self, name, method, arg):
        parentURI = self.renderer.makeURI(".".join(name.split(".")[:-1]))
        trailTitle = self.formatTrailAsTitle(name)
        
        declarationTree = method(arg)
        
        return nodes.section('',
            trailTitle,
            nodes.paragraph('', '',
                nodes.Text("For examples and more explanations, see the "),
                nodes.reference('', 'module level docs.', refuri=parentURI)
                ),
            nodes.transition(),
            nodes.section('', *declarationTree),
            )
           
    def formatModule(self, moduleName, module, components, prefabs, classes, functions):
        
        trailTitle = self.formatTrailAsTitle(moduleName)
        moduleTree = self.docString(module.docString, main=True)
        
        if self.config.promoteModuleTitles and \
           len(moduleTree.children)>=1 and \
           isinstance(moduleTree.children[0], nodes.title):
            theTitle = moduleTree.children[0]
            moduleTree.remove(theTitle)
            promotedTitle = [ theTitle ]
        else:
            promotedTitle = []

        toc = self.buildTOC(moduleTree, depth=self.config.tocDepth)
        
        allDeclarations = []
        
        declarationTrees = {}
        for component in components:
            cTrail = self.formatTrail(moduleName+"."+component.name)
            declarationTrees[component.name] = nodes.container('',
                nodes.title('','', *cTrail.children),
                    self.formatComponent(component)
            )
            
        for prefab in prefabs:
            assert(prefab.name not in declarationTrees)
            pTrail = self.formatTrail(moduleName+"."+prefab.name)
            declarationTrees[prefab.name] = nodes.container('',
                nodes.title('','', *pTrail.children),
                    self.formatPrefab(prefab)
            )

        for cls in classes:
            assert(cls.name not in declarationTrees)
            cTrail = self.formatTrail(moduleName+"."+cls.name)
            declarationTrees[cls.name] = nodes.container('',
                nodes.title('','', *cTrail.children),
                    self.formatClass(cls)
            )

        for function in functions:
            assert(function.name not in declarationTrees)
            fTrail = self.formatTrail(moduleName+"."+function.name)
            declarationTrees[function.name] = nodes.container('',
                nodes.title('','', *fTrail.children),
                    self.formatFunction(function)
            )

        declNames = declarationTrees.keys()
        declNames.sort()
        for name in declNames:
            allDeclarations.extend(declarationTrees[name])
        
        componentListTree = self.componentList( components + prefabs + classes + functions )

        return nodes.container('',
            nodes.section('',
                trailTitle,
                ),
            nodes.section('',
                * promotedTitle + \
                  [ componentListTree,
                    toc,
                  ]
            ),
            nodes.transition(),
            moduleTree,
            nodes.transition(),
            nodes.section('', *allDeclarations),
            )
            
    def buildTOC(self, srcTree, parent=None, depth=None):
        """Recurse through a source document tree, building a table of contents"""
        if parent is None:
            parent = nodes.bullet_list()

        if depth==None:
            depth=self.config.tocDepth
            
        if depth<=0:
            return parent

        items=nodes.section()
        
        for n in srcTree.children:
            if isinstance(n, nodes.title):
                refid = self.genUniqueRef()
                n.attributes['ids'].append(refid)
                newItem = nodes.list_item()
                newItem.append(nodes.paragraph('','', nodes.reference('', refid=refid, *n.children)))
                newItem.append(nodes.bullet_list())
                parent.append(newItem)
            elif isinstance(n, nodes.section):
                if len(parent)==0:
                    newItem = nodes.list_item()
                    newItem.append(nodes.bullet_list())
                    parent.append(newItem)
                self.buildTOC( n, parent[-1][-1], depth-1)

        # go through parent promoting any doubly nested bullet_lists
        for item in parent.children:
            if isinstance(item.children[0], nodes.bullet_list):
                sublist = item.children[0]
                for subitem in sublist.children[:]:   # copy it so it isn't corrupted by what we're about to do
                    sublist.remove(subitem)
                    item.parent.insert(item.parent.index(item), subitem)
                parent.remove(item)
                
            
        return parent
        

    def formatIndex(self, path, subTree): #indexName, subTree, componentsAndPrefabs):
        depth=self.config.treeDepth

        indexName = ".".join(path)

        trailTitle = self.formatTrailAsTitle(indexName)
        
        moduleTree = nodes.container('')
        if self.config.includeModuleDocString:
            if subTree.has_key("__init__"):
                docs = subTree["__init__"].docString
                if docs and ("This is a doc string" not in docs):
                    moduleTree =self.docString(docs)

        if self.config.promoteModuleTitles and \
           len(moduleTree.children)>=1 and \
           isinstance(moduleTree.children[0], nodes.title):
            theTitle = moduleTree.children[0]
            moduleTree.remove(theTitle)
            promotedTitle = [ theTitle ]
        else:
            promotedTitle = []

        return nodes.section('',
            * [ trailTitle ]
            + promotedTitle
            + [ self.generateIndex(path, subTree, depth=depth) ]
            + [ moduleTree ]
            )

    def generateIndex(self, path, srcTree, parent=None, depth=99):
        if parent is None:
            parent = nodes.bullet_list()

        if depth<=0:
            return parent

        items=nodes.section()

        childNames = srcTree.keys()
        childNames.sort()
        for name in [c for c in childNames if c != "__init__"]:
            moduleContents = []
            
            modPath = tuple(list(path)+[name])
            modName = ".".join(modPath)

            if self.config.repository.flatModules.has_key(modPath):
                thisMod = self.config.repository.flatModules[modPath]
                
                # build "(a,b,c)" style list of links to actual components/prefabs in the module
                # (if they exist)
                if self.config.showComponentsOnIndices:
                    declNames = [_.name for _ in thisMod.components + thisMod.prefabs]
                    if len(declNames)>0:
                        moduleContents.append(nodes.Text(" ( "))
                        first=True
                        for declName in declNames:
                            if not first:
                                moduleContents.append(nodes.Text(", "))
                            first=False
                            uri = self.renderer.makeURI(modName+"."+declName)
                            linkToDecl = nodes.reference('', nodes.Text(declName), refuri=uri)
                            moduleContents.append(linkToDecl)
                        moduleContents.append(nodes.Text(" )"))

            # now make the list item for this module
            uri = self.renderer.makeURI(modName)
            text = name
            newItem = nodes.list_item('',
                nodes.paragraph('','',
                    nodes.strong('', '',nodes.reference('', text, refuri=uri)),
                    *moduleContents
                    )
                )
                
            if isinstance(srcTree[name],dict):  # if not empty, recurse
                newItem.append(nodes.bullet_list())
                self.generateIndex(modPath, srcTree[name], newItem[-1], depth-1)
            parent.append(newItem)

        return parent

#    def postscript(self):
#        return self.config.pageFooter.deepcopy()
#        return self.docString("""\
#            Feedback
#            --------
#            Got a problem with the documentation? Something unclear that could be clearer?
#            Want to help improve it? Constructive criticism is very welcome! (preferably in
#            the form of suggested rewording)
#            
#            Please leave you feedback
#            `here <http://kamaelia.sourceforge.net/cgi-bin/blog/blog.cgi?rm=viewpost&nodeid=1142023701>`_
#            in reply to the documentation thread in the Kamaelia blog.
#            """)
            
            
def generateDocumentationFiles(formatter, CONFIG):
    
    MODULES = [ K for K in CONFIG.repository.flatModules.keys() \
                if CONFIG.filterPattern in ".".join(K) ]
    for MODULE in MODULES:
        moduleName = ".".join(MODULE)
        print "Processing: "+moduleName

        module     = CONFIG.repository.flatModules[MODULE]
        components = module.components
        prefabs    = module.prefabs
        if CONFIG.includeNonKamaeliaStuff:
            classes    = module.classes
            functions  = module.functions
        else:
            classes = []
            functions = []
        
        doctree  = formatter.formatModule(moduleName, module, components, prefabs, classes, functions)
        filename = formatter.renderer.makeFilename(moduleName)
        output   = formatter.renderer.render(moduleName, doctree)
        
        F = open(CONFIG.docdir+"/"+filename, "w")
        F.write(output)
        F.close()
        
        for component in components:
            NAME = moduleName+"."+component.name
            print "    Component: "+NAME
            filename = formatter.renderer.makeFilename(NAME)
            doctree = formatter.formatComponentPage(NAME, component)
            output   = formatter.renderer.render(NAME, doctree)
            F = open(CONFIG.docdir+"/"+filename, "w")
            F.write(output)
            F.close()

        for prefab in prefabs:
            NAME = moduleName+"."+prefab.name
            print "    Prefab: "+NAME
            filename = formatter.renderer.makeFilename(NAME)
            doctree = formatter.formatPrefabPage(NAME, prefab)
            output   = formatter.renderer.render(NAME, doctree)
            F = open(CONFIG.docdir+"/"+filename, "w")
            F.write(output)
            F.close()
            
        for cls in classes:
            NAME = moduleName+"."+cls.name
            filename = formatter.renderer.makeFilename(NAME)
            doctree = formatter.formatClassPage(NAME, cls)
            output = formatter.renderer.render(NAME, doctree)
            F = open(CONFIG.docdir+"/"+filename, "w")
            F.write(output)
            F.close()

        for function in functions:
            NAME = moduleName+"."+function.name
            filename = formatter.renderer.makeFilename(NAME)
            doctree = formatter.formatFunctionPage(NAME, function)
            output = formatter.renderer.render(NAME, doctree)
            F = open(CONFIG.docdir+"/"+filename, "w")
            F.write(output)
            F.close()

def generateIndices(formatter, CONFIG):

    def generate(formatter, CONFIG, subtree, path):
        if path != []:
            indexName = ".".join(path)
            print "Creating index: "+indexName
            
            doctree  = formatter.formatIndex(path,subtree)
            filename = formatter.renderer.makeFilename(indexName)
            output   = formatter.renderer.render(indexName, doctree)
            
            F = open(CONFIG.docdir+"/"+filename, "w")
            F.write(output)
            F.close()
        
        for (name,leaf) in subtree.items():
            if isinstance(leaf, dict):
                generate(formatter, CONFIG, leaf, path+[name])
            else:
                # must be module documentation object
                pass

    generate(formatter, CONFIG, CONFIG.repository.nestedModules, [])
    

    
    
if __name__ == "__main__":
    import sys
    
    config = DocGenConfig()
    config.docdir     = "pydoc"
    config.treeDepth=99
    config.tocDepth=3
    config.includeMethods=True
    config.includeModuleDocString=True
    config.showComponentsOnIndices=True
        

    urlPrefix=""

    cmdLineArgs = []

    for arg in sys.argv[1:]:
        if arg[:2] == "--" and len(arg)>2:
            cmdLineArgs.append(arg.lower())
        else:
            cmdLineArgs.append(arg)
    
    if not cmdLineArgs or "--help" in cmdLineArgs or "-h" in cmdLineArgs:
        sys.stderr.write("\n".join([
            "Usage:",
            "",
            "    "+sys.argv[0]+" <arguments - see below>",
            "",
            "Only <repository dir> is mandatory, all other arguments are optional.",
            "",
            "    --help               Display this help message",
            "",
            "    --filter <substr>    Only build docs for components/prefabs for components",
            "                         or modules who's full path contains <substr>",
            "",
            "    --urlprefix <prefix> Prefix for URLs - eg. a base dir: '/Components/pydoc/",
            "                         (remember the trailing slash if you want one)",
            "",
            "    --outdir <dir>       Directory to put output into (default is 'pydoc')",
            "                         directory must already exist (and be emptied)",
            "",
            "    --root <moduleRoot>  The module path leading up to the repositoryDir specified",
            "                         eg. Kamaelia.File, if repositoryDir='.../Kamaelia/File/'",
            "                         default='Kamaelia'",
            "",
            "    --notjustcomponents  Causes documentation for classes and functions too",
            "",
            "    --footerinclude <file> '<prefix><file>' will be specified as an include at the",
            "                           bottom of all pages",
            "",
            "    --promotetitles      Promote module level doc string titles to top of pages",
            "                         generated. Also causes breadcrumb trails at the top of",
            "                         pages to be reduced in emphasis slightly, so the title",
            "                         properly stands out",
            "",
            "    --indexdepth         Depth (nesting levels) of indexes on non-module pages.",
            "                         Use 0 to suppress index all together",
            "",
            "    <repositoryDir>      Use Kamaelia modules here instead of the installed ones",
            "",
            "",
        ]))
        sys.exit(0)

    try:
        if "--filter" in cmdLineArgs:
            index = cmdLineArgs.index("--filter")
            config.filterPattern = cmdLineArgs[index+1]
            del cmdLineArgs[index+1]
            del cmdLineArgs[index]

        if "--urlprefix" in cmdLineArgs:
            index = cmdLineArgs.index("--urlprefix")
            urlPrefix = cmdLineArgs[index+1]
            del cmdLineArgs[index+1]
            del cmdLineArgs[index]
            
        if "--outdir" in cmdLineArgs:
            index = cmdLineArgs.index("--outdir")
            config.docdir = cmdLineArgs[index+1]
            del cmdLineArgs[index+1]
            del cmdLineArgs[index]
            
        if "--root" in cmdLineArgs:
            index = cmdLineArgs.index("--root")
            config.docroot = cmdLineArgs[index+1]
            del cmdLineArgs[index+1]
            del cmdLineArgs[index]
            
        if "--notjustcomponents" in cmdLineArgs:
            index = cmdLineArgs.index("--notjustcomponents")
            config.includeNonKamaeliaStuff=True
            del cmdLineArgs[index]

        if "--promotetitles" in cmdLineArgs:
            index = cmdLineArgs.index("--promotetitles")
            config.promoteModuleTitles=True
            config.deemphasiseTrails=True
            del cmdLineArgs[index]

        if "--footerinclude" in cmdLineArgs:
            index = cmdLineArgs.index("--footerinclude")
            location=cmdLineArgs[index+1]
            config.pageFooter = "\n[include][location="+urlPrefix+location+" ] ]\n"
            del cmdLineArgs[index+1]
            del cmdLineArgs[index]

        if "--indexdepth" in cmdLineArgs:
            index = cmdLineArgs.index("--indexdepth")
            config.treeDepth = int(cmdLineArgs[index+1])
            assert(config.treeDepth >= 0)
            del cmdLineArgs[index+1]
            del cmdLineArgs[index]

        if len(cmdLineArgs)==1:
            REPOSITORYDIR = cmdLineArgs[0]
        elif len(cmdLineArgs)==0:
            REPOSITORYDIR = None
        else:
            raise
    except:
        sys.stderr.write("\n".join([
            "Error in command line arguments.",
            "Run with '--help' for info on command line arguments.",
            "",
            "",
        ]))
        sys.exit(1)
    
    sys.argv=sys.argv[0:0]
        
    debug = False
    REPOSITORY = Repository.SourceTreeDocs(baseDir=REPOSITORYDIR,rootName=config.docroot)
    config.repository=REPOSITORY

    renderer = RenderHTML(titlePrefix="Kamaelia docs : ",
                          urlPrefix=urlPrefix,
                          debug=False,
                          rawFooter=config.pageFooter)
    
    if 1:
        # automatically generate crosslinks when component names are seen
        crossLinks = {}
        for (path,m) in REPOSITORY.flatModules.items():
            items = m.components + m.prefabs
            if config.includeNonKamaeliaStuff:
                items += m.classes + m.functions
            for item in items:
                name=".".join(path)
                crossLinks[name] = name
                name=".".join(list(path)+[item.name])
                crossLinks[name] = name
#        for fullpath in crossLinks.keys():
#            shortened = fullpath.split(".")[-1]
#            crossLinks[shortened] = crossLinks[fullpath]
        renderer.setAutoCrossLinks( crossLinks )
    
    formatter = docFormatter(renderer, config=config)

    generateDocumentationFiles(formatter,config)
    generateIndices(formatter,config)
