import { Controller, Get } from '@nestjs/common';
import { AppService } from './app.service';
import { CONST, rpc, sc, wallet, tx, u } from '@cityofzion/neon-core';
// import Neon from '@cityofzion/neon-js';
import * as neonCore from '@cityofzion/neon-core';

// https://dojo.coz.io/neo3/neon-js/docs/guides/transfer

@Controller()
export class AppController {
  private coreContract = '0xb0598ece0bdd699e0b3e7fa89d505e0912ef6658';
  private cutieToken = '0x4d038f4f53ca4ea905887231695aecf301c29d46';
  private rpcClient;
  private vars: any = {};
  private inputs = {
    toAccount: new wallet.Account(
      // '721a66b9bc867cbd43891d0a0e7b2cf6a85c2d6fab511edc46cbecb502dddb2b',
      'L13Wg9tckQsttrGxA8S2hMg1uqSJRWVNZh17TRTdkkNA1Libpd6o'
    ),
    fromAccount: new wallet.Account(
      // '19650b64eb614c295053cf044b74d8cf9dab3c41040e3c88f181dcf583f37ba8',
      'Kx55J7cK8hqZeLZchi9PnX2v9L6zAZTSE3eQzDD9as6dbuggy7tn',
    ),
    tokenScriptHash: CONST.NATIVE_CONTRACT_HASH.GasToken,
    // tokenScriptHash: '0xefd36792452f2a9c4ece2e0dea0a8de43290e67c',
    amountToTransfer: 1,
    systemFee: 0,
    networkFee: 0,
    // networkMagic: 1234567890, //CONST.MAGIC_NUMBER.TestNet,
    networkMagic: 4006389356, //CONST.MAGIC_NUMBER.TestNet,
    nodeUrl: 'http://localhost:50012', //'http://seed2t.neo.org:20332',
  };

  constructor(private readonly appService: AppService) {
    this.rpcClient = new rpc.RPCClient(this.inputs.nodeUrl);
  }

  @Get()
  getHello(): string {
    return this.appService.getHello();
  }

  @Get('aaa')
  async getXxx() {
    return await this.rpcClient.getApplicationLog('0x3e676d5f15f5123a5a463dc4bb981d1bfdc6287a9b4945917a35c5430885b5ec')
  }

  @Get('xxx')
  async getX() {
    await this.createTransaction();
    await this.checkToken();
    await this.checkNetworkFee();
    await this.checkSystemFee();
    await this.checkBalance();
    await this.performTransfer();
  }

  async createTransaction() {
    // Since the token is now an NEP-17 token, we transfer using a VM script.
    const script = sc.createScript({
      scriptHash: this.inputs.tokenScriptHash,
      operation: 'transfer',
      args: [
        sc.ContractParam.hash160(this.inputs.fromAccount.address),
        sc.ContractParam.hash160(this.coreContract),
        sc.ContractParam.integer(300),
        sc.ContractParam.array(
          sc.ContractParam.string('_create_sale_auction'),
          sc.ContractParam.integer(1),
          sc.ContractParam.integer(100),
          sc.ContractParam.integer(9000),
          sc.ContractParam.integer(3000000),
        ),
      ],
    });
    // const script = sc.createScript({
    //   scriptHash: this.cutieToken,
    //   operation: 'ownerOf',
    //   args: [
    //     sc.ContractParam.integer(1),
    //   ],
    // });


    // We retrieve the current block height as we need to
    const currentHeight = await this.rpcClient.getBlockCount();
    this.vars.tx = new tx.Transaction({
      signers: [
        {
          account: this.inputs.fromAccount.scriptHash,
          // scopes: tx.WitnessScope.CalledByEntry,
          // scopes: tx.WitnessScope.Global,
          scopes: tx.WitnessScope.CustomContracts,
          allowedContracts: [
            CONST.NATIVE_CONTRACT_HASH.GasToken,
            this.coreContract,
            // this.cutieToken,
          ],
        },
      ],
      validUntilBlock: currentHeight + 1000,
      script: script,
    });
    console.log('\u001b[32m  ✓ Transaction created \u001b[0m');
  }

  async checkNetworkFee() {
    const feePerByteInvokeResponse = await this.rpcClient.invokeFunction(
      CONST.NATIVE_CONTRACT_HASH.PolicyContract,
      'getFeePerByte'
    );

    if (feePerByteInvokeResponse.state !== 'HALT') {
      if (this.inputs.networkFee === 0) {
        throw new Error('Unable to retrieve data to calculate network fee.');
      } else {
        console.log(
          '\u001b[31m  ✗ Unable to get information to calculate network fee.  Using user provided value.\u001b[0m'
        );
        this.vars.tx.networkFee = u.BigInteger.fromNumber(this.inputs.networkFee);
      }
    }
    const feePerByte = u.BigInteger.fromNumber(
      feePerByteInvokeResponse.stack[0].value as string
    );
    // Account for witness size
    const transactionByteSize = this.vars.tx.serialize().length / 2 + 109;
    // Hardcoded. Running a witness is always the same cost for the basic account.
    const witnessProcessingFee = u.BigInteger.fromNumber(1000390);
    const networkFeeEstimate = feePerByte
      .mul(transactionByteSize)
      .add(witnessProcessingFee);
    if (
      this.inputs.networkFee &&
      u.BigInteger.fromNumber(this.inputs.networkFee) >= networkFeeEstimate
    ) {
      this.vars.tx.networkFee = u.BigInteger.fromNumber(this.inputs.networkFee);
      console.log(
        `  i Node indicates ${networkFeeEstimate.toDecimal(
          8
        )} networkFee but using user provided value of ${
          this.inputs.networkFee
        }`,
      );
    } else {
      this.vars.tx.networkFee = networkFeeEstimate;
    }
    console.log(
      `\u001b[32m  ✓ Network Fee set: ${this.vars.tx.networkFee.toDecimal(
        8
      )} \u001b[0m`
    );
  }

  async checkToken() {
    const tokenNameResponse = await this.rpcClient.invokeFunction(
      this.inputs.tokenScriptHash,
      'symbol',
    );

    if (tokenNameResponse.state !== 'HALT') {
      throw new Error(
        'Token not found! Please check the provided tokenScriptHash is correct.'
      );
    }

    this.vars.tokenName = u.HexString.fromBase64(
      tokenNameResponse.stack[0].value as string
    ).toAscii();

    console.log('\u001b[32m  ✓ Token found \u001b[0m');
  }

  /**
   SystemFees pay for the processing of the script carried in the transaction. We
   can easily get this number by using invokeScript with the appropriate signers.
   */
  async checkSystemFee() {
    // this.vars.tx.systemFee = u.BigInteger.fromNumber(11322390);
    // return;
    const invokeFunctionResponse = await this.rpcClient.invokeScript(
      u.HexString.fromHex(this.vars.tx.script),
      [
        {
          account: this.inputs.fromAccount.scriptHash,
          // scopes: tx.WitnessScope.Global, // TODO: also try to make it with CalledByEntry here
          // scopes: tx.WitnessScope.CustomContracts,
          scopes: tx.WitnessScope.CalledByEntry,
          // allowedContracts: [
          //   this.coreContract,
          //   this.cutieToken,
          // ],
        },
      ],
    );
    console.log(invokeFunctionResponse);
    if (invokeFunctionResponse.state !== 'HALT') {
      throw new Error(
        `Transfer script errored out: ${invokeFunctionResponse.exception}`
      );
    }
    const requiredSystemFee = u.BigInteger.fromNumber(
      invokeFunctionResponse.gasconsumed
    );
    if (
      this.inputs.systemFee &&
      u.BigInteger.fromNumber(this.inputs.systemFee) >= requiredSystemFee
    ) {
      this.vars.tx.systemFee = u.BigInteger.fromNumber(this.inputs.systemFee);
      console.log(
        `  i Node indicates ${requiredSystemFee} systemFee but using user provided value of ${this.inputs.systemFee}`
      );
    } else {
      this.vars.tx.systemFee = requiredSystemFee;
    }
    console.log(
      `\u001b[32m  ✓ SystemFee set: ${this.vars.tx.systemFee.toDecimal(8)}\u001b[0m`
    );
  }

  /**
   We will also need to check that the inital address has sufficient funds for the transfer.
   We look for both funds of the token we intend to transfer and GAS required to pay for the transaction.
   For this, we rely on the [TokensTracker](https://github.com/neo-project/neo-modules/tree/master/src/TokensTracker)
   plugin. Hopefully, the node we select has the plugin installed.
   */
  async checkBalance() {
    let balanceResponse;
    try {
      balanceResponse = await this.rpcClient.execute(
        new rpc.Query({
          method: 'getnep17balances',
          params: [this.inputs.fromAccount.address],
        })
      );
    } catch (e) {
      console.log(e);
      console.log(
        '\u001b[31m  ✗ Unable to get balances as plugin was not available. \u001b[0m'
      );
      return;
    }

    console.log(balanceResponse)

    // Check for token funds
    const balances = balanceResponse.balance.filter((bal) =>
      bal.assethash.includes(this.inputs.tokenScriptHash)
    );
    const balanceAmount =
      balances.length === 0 ? 0 : parseInt(balances[0].amount);
    if (balanceAmount < this.inputs.amountToTransfer) {
      throw new Error(`Insufficient funds! Found ${balanceAmount}`);
    } else {
      console.log('\u001b[32m  ✓ Token funds found \u001b[0m');
    }

    // Check for gas funds for fees
    const gasRequirements = this.vars.tx.networkFee.add(this.vars.tx.systemFee);
    const gasBalance = balanceResponse.balance.filter((bal) =>
      bal.assethash.includes(CONST.NATIVE_CONTRACT_HASH.GasToken)
    );
    const gasAmount =
      gasBalance.length === 0
        ? u.BigInteger.fromNumber(0)
        : u.BigInteger.fromNumber(gasBalance[0].amount);

    if (gasAmount.compare(gasRequirements) === -1) {
      throw new Error(
        `Insufficient gas to pay for fees! Required ${gasRequirements.toString()} but only had ${gasAmount.toString()}`,
      );
    } else {
      console.log(
        `\u001b[32m  ✓ Sufficient GAS for fees found (${gasRequirements.toString()}) \u001b[0m`,
      );
    }
  }

  /**
   And finally, to send it off to network.
   */
  async performTransfer() {
    const signedTransaction = this.vars.tx.sign(
      this.inputs.fromAccount,
      this.inputs.networkMagic,
    );

    console.log(this.vars.tx.toJson());
    console.log(signedTransaction);
    const result = await this.rpcClient.sendRawTransaction(
      u.HexString.fromHex(signedTransaction.serialize(true)),
    );

    console.log('\n\n--- Transaction hash ---');
    console.log(result);

  }
}
