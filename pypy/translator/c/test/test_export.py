from pypy.translator.translator import TranslationContext
from pypy.translator.c.exportinfo import export, ModuleExportInfo
from pypy.translator.c.dlltool import CLibraryBuilder
from pypy.translator.tool.cbuild import ExternalCompilationInfo
import sys

class TestExportFunctions:
    def setup_method(self, method):
        self.additional_PATH = []
        # Uniquify: use the method name without the 'test' prefix.
        self.module_suffix = method.__name__[4:]

    def compile_module(self, modulename, **exports):
        modulename += self.module_suffix
        export_info = ModuleExportInfo()
        for name, obj in exports.items():
            export_info.add_function(name, obj)

        t = TranslationContext()
        t.buildannotator()
        export_info.annotate(t.annotator)
        t.buildrtyper().specialize()

        functions = [(f, None) for f in export_info.functions.values()]
        builder = CLibraryBuilder(t, None, config=t.config,
                                  name='lib' + modulename,
                                  functions=functions)
        if sys.platform != 'win32' and self.additional_PATH:
            builder.merge_eci(ExternalCompilationInfo(
                    link_extra=['-Wl,-rpath,%s' % path for path in
                                self.additional_PATH]))
        builder.modulename = 'lib' + modulename
        builder.generate_source()
        builder.compile()

        mod = export_info.make_import_module(builder)

        filepath = builder.so_name.dirpath()
        self.additional_PATH.append(filepath)

        return mod

    def test_simple_call(self):
        # function exported from the 'first' module
        @export(float)
        def f(x):
            return x + 42.3
        firstmodule = self.compile_module("first", f=f)
        
        # call it from a function compiled in another module
        @export()
        def g():
            return firstmodule.f(12.0)
        secondmodule = self.compile_module("second", g=g)

        assert secondmodule.g() == 54.3

    def test_implied_signature(self):
        @export  # No explicit signature here.
        def f(x):
            return x + 1.5
        @export()  # This is an explicit signature, with no argument.
        def f2():
            f(1.0)
        firstmodule = self.compile_module("first", f=f, f2=f2)
        
        @export()
        def g():
            return firstmodule.f(41)
        secondmodule = self.compile_module("second", g=g)

        assert secondmodule.g() == 42.5

