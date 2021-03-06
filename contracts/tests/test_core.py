import os

import boa3
from pprint import pprint
from boa3 import constants
from boa3_test.tests.test_classes.testengine import TestEngine, WitnessScope

from cutie_test import CutieTest


class TestCore(CutieTest):
    default_folder: str = 'contracts'

    # OWNER_ACCOUNT = to_script_hash(b'NigoG6c4gTJcUVZtpY7fZPcCZaA2WiE12m')
    OWNER_ACCOUNT = b'\x9c\xa5/\x04"{\xf6Z\xe2\xe5\xd1\xffe\x03\xd1\x9dd\xc2\x9cF' # some address generated by tests
    COZ_ACCOUNT = boa3.neo.to_script_hash(b'NigVWQwT8Mc4ZkxEDsaEtuvL8hZYQFHr5A')

    # gas transfer case, with default Witness scope is not working (why?!)
    def test_failing_transfer(self):
        folders = os.path.abspath(__file__).split(os.sep)
        self.engine = TestEngine(self.test_engine_path())

        # init cutie token
        self.cutie_token_path = self.get_contract_path('/'.join(folders[:-2]), 'contracts', 'SomeNFT')
        self.engine.add_contract(self.cutie_token_path.replace('.py', '.nef'))
        output, manifest = self.get_output(self.cutie_token_path)
        cutie_token_address = boa3.neo.cryptography.hash160(output)

        # init core
        self.core_path = self.get_contract_path('/'.join(folders[:-2]), 'contracts', 'Core')
        self.engine.add_contract(self.core_path.replace('.py', '.nef'))
        output, manifest = self.get_output(self.core_path)
        self.core_address = boa3.neo.cryptography.hash160(output)

        self.engine.add_gas(self.OWNER_ACCOUNT, 1000_00000000)
        self.engine.add_gas(self.COZ_ACCOUNT, 1000_00000000)

        self.run_smart_contract(self.engine, constants.GAS_SCRIPT, 'transfer', self.COZ_ACCOUNT, self.core_address, 300, ["test_gas", 777], signer_accounts=[self.COZ_ACCOUNT])

        transferEvent = self.engine.get_events('Transfer')
        self.assertEqual(len(transferEvent), 0)
        gasTestEvent = self.engine.get_events('GasTestEvent')
        self.assertEqual(len(gasTestEvent), 0)

    # gas transfer case, with GLOBAL Witness scope is working (why?!)
    def test_working_transfer(self):
        folders = os.path.abspath(__file__).split(os.sep)
        self.engine = TestEngine(self.test_engine_path())

        # init cutie token
        self.cutie_token_path = self.get_contract_path('/'.join(folders[:-2]), 'contracts', 'SomeNFT')
        self.engine.add_contract(self.cutie_token_path.replace('.py', '.nef'))
        output, manifest = self.get_output(self.cutie_token_path)
        cutie_token_address = boa3.neo.cryptography.hash160(output)

        # init core
        self.core_path = self.get_contract_path('/'.join(folders[:-2]), 'contracts', 'Core')
        self.engine.add_contract(self.core_path.replace('.py', '.nef'))
        output, manifest = self.get_output(self.core_path)
        self.core_address = boa3.neo.cryptography.hash160(output)

        self.engine.add_gas(self.OWNER_ACCOUNT, 1000_00000000)
        self.engine.add_gas(self.COZ_ACCOUNT, 1000_00000000)

        self.engine.add_signer_account(self.COZ_ACCOUNT, WitnessScope.Global) # HERE IS THE MAIN DIFFERENCE BETWEEN TWO TESTS
        self.run_smart_contract(self.engine, constants.GAS_SCRIPT, 'transfer', self.COZ_ACCOUNT, self.core_address, 300, ["test_gas", 777], signer_accounts=[self.COZ_ACCOUNT])

        transferEvent = self.engine.get_events('Transfer')
        self.assertEqual(transferEvent[0].name, 'Transfer')
        self.assertEqual(transferEvent[0].arguments, (
            b'\xf9\xbea}\xf1\x96\x11\xa3\xd33a\x9d$\xed\xd0\x92\x8e\x7f\x83\x9b',
            b')\xb5@\x82\x1d\x12\x19\xeb\xb6\x84+\x88dy4\xfd\xecr\x0eX',
            300
        ))

        gasTestEvent = self.engine.get_events('GasTestEvent')
        self.assertEqual(gasTestEvent[0].name, 'GasTestEvent')
        self.assertEqual(gasTestEvent[0].arguments, (
            b'\xf9\xbea}\xf1\x96\x11\xa3\xd33a\x9d$\xed\xd0\x92\x8e\x7f\x83\x9b',
            300,
            ['test_gas', 777]
        ))



