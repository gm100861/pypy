import py
from pypy.conftest import gettestobjspace, option
from pypy.rlib import debug

class AppTestDebug:
    def setup_class(cls):
        if option.runappdirect:
            py.test.skip("not meant to be run with -A")
        cls.space = gettestobjspace(usemodules=['__pypy__'])
        space = cls.space
        cls.w_check_log = cls.space.wrap(cls.check_log)

    def setup_method(self, meth):
        debug._log = debug.DebugLog()

    def teardown_method(self, meth):
        debug._log = None

    @classmethod
    def check_log(cls, expected):
        assert list(debug._log) == expected

    def test_debug_print(self):
        from __pypy__ import debug_start, debug_stop, debug_print
        debug_start('my-category')
        debug_print('one')
        debug_print('two', 3, [])
        debug_stop('my-category')
        self.check_log([
                ('my-category', [
                        ('debug_print', 'one'),
                        ('debug_print', 'two 3 []'),
                        ])
                ])

    def test_debug_print_once(self):
        from __pypy__ import debug_print_once
        debug_print_once('foobar', 'hello world')
        self.check_log([
                ('foobar', [
                        ('debug_print', 'hello world'),
                        ])
                ])
