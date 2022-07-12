import boa3
from boa3_test.tests.boa_test import BoaTest


class CutieTest(BoaTest):
    ZERO_ADDRESS = boa3.neo.to_script_hash(b'NKuyBkoGdZZSLyPbJEetheRhMjeznFZszf')

    def test_engine_path(self):
        return '/usr/src/neo-devpack-dotnet/src/Neo.TestEngine/bin/Debug/net6.0'
