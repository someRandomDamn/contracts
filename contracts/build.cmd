
neo3-boa contracts/SomeNFT.py --debug
neo3-boa contracts/Core.py --debug

neoxp transfer 10000000 GAS genesis owner
neoxp transfer 10000000 GAS genesis coz

neoxp contract deploy contracts/SomeNFT.nef owner
neoxp contract deploy contracts/Core.nef owner

neoxp contract invoke invoke-files/init.neo-invoke.json owner

neoxp contract list
neoxp show balances owner
neoxp show balances coz

neoxp checkpoint create checkpoints/test --force
