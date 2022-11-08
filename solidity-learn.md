# Solidity开发



## 基础概念



```js
pragma solidity ^0.4.0;

contract SimpleStorage {
    uint storedData;

    function set(uint x) public {
        storedData = x;
    }

    function get() public view returns (uint) {
        return storedData;
    }
}
```

关键字 `pragma` 的含义是，一般来说，pragmas（编译指令）是告知编译器如何处理源代码的指令的

>所有的标识符（合约名称，函数名称和变量名称）都只能使用ASCII字符集。UTF-8编码的数据可以用字符串变量的形式存储。

### 子货币（Subcurrency）例子

下面的合约实现了一个最简单的加密货币。这里，币确实可以无中生有地产生，但是只有创建合约的人才能做到（实现一个不同的发行计划也不难）。而且，任何人都可以给其他人转币，不需要注册用户名和密码 —— 所需要的只是以太坊密钥对。

```js
pragma solidity ^0.4.21;

contract Coin {
    // 关键字“public”让这些变量可以从外部读取
    address public minter;
    mapping (address => uint) public balances;

    // 轻客户端可以通过事件针对变化作出高效的反应
    event Sent(address from, address to, uint amount);

    // 这是构造函数，只有当合约创建时运行
    function Coin() public {
        minter = msg.sender;
    }

    function mint(address receiver, uint amount) public {
        if (msg.sender != minter) return;
        balances[receiver] += amount;
    }

    function send(address receiver, uint amount) public {
        if (balances[msg.sender] < amount) return;
        balances[msg.sender] -= amount;
        balances[receiver] += amount;
        emit Sent(msg.sender, receiver, amount);
    }
}
```

`address public minter;` 这一行声明了一个可以被公开访问的 `address` 类型的状态变量。 `address` 类型是一个160位的值，且不允许任何算数操作。这种类型适合存储合约地址或外部人员的密钥对。关键字 `public` 自动生成一个函数，允许你在这个合约之外访问这个状态变量的当前值。如果没有这个关键字，其他的合约没有办法访问这个变量

下一行， `mapping (address => uint) public balances;` 也创建一个公共状态变量，但它是一个更复杂的数据类型。 该类型将address映射为无符号整数。 Mappings 可以看作是一个 [哈希表](https://en.wikipedia.org/wiki/Hash_table) 它会执行虚拟初始化，以使所有可能存在的键都映射到一个字节表示为**全零的值**。 但是，这种类比并不太恰当，**因为它既不能获得映射的所有键的列表，也不能获得所有值的列表**。 因此，要么记住你添加到mapping中的数据（**使用列表或更高级的数据类型会更好**），要么在不需要键列表或值列表的上下文中使用它，就如本例。 而由 `public` 关键字创建的getter函数 [getter function](https://solidity-cn.readthedocs.io/zh/develop/contracts.html#getter-functions) 则是更复杂一些的情况， 它大致如下所示：

```js
function balances(address _account) public view returns (uint) {
    return balances[_account];
}
```

`event Sent(address from, address to, uint amount);` 这行声明了一个所谓的“事件（event）”，它会在 `send` 函数的最后一行被发出。用户界面（当然也包括服务器应用程序）可以监听区块链上正在发送的事件，而不会花费太多成本。一旦它被发出，监听该事件的listener都将收到通知。而所有的事件都包含了 `from` ， `to` 和 `amount` 三个参数，可方便追踪事务。 为了监听这个事件，你可以使用如下代码

```js
Coin.Sent().watch({}, '', function(error, result) {
    if (!error) {
        console.log("Coin transfer: " + result.args.amount +
            " coins were sent from " + result.args.from +
            " to " + result.args.to + ".");
        console.log("Balances now:\n" +
            "Sender: " + Coin.balances.call(result.args.from) +
            "Receiver: " + Coin.balances.call(result.args.to));
    }
})
```

特殊函数 `Coin` 是在创建合约期间运行的构造函数，不能在事后调用。 它永久存储创建合约的人的地址: `msg` (以及 `tx` 和 `block` ) 是一个神奇的全局变量，其中包含一些允许访问区块链的属性。 `msg.sender` 始终是当前**（外部）函数调用的来源地址。**

最后，真正被用户或其他合约所调用的，以完成本合约功能的方法是 `mint` 和 `send`。 如果 `mint` 被合约创建者外的其他人调用则什么也不会发生。 另一方面， `send` 函数可被任何人用于向他人发送币 (当然，前提是发送者拥有这些币)。



### 账户

外部账户的地址是由公钥决定的，而合约账户的地址是在创建该合约时确定的（这个地址通过合约创建者的地址和从该地址发出过的交易数量计算得到的，也就是所谓的“nonce”）

无论帐户是否存储代码，这两类账户对 EVM 来说是一样的。

每个账户都有一个键值对形式的持久化存储。其中 key 和 value 的长度都是256位，我们称之为 **存储** 。

此外，每个账户有一个以太币余额（ **balance** ）（单位是“Wei”），余额会因为发送包含以太币的交易而改变。



### 交易

交易可以看作是从一个帐户发送到另一个帐户的消息（这里的账户，可能是相同的或特殊的零帐户，请参阅下文）。它能包含一个二进制数据（合约负载）和以太币。

**如果目标账户含有代码，此代码会被执行，并以 payload 作为入参。**

如果目标账户是**零账户（账户地址为 `0` )**，此交易将创建一个 **新合约** 。 如前文所述，合约的地址不是零地址，而是通过合约创建者的地址和从该地址发出过的交易数量计算得到的（所谓的“nonce”）。 这个用来创建合约的交易的 payload 会被转换为 EVM 字节码并执行。**执行的输出将作为合约代码被永久存储**。这意味着，**为创建一个合约，你不需要发送实际的合约代码，而是发送能够产生合约代码的代码。** 为其他语言编写合约代码提供可能。

(不能主动发起交易，只能接收到外部账户调用后才能发起交易或调用其他**合约账户**)其除了balance和nonce之外还有code(代码)、**storage(相关状态-存储)**
创建合约时候会返回一个地址，就可以对其调用。调用过程中，代码不变但存储状态会发生改变。

**注解**

在合约创建的过程中，它的代码还是空的。所以直到构造函数执行结束，你都不应该在其中调用合约自己函数。



### Gas

无论执行到什么位置，一旦 gas 被耗尽（比如降为负值），将会触发一个 out-of-gas 异常。当前调用帧（call frame）所做的所有状态修改都将被回滚。

译者注：调用帧（call frame），指的是下文讲到的EVM的运行栈（stack）中当前操作所需要的若干元素。



### 存储，内存和栈

每个账户有一块持久化内存区称为 **存储** 。 存储是将256位字映射到256位字的键值存储区。 在合约中枚举存储是不可能的，且读存储的相对开销很高，修改存储的开销甚至更高。合约只能读写存储区内属于自己的部分。

第二个内存区称为 **内存** ，合约会试图为每一次消息调用获取一块被**重新擦拭干净的内存实例**。 **内存是线性的**，可按**字节级寻址**，但**读的长度被限制为256位，而写的长度可以是8位或256位。当访问（无论是读还是写）之前从未访问过的内存字（word）时**（无论是偏移到该字内的任何位置），内存将按字进行扩展（每个字是256位）。**扩容也将消耗一定的gas**。 随着内存使用量的增长，其费用也会增高（以平方级别）。

EVM 不是基于寄存器的，而是**基于栈的**，因此所有的计算都在一个被称为 **栈（stack）** 的区域执行。 栈最大有**1024个元素**，**每个元素长度是一个字（256位**）(**寻址单位是256位**)。对栈的访问只限于其顶端，限制方式为：**允许拷贝最顶端的16个元素中的一个到栈顶，或者是交换栈顶元素和下面16个元素中的一个。所有其他操作都只能取最顶的两个（或一个，或更多，取决于具体的操作）元素，运算后，把结果压入栈顶**。当然可以把栈上的元素放到存储或内存中。但是无法只访问栈上指定深度的那个元素，除非先从栈顶移除其他元素。

### 指令集

EVM的指令集量应尽量少，以最大限度地避免可能导致共识问题的错误实现。所有的指令都是针对"256位的字（word）"这个基本的数据类型来进行操作。具备常用的算术、位、逻辑和比较操作。也可以做到有条件和无条件跳转。此外，合约可以访问当前区块的相关属性，比如它的编号和时间戳。

### 消息调用

合约可以通过消息调用的方式来调用其它合约或者发送以太币到非合约账户。消息调用和交易非常类似，它们都有一个源、目标、数据、以太币、gas和返回数据。事实上每个交易都由一个顶层消息调用组成，这个消息调用又可创建更多的消息调用。

被调用的合约（可以和调用者是同一个合约）会获得一块刚刚清空过的内存，并可以访问调用的payload——由被称为 calldata 的独立区域所提供的数据。调用执行结束后，返回数据将被存放在调用方预先分配好的一块内存中。 调用深度被 **限制** 为 1024 ，因此对于更加复杂的操作，我们应使用循环而不是递归。

### 委托调用/代码调用和库

有一种特殊类型的消息调用，被称为 **委托调用(delegatecall)** 。它和一般的消息调用的区别在于，目标地址的代码将在发起调用的合约的上下文中执行，并且 `msg.sender` 和 `msg.value` 不变。 这意味着一个合约可以在运行时从另外一个地址动态加载代码。存储、当前地址和余额都指向发起调用的合约，只有代码是从被调用地址获取的。 这使得 Solidity 可以实现”库“能力：可复用的代码库可以放在一个合约的存储上，如用来实现复杂的数据结构的库

### 日志

有一种特殊的可索引的数据结构，其存储的数据可以一路映射直到区块层级。这个特性被称为 **日志(logs)** ，Solidity用它来实现 **事件(events)** 。合约创建之后就无法访问日志数据，但是这些数据可以从区块链外高效的访问。因为部分日志数据被存储在 [布隆过滤器（Bloom filter)](https://en.wikipedia.org/wiki/Bloom_filter) 中，我们可以高效并且加密安全地搜索日志，所以那些没有下载整个区块链的网络节点（轻客户端）也可以找到这些日志。

### 创建

合约甚至可以通过一个特殊的指令来创建其他合约（不是简单的调用零地址）。创建合约的调用 **create calls** 和普通消息调用的唯一区别在于，负载会被执行，执行的结果被存储为合约代码，调用者/创建者在栈上得到新合约的地址

### 自毁

合约代码从区块链上移除的唯一方式是合约在合约地址上的执行自毁操作 `selfdestruct` 。合约账户上剩余的以太币会发送给指定的目标，然后其存储和代码从状态中被移除。



## 根据例子学习Solidity

### 投票

我们的想法是为每个（投票）表决创建一份合约，为每个选项提供简称。 然后作为合约的创造者——即主席，将给予每个独立的地址以投票权。

地址后面的人可以选择自己投票，或者委托给他们信任的人来投票。

在投票时间结束时，`winningProposal()` 将返回获得最多投票的提案。

```js
pragma solidity ^0.4.22;

/// @title 委托投票
contract Ballot {
    // 这里声明了一个新的复合类型用于稍后的变量
    // 它用来表示一个选民
    struct Voter {
        uint weight; // 计票的权重
        bool voted;  // 若为真，代表该人已投票
        address delegate; // 被委托人
        uint vote;   // 投票提案的索引
    }

    // 提案的类型
    struct Proposal {
        bytes32 name;   // 简称（最长32个字节）
        uint voteCount; // 得票数
    }

    address public chairperson;

    // 这声明了一个状态变量，为每个可能的地址存储一个 `Voter`。
    mapping(address => Voter) public voters;

    // 一个 `Proposal` 结构类型的动态数组
    Proposal[] public proposals;

    /// 为 `proposalNames` 中的每个提案，创建一个新的（投票）表决
    constructor(bytes32[] proposalNames) public {
        chairperson = msg.sender;
        voters[chairperson].weight = 1;
        //对于提供的每个提案名称，
        //创建一个新的 Proposal 对象并把它添加到数组的末尾。
        for (uint i = 0; i < proposalNames.length; i++) {
            // `Proposal({...})` 创建一个临时 Proposal 对象，
            // `proposals.push(...)` 将其添加到 `proposals` 的末尾
            proposals.push(Proposal({
                name: proposalNames[i],
                voteCount: 0
            }));
        }
    }

    // 授权 `voter` 对这个（投票）表决进行投票
    // 只有 `chairperson` 可以调用该函数。
    function giveRightToVote(address voter) public {
        // 若 `require` 的第一个参数的计算结果为 `false`，
        // 则终止执行，撤销所有对状态和以太币余额的改动。
        // 在旧版的 EVM 中这曾经会消耗所有 gas，但现在不会了。
        // 使用 require 来检查函数是否被正确地调用，是一个好习惯。
        // 你也可以在 require 的第二个参数中提供一个对错误情况的解释。
        require(
            msg.sender == chairperson,
            "Only chairperson can give right to vote."
        );
        require(
            !voters[voter].voted,
            "The voter already voted."
        );
        require(voters[voter].weight == 0);
        voters[voter].weight = 1;
    }

    /// 把你的投票委托到投票者 `to`。
    function delegate(address to) public {
        // 传引用    这个Storage类型是什么意思？
        Voter storage sender = voters[msg.sender];
        require(!sender.voted, "You already voted.");
        require(to != msg.sender, "Self-delegation is disallowed.");

        // 委托是可以传递的，只要被委托者 `to` 也设置了委托。
        // 一般来说，这种循环委托是危险的。因为，如果传递的链条太长，
        // 则可能需消耗的gas要多于区块中剩余的（大于区块设置的gasLimit），
        // 这种情况下，委托不会被执行。
        // 而在另一些情况下，如果形成闭环，则会让合约完全卡住。
        while (voters[to].delegate != address(0)) {
            to = voters[to].delegate;
            // 不允许闭环委托
            require(to != msg.sender, "Found loop in delegation.");
        }

        // `sender` 是一个引用, 相当于对 `voters[msg.sender].voted` 进行修改
        sender.voted = true;
        sender.delegate = to;
        Voter storage delegate_ = voters[to];
        if (delegate_.voted) {
            // 若被委托者已经投过票了，直接增加得票数
            proposals[delegate_.vote].voteCount += sender.weight;
        } else {
            // 若被委托者还没投票，增加委托者的权重
            delegate_.weight += sender.weight;
        }
    }

    /// 把你的票(包括委托给你的票)，
    /// 投给提案 `proposals[proposal].name`.
    function vote(uint proposal) public {
        Voter storage sender = voters[msg.sender];
        require(!sender.voted, "Already voted.");
        sender.voted = true;
        sender.vote = proposal;

        // 如果 `proposal` 超过了数组的范围，则会自动抛出异常，并恢复所有的改动
        proposals[proposal].voteCount += sender.weight;
    }

    /// @dev 结合之前所有的投票，计算出最终胜出的提案
    function winningProposal() public view
            returns (uint winningProposal_)
    {
        uint winningVoteCount = 0;
        for (uint p = 0; p < proposals.length; p++) {
            if (proposals[p].voteCount > winningVoteCount) {
                winningVoteCount = proposals[p].voteCount;
                winningProposal_ = p;
            }
        }
    }

    // 调用 winningProposal() 函数以获取提案数组中获胜者的索引，并以此返回获胜者的名称
    function winnerName() public view
            returns (bytes32 winnerName_)
    {
        winnerName_ = proposals[winningProposal()].name;
    }
}
```

几个疑问： view   storage 关键词作用  、?	

### 可能的优化

当前，为了把投票权分配给所有参与者，需要执行很多交易。你有没有更好的主意？

### 秘密竞价（盲拍）

在本节中，我们将展示如何轻松地在以太坊上创建一个秘密竞价的合约。 我们将从公开拍卖开始，每个人都可以看到出价，然后将此合约扩展到盲拍合约， 在竞标期结束之前无法看到实际出价。

### 简单的公开拍卖

以下简单的拍卖合约的总体思路是每个人都可以在投标期内发送他们的出价。 出价已经包含了资金/以太币，来将投标人与他们的投标绑定。 如果最高出价提高了（被其他出价者的出价超过），之前出价最高的出价者可以拿回她的钱。 在投标期结束后，受益人需要手动调用合约来接收他的钱 - 合约不能自己激活接收。

```js
pragma solidity ^0.4.22;
contract SimpleAuction {
    // 拍卖的参数。
    address public beneficiary;
    // 时间是unix的绝对时间戳（自1970-01-01以来的秒数）
    // 或以秒为单位的时间段。
    uint public auctionEnd;

    // 拍卖的当前状态
    address public highestBidder;
    uint public highestBid;

    //可以取回的之前的出价
    mapping(address => uint) pendingReturns;

    // 拍卖结束后设为 true，将禁止所有的变更
    bool ended;

    // 变更触发的事件
    event HighestBidIncreased(address bidder, uint amount);
    event AuctionEnded(address winner, uint amount);

    // 以下是所谓的 natspec 注释，可以通过三个斜杠来识别。
    // 当用户被要求确认交易时将显示。

    /// 以受益者地址 `_beneficiary` 的名义，
    /// 创建一个简单的拍卖，拍卖时间为 `_biddingTime` 秒。
    constructor(
        uint _biddingTime,
        address _beneficiary
    ) public {
        beneficiary = _beneficiary;
        auctionEnd = now + _biddingTime;
    }

    /// 对拍卖进行出价，具体的出价随交易一起发送。
    /// 如果没有在拍卖中胜出，则返还出价。
    function bid() public payable {
        // 参数不是必要的。因为所有的信息已经包含在了交易中。
        // 对于能接收以太币的函数，关键字 payable 是必须的。

        // 如果拍卖已结束，撤销函数的调用。
        require(
            now <= auctionEnd,
            "Auction already ended."
        );

        // 如果出价不够高，返还你的钱
        require(
            msg.value > highestBid,
            "There already is a higher bid."
        );

        if (highestBid != 0) {
            // 返还出价时，简单地直接调用 highestBidder.send(highestBid) 函数，
            // 是有安全风险的，因为它有可能执行一个非信任合约。
            // 更为安全的做法是让接收方自己提取金钱。
            pendingReturns[highestBidder] += highestBid;
        }
        highestBidder = msg.sender;
        highestBid = msg.value;
        emit HighestBidIncreased(msg.sender, msg.value);
    }

    /// 取回出价（当该出价已被超越）
    function withdraw() public returns (bool) {
        uint amount = pendingReturns[msg.sender];
        if (amount > 0) {
            // 这里很重要，首先要设零值。
            // 因为，作为接收调用的一部分，
            // 接收者可以在 `send` 返回之前，重新调用该函数。
            pendingReturns[msg.sender] = 0;

            if (!msg.sender.send(amount)) {
                // 这里不需抛出异常，只需重置未付款
                pendingReturns[msg.sender] = amount;
                return false;
            }
        }
        return true;
    }

    /// 结束拍卖，并把最高的出价发送给受益人
    function auctionEnd() public {
        // 对于可与其他合约交互的函数（意味着它会调用其他函数或发送以太币），
        // 一个好的指导方针是将其结构分为三个阶段：
        // 1. 检查条件
        // 2. 执行动作 (可能会改变条件)
        // 3. 与其他合约交互
        // 如果这些阶段相混合，其他的合约可能会回调当前合约并修改状态，
        // 或者导致某些效果（比如支付以太币）多次生效。
        // 如果合约内调用的函数包含了与外部合约的交互，
        // 则它也会被认为是与外部合约有交互的。

        // 1. 条件
        require(now >= auctionEnd, "Auction not yet ended.");
        require(!ended, "auctionEnd has already been called.");

        // 2. 生效
        ended = true;
        emit AuctionEnded(highestBidder, highestBid);

        // 3. 交互
        beneficiary.transfer(highestBid);
    }
}
```



### 秘密竞拍（盲拍）

之前的公开拍卖接下来将被扩展为一个秘密竞拍。 秘密竞拍的好处是在投标结束前不会有时间压力。 在一个透明的计算平台上进行秘密竞拍听起来像是自相矛盾，但密码学可以实现它。

在 **投标期间** ，投标人实际上并没有发送她的出价，而只是发送一个哈希版本的出价。 由于目前几乎不可能找到两个（足够长的）值，其哈希值是相等的，因此投标人可通过该方式提交报价。 在投标结束后，投标人必须公开他们的出价：他们不加密的发送他们的出价，合约检查出价的哈希值是否与投标期间提供的相同。

另一个挑战是如何使拍卖同时做到 **绑定和秘密** : **唯一能阻止投标者在她赢得拍卖后不付款的方式是，让她将钱连同出价一起发出。** 但由于资金转移在 以太坊Ethereum 中不能被隐藏，因此任何人都可以看到转移的资金。

下面的合约通过接受任何大于最高出价的值来解决这个问题。 当然，因为这只能在披露阶段进行检查，有些出价可能是 **无效** 的， 并且，这是故意的(与高出价一起，它甚至提供了一个明确的标志来标识无效的出价): 投标人可以通过设置几个或高或低的无效出价来迷惑竞争对手。

```js
pragma solidity >0.4.23 <0.5.0;

contract BlindAuction {
    struct Bid {  // 
        bytes32 blindedBid;
        uint deposit;
    }

    address public beneficiary;
    uint public biddingEnd;
    uint public revealEnd;
    bool public ended;

    mapping(address => Bid[]) public bids;

    address public highestBidder;
    uint public highestBid;

    // 可以取回的之前的出价
    mapping(address => uint) pendingReturns;

    event AuctionEnded(address winner, uint highestBid);

    /// 使用 modifier 可以更便捷的校验函数的入参。
    /// `onlyBefore` 会被用于后面的 `bid` 函数：
    /// 新的函数体是由 modifier 本身的函数体，并用原函数体替换 `_;` 语句来组成的。
    modifier onlyBefore(uint _time) { require(now < _time); _; }
    modifier onlyAfter(uint _time) { require(now > _time); _; }

    constructor(
        uint _biddingTime,
        uint _revealTime,
        address _beneficiary
    ) public {
        beneficiary = _beneficiary;
        biddingEnd = now + _biddingTime;
        revealEnd = biddingEnd + _revealTime;
    }

    /// 可以通过 `_blindedBid` = keccak256(value, fake, secret)
    /// 设置一个秘密竞拍。
    /// 只有在出价披露阶段被正确披露，已发送的以太币才会被退还。
    /// 如果与出价一起发送的以太币至少为 “value” 且 “fake” 不为真，则出价有效。
    /// 将 “fake” 设置为 true ，然后发送满足订金金额但又不与出价相同的金额是隐藏实际出价的方法。
    /// 同一个地址可以放置多个出价。
    function bid(bytes32 _blindedBid)
        public
        payable
        onlyBefore(biddingEnd)
    {
        bids[msg.sender].push(Bid({
            blindedBid: _blindedBid,
            deposit: msg.value
        }));
    }

    /// 披露你的秘密竞拍出价。
    /// 对于所有正确披露的无效出价以及除最高出价以外的所有出价，你都将获得退款。
    function reveal(
        uint[] _values,
        bool[] _fake,
        bytes32[] _secret
    )
        public
        onlyAfter(biddingEnd)
        onlyBefore(revealEnd)
    {
        uint length = bids[msg.sender].length;
        require(_values.length == length);
        require(_fake.length == length);
        require(_secret.length == length);

        uint refund;
        for (uint i = 0; i < length; i++) {
            Bid storage bid = bids[msg.sender][i];
            (uint value, bool fake, bytes32 secret) =
                    (_values[i], _fake[i], _secret[i]);
            if (bid.blindedBid != keccak256(value, fake, secret)) {
                // 出价未能正确披露
                // 不返还订金
                continue;
            }
            refund += bid.deposit;
            if (!fake && bid.deposit >= value) {
                if (placeBid(msg.sender, value))
                    refund -= value;
            }
            // 使发送者不可能再次认领同一笔订金
            bid.blindedBid = bytes32(0);
        }
        msg.sender.transfer(refund);
    }

    // 这是一个 "internal" 函数， 意味着它只能在本合约（或继承合约）内被调用
    function placeBid(address bidder, uint value) internal
            returns (bool success)
    {
        if (value <= highestBid) {
            return false;
        }
        if (highestBidder != address(0)) {
            // 返还之前的最高出价
            pendingReturns[highestBidder] += highestBid;
        }
        highestBid = value;
        highestBidder = bidder;
        return true;
    }

    /// 取回出价（当该出价已被超越）
    function withdraw() public {
        uint amount = pendingReturns[msg.sender];
        if (amount > 0) {
            // 这里很重要，首先要设零值。
            // 因为，作为接收调用的一部分，
            // 接收者可以在 `transfer` 返回之前重新调用该函数。（可查看上面关于‘条件 -> 影响 -> 交互’的标注）
            pendingReturns[msg.sender] = 0;

            msg.sender.transfer(amount);
        }
    }

    /// 结束拍卖，并把最高的出价发送给受益人
    function auctionEnd()
        public
        onlyAfter(revealEnd)
    {
        require(!ended);
        emit AuctionEnded(highestBidder, highestBid);
        ended = true;
        beneficiary.transfer(highestBid);
    }
}
```

### 安全的远程购买

```js
pragma solidity ^0.4.22;

contract Purchase {
    uint public value;
    address public seller;
    address public buyer;
    enum State { Created, Locked, Inactive }
    State public state;

    //确保 `msg.value` 是一个偶数。
    //如果它是一个奇数，则它将被截断。
    //通过乘法检查它不是奇数。
    constructor() public payable {
        seller = msg.sender;
        value = msg.value / 2;
        require((2 * value) == msg.value, "Value has to be even.");
    }

    modifier condition(bool _condition) {
        require(_condition);
        _;
    }

    modifier onlyBuyer() {
        require(
            msg.sender == buyer,
            "Only buyer can call this."
        );
        _;
    }

    modifier onlySeller() {
        require(
            msg.sender == seller,
            "Only seller can call this."
        );
        _;
    }

    modifier inState(State _state) {
        require(
            state == _state,
            "Invalid state."
        );
        _;
    }

    event Aborted();
    event PurchaseConfirmed();
    event ItemReceived();

    ///中止购买并回收以太币。
    ///只能在合约被锁定之前由卖家调用。
    function abort()
        public
        onlySeller
        inState(State.Created)
    {
        emit Aborted();
        state = State.Inactive;
        seller.transfer(address(this).balance);
    }

    /// 买家确认购买。
    /// 交易必须包含 `2 * value` 个以太币。
    /// 以太币会被锁定，直到 confirmReceived 被调用。
    function confirmPurchase()
        public
        inState(State.Created)
        condition(msg.value == (2 * value))
        payable
    {
        emit PurchaseConfirmed();
        buyer = msg.sender;
        state = State.Locked;
    }

    /// 确认你（买家）已经收到商品。
    /// 这会释放被锁定的以太币。
    function confirmReceived()
        public
        onlyBuyer
        inState(State.Locked)
    {
        emit ItemReceived();
        // 首先修改状态很重要，否则的话，由 `transfer` 所调用的合约可以回调进这里（再次接收以太币）。
        state = State.Inactive;

        // 注意: 这实际上允许买方和卖方阻止退款 - 应该使用取回模式。
        buyer.transfer(value);
        seller.transfer(address(this).balance);
    }
}
```



## 深入理解Solidity

### 源文件结构

**结构**

```js
pragma solidity ^0.4.0;
```

源文件将既不允许低于 0.4.0 版本的编译器编译， 也不允许高于（包含） `0.5.0` 版本的编译器编译（第二个条件因使用 `^` 被添加）。 这种做法的考虑是，编译器在 0.5.0 版本之前不会有重大变更，所以可确保源代码始终按预期被编译。

**导入**

```js
import {symbol1 as alias, symbol2} from "filename";
...创建新的全局符号 alias 和 symbol2，分别从 "filename" 引用 symbol1 和 symbol2 。
```



```js
import * as symbolName from "filename";
创建一个新的全局符号 symbolName，其成员均来自 "filename" 中全局符号。
```



```js
import "filename";
此语句将从 “filename” 中导入所有的全局符号到当前全局作用域中（不同于 ES6，Solidity 是向后兼容的）。
```



用 `import "./x" as x;` 语句导入当前源文件同目录下的文件 `x` 。 如果用 `import "x" as x;` 代替，可能会引入不同的文件（在全局 `include directory` 中）。

```js
import "github.com/ethereum/dapp-bin/library/iterable_mapping.sol" as it_mapping;
solc:
solc module1:github.com/ethereum/dapp-bin/=/usr/local/dapp-bin/ \
module2:github.com/ethereum/dapp-bin/=/usr/local/dapp-bin_old/ \
source.sol
```



有另一种注释称为 natspec 注释，其文档还尚未编写。 它们是用三个反斜杠（`///`）或双星号开头的块（`/** ... */`）书写，它们应该直接在函数声明或语句上使用。

文档化函数、 标注形式校验通过的条件，和提供一个当用户试图调用一个函数时显示给用户的 **确认文本**。

```js
pragma solidity ^0.4.0;

/** @title 形状计算器。 */
contract shapeCalculator {
    /** @dev 求矩形表明面积与周长。
    * @param w 矩形宽度。
    * @param h 矩形高度。
    * @return s 求得表面积。
    * @return p 求得周长。
    */
    function rectangle(uint w, uint h) returns (uint s, uint p) {
        s = w * h;
        p = 2 * (w + h);
    }
}
```





### 合约结构

```js
状态变量是永久地存储在合约存储中的值。
uint storedData; // 状态变量

函数调用 可发生在合约内部或外部，且函数对其他合约有不同程度的可见性（ 可见性和 getter 函数）。
function bid() public payable { // 函数
        // ...
}

函数修饰器可以用来以声明的方式改良函数语义
modifier onlySeller() { // 修饰器
        require(
            msg.sender == seller,
            "Only seller can call this."
        );
        _;
    }

事件是能方便地调用以太坊虚拟机日志功能的接口。
    event HighestBidIncreased(address bidder, uint amount); // 事件
    function bid() public payable {
        // ...
        emit HighestBidIncreased(msg.sender, msg.value); // 触发事件
    }

struct Voter { // 结构
        uint weight;
        bool voted;
        address delegate;
        uint vote;
    }

枚举可用来创建由一定数量的“常量值”构成的自定义类型
enum State { Created, Locked, Inactive } // 枚举
```

### **类型**

```js
bool ：可能的取值为字面常数值 true 和 false 。

! （逻辑非）
&& （逻辑与， "and" ）
|| （逻辑或， "or" ）
== （等于）
!= （不等于）

int / uint ：分别表示有符号和无符号的不同位数的整型变量。 
支持关键字 uint8 到 uint256 （无符号，从 8 位到 256 位）以及 int8 到 int256，以 8 位为步长递增。 
uint 和 int 分别是 uint256 和 int256 的别名。

比较运算符： <= ， < ， == ， != ， >= ， > （返回布尔值）
位运算符： & ， | ， ^ （异或）， ~ （位取反）

除法总是会截断的（仅被编译为 EVM 中的 DIV 操作码）， 但如果操作数都是 字面常数（literals） （或者字面常数表达式），则不会截断。
除以零或者模零运算都会引发运行时异常。
移位运算的结果取决于运算符左边的类型。 表达式 x << y 与 x * 2**y 是等价的， x >> y 与 x / 2**y 是等价的。这意味对一个负数进行移位会导致其符号消失。 按负数位移动会引发运行时异常。
warning:
	由有符号整数类型负值右移所产生的结果跟其它语言中所产生的结果是不同的。 在 Solidity 中，右移和除是等价的，因此对一个负数进行右移操作会导致向 0 的取整（截断）。 而在其它语言中， 对负数进行右移类似于（向负无穷）取整。
    
百度：负数的移位计算  https://www.cnblogs.com/oldfish123/p/14941113.html
先转化成补码，左移运算一律在右端补0，右移运算一律在左端补符号数(负数符号位为1就补1，正数符号位为0就补0)
特别注意溢出问题：负数移位溢出之后的值一律为-1，正数移位溢出之后的值一律为0
```



`fixed` / `ufixed`：表示各种大小的有符号和无符号的定长浮点型。 在关键字 `ufixedMxN` 和 `fixedMxN` 中，`M` 表示该类型占用的位数，`N` 表示可用的小数位数。 `M` 必须能整除 8，即 8 到 256 位。 `N` 则可以是从 0 到 80 之间的任意数。 `ufixed` 和 `fixed` 分别是 `ufixed128x19` 和 `fixed128x19` 的别名。

Solidity 还没有完全支持定长浮点型。可以声明定长浮点型的变量，但不能给它们赋值或把它们赋值给其他变量。。

**地址类型**

`address`：地址类型存储一个 20 字节的值（以太坊地址的大小）。 地址类型也有成员变量，并作为所有合约的基础。

从 0.5.0 版本开始，合约不会从地址类型派生，但仍然可以显式地转换成地址类型。

**地址类型成员变量**

可以使用 `balance` 属性来查询一个地址的余额， 也可以使用 `transfer` 函数向一个地址发送 以太币Ether （以 wei 为单位）：

```js
address x = 0x123;
address myAddress = this;
if (x.balance < 10 && myAddress.balance >= 10) x.transfer(10);

send
send 是 transfer 的低级版本。如果执行失败，当前的合约不会因为异常而终止，但 send 会返回 false。
warning:
	在使用 send 的时候会有些风险：如果调用栈深度是 1024 会导致发送失败（这总是可以被调用者强制），如果接收者用光了 gas 也会导致发送失败。 所以为了保证 以太币Ether 发送的安全，一定要检查 send 的返回值，使用 transfer 或者更好的办法： 使用一种接收者可以取回资金的模式。
```

uint  256位  为      256/8 = 32 字节           byte32[] 其实也就是32字节是数组  比如      ["0xe68891e79a84e5a4a90000000000000000000000000000000000000000000000"]  （64位）

16进制对应4个比特 比如1001对应 9 . 1个字节对应两个16进制字符     



string 类型存储[字符串](https://so.csdn.net/so/search?q=字符串&spm=1001.2101.3001.7020)， 在solidity中使用了UTF-8格式来存储字符串。  是可变的字节长度，一般是1-3字节。

汉字占了3个字节，英文和特殊字符占了一个字节           一个汉字 ”天“=》 对应0xe5a4a9

**keccak256**

keccak256算法则可以将任意长度的输入压缩成(32字节)64位[16进制](https://so.csdn.net/so/search?q=16进制&spm=1001.2101.3001.7020)的数，且哈希碰撞的概率近乎为0.



- `**call`， `callcode` 和 `delegatecall`**

此外，为了与不符合 应用二进制接口Application Binary Interface(ABI) 的合约交互，于是就有了可以接受任意类型任意数量参数的 `call` 函数。 **这些参数会被打包到以 32 字节为单位的连续区域(calldata?)中存放。 其中一个例外是当第一个参数被编码成正好 4 个字节的情况。 在这种情况下，这个参数后边不会填充后续参数编码，以允许使用函数签名。**

```js
address nameReg = 0x72ba7d8e73fe8eb666ea66babc8116a41bfb10e2;
nameReg.call("register", "MyName");
nameReg.call(bytes4(keccak256("fun(uint256)")), a);
```

`call` 返回的布尔值表明了被调用的函数已经执行完毕（`true`）或者引发了一个 EVM 异常（`false`）。 无法访问返回的真实数据（为此我们需要事先知道编码和大小）。

可以使用 `.gas()` 修饰器modifier 调整提供的 gas 数量

```js
namReg.call.gas(1000000)("register", "MyName");
nameReg.call.gas(1000000).value(1 ether)("register", "MyName");
```

类似地，也可以使用 `delegatecall`： 区别在于只使用给定地址的代码，其它属性（存储，余额，……）都取自当前合约。 `delegatecall` 的目的是使用存储在另外一个合约中的库代码。 用户必须确保两个合约中的存储结构都适用于 delegatecall。 在 homestead 版本之前，只有一个功能类似但作用有限的 `callcode` 的函数可用，但它不能获取委托方的 `msg.sender` 和 `msg.value`。

这三个函数 `call`， `delegatecall` 和 `callcode` 都是非常低级的函数，应该只把它们当作 *最后一招* 来使用，因为它们破坏了 Solidity 的类型安全性。

所有合约都继承了地址（address）的成员变量，因此可以使用 `this.balance` 查询当前合约的余额。

不鼓励使用 `callcode`，在未来也会将其移除。

这三个函数都属于低级函数，需要谨慎使用。 具体来说，任何未知的合约都可能是恶意的。 你在调用一个合约的同时就将控制权交给了它，它可以反过来调用你的合约， 因此，当调用返回时要为你的状态变量的改变做好准备。





**定长字节数组**

关键字有：`bytes1`， `bytes2`， `bytes3`， ...， `bytes32`。`byte` 是 `bytes1` 的别名。

- 索引访问：如果 `x` 是 `bytesI` 类型，那么 `x[k]` （其中 `0 <= k < I`）返回第 `k` 个字节（只读）。

可以将 `byte[]` 当作字节数组使用，但这种方式非常浪费存储空间，准确来说，是在传入调用时，每个元素会浪费 31 字节。 更好地做法是使用 `bytes`。（传入调用，参数以32字节打包 ）

**变长字节数组**

`bytes`:

变长字节数组，参见 [数组](https://solidity-cn.readthedocs.io/zh/develop/types.html#arrays)。它并不是值类型。

`string`:

变长 UTF-8 编码字符串类型，参见 [数组](https://solidity-cn.readthedocs.io/zh/develop/types.html#arrays)。并不是值类型。

**枚举类型**

```js
    // 由于枚举类型不属于 |ABI| 的一部分，因此对于所有来自 Solidity 外部的调用，
    // "getChoice" 的签名会自动被改成 "getChoice() returns (uint8)"。
    // 整数类型的大小已经足够存储所有枚举类型的值，随着值的个数增加，
    // 可以逐渐使用 `uint16` 或更大的整数类型。
    function getChoice() public view returns (ActionChoices) {
        return choice;
    }

    function getDefaultChoice() public pure returns (uint) {
        return uint(defaultChoice);
    }
```



**函数类型**

函数类型是一种表示函数的类型。可以将一个函数赋值给另一个函数类型的变量，也可以将一个函数作为参数进行传递，还能在函数调用中返回函数类型变量。 函数类型有两类：- *内部（internal）* 函数和 *外部（external）* 函数：

内部函数只能在当前合约内被调用，更具体来说，在当前代码块内，调用一个内部函数是通过跳转到它的入口标签来实现的，就像在当前合约的内部调用一个函数。

外部函数由一个地址和一个函数签名组成，可以通过外部函数调用传递或者返回。

```js
function (<parameter types>) {internal|external} [pure|constant|view|payable] [returns (<return types>)]
```

函数类型**默认是内部函数，**因此不需要声明 `internal` 关键字。 与此相反的是，合约中的函数本身默认是 public 的，只有当它被当做类型名称时，默认才是内部函数。



当前合约的 public 函数既可以被当作内部函数也可以被当作外部函数使用。 如果想将一个函数当作内部函数使用，就用 `f` 调用，如果想将其当作外部函数，使用 `this.f` 。

除此之外，public（或 external）函数也有一个特殊的成员变量称作 `selector`，可以返回 [ABI 函数选择器](https://solidity-cn.readthedocs.io/zh/develop/abi-spec.html#abi-function-selector):

```js
pragma solidity ^0.4.16;

contract Selector {
  function f() public view returns (bytes4) {
    return this.f.selector;
  }
}
```

如果使用内部函数类型的例子:

```js
pragma solidity ^0.4.16;

library ArrayUtils {
  // 内部函数可以在内部库函数中使用，
  // 因为它们会成为同一代码上下文的一部分
  function map(uint[] memory self, function (uint) pure returns (uint) f)
    internal
    pure
    returns (uint[] memory r)
  {
    r = new uint[](self.length);
    for (uint i = 0; i < self.length; i++) {
      r[i] = f(self[i]);
    }
  }
  function reduce(
    uint[] memory self,
    function (uint, uint) pure returns (uint) f
  )
    internal
    pure
    returns (uint r)
  {
    r = self[0];
    for (uint i = 1; i < self.length; i++) {
      r = f(r, self[i]);
    }
  }
  function range(uint length) internal pure returns (uint[] memory r) {
    r = new uint[](length);
    for (uint i = 0; i < r.length; i++) {
      r[i] = i;
    }
  }
}

contract Pyramid {
  using ArrayUtils for *;
  function pyramid(uint l) public pure returns (uint) {
    return ArrayUtils.range(l).map(square).reduce(sum);
  }
  function square(uint x) internal pure returns (uint) {
    return x * x;
  }
  function sum(uint x, uint y) internal pure returns (uint) {
    return x + y;
  }
}
```



**没看懂**

另外一个使用外部函数类型的例子:

```js
pragma solidity ^0.4.11;

contract Oracle {
  struct Request {
    bytes data;
    function(bytes memory) external callback;
  }
  Request[] requests;
  event NewRequest(uint);
  function query(bytes data, function(bytes memory) external callback) public {
    requests.push(Request(data, callback));
    NewRequest(requests.length - 1);
  }
  function reply(uint requestID, bytes response) public {
    // 这里要验证 reply 来自可信的源
    requests[requestID].callback(response);
  }
}

contract OracleUser {
  Oracle constant oracle = Oracle(0x1234567); // 已知的合约
  function buySomething() {
    oracle.query("USD", this.oracleResponse);
  }
  function oracleResponse(bytes response) public {
    require(msg.sender == address(oracle));
    // 使用数据
  }
}
```

**引用类型**

函数参数（包括返回的参数）的数据位置默认是 `memory`， 局部变量的数据位置默认是 `storage`，状态变量的数据位置强制是 `storage` （这是显而易见的, 比如 余额 代码 之类的  需要永久存储）。

也存在第三种数据位置， `calldata` ，这是一块只读的，且不会永久存储的位置，用来存储函数参数。 外部函数的参数（非返回参数）的数据位置被强制指定为 `calldata` ，效果跟 `memory` 差不多。 **（32字节一个单位？）**

数据位置的指定非常重要，因为它们影响着赋值行为： 在 存储storage 和 内存memory 之间两两赋值，或者 存储storage 向状态变量（甚至是从其它状态变量）赋值都会创建一份独立的拷贝。 然而状态变量向局部变量赋值时仅仅传递一个引用，而且这个引用总是指向状态变量，因此后者改变的同时前者也会发生改变。 另一方面，从一个 内存memory 存储的引用类型向另一个 内存memory 存储的引用类型赋值并不会创建拷贝。

```js
pragma solidity ^0.4.0;

contract C {
    uint[] x; // x 的数据存储位置是 storage

    // memoryArray 的数据存储位置是 memory
    function f(uint[] memoryArray) public {
        x = memoryArray; // 将整个数组拷贝到 storage 中，可行
        var y = x;  // 分配一个指针（其中 y 的数据存储位置是 storage），可行
        y[7]; // 返回第 8 个元素，可行
        y.length = 2; // 通过 y 修改 x，可行
        delete x; // 清除数组，同时修改 y，可行
        // 下面的就不可行了；需要在 storage 中创建新的未命名的临时数组， /
        // 但 storage 是“静态”分配的：
        // y = memoryArray;              XXXXXXXXXXXXX ???????? 就是说创建只能现在内存创建？然后只能拷贝到storage吗
        // 下面这一行也不可行，因为这会“重置”指针，
        // 但并没有可以让它指向的合适的存储位置。
        // delete y;             XXXXXXXXXXXXX         不能出现空指针

        g(x); // 调用 g 函数，同时移交对 x 的引用
        h(x); // 调用 h 函数，同时在 memory 中创建一个独立的临时拷贝
    }

    function g(uint[] storage storageArray) internal {}
    function h(uint[] memoryArray) public {}
}
```

**总结**

- **强制指定的数据位置：**

  **外部函数的参数（不包括返回参数）： calldata**

  **状态变量： storage**

- **默认数据位置：**

  **函数参数（包括返回参数）： memory**

  **所有其它局部变量： storage**

**数组类型**

数组可以在声明时指定长度，也可以动态调整大小。 对于 **存储storage 的数组来说，元素类型可以是任意的**（即元素也可以是数组类型，映射类型或者结构体）。 **对于 内存memory 的数组来说，元素类型不能是映射类型，如果作为 public 函数的参数，它只能是 ABI 类型。**

一个元素类型为 `T`，固定长度为 `k` 的数组可以声明为 `T[k]`，而动态数组声明为 `T[]`。 举个例子，一个长度为 5，元素类型为 `uint` 的动态数组的数组，应声明为 `uint[][5]` （注意这里跟其它语言比，数组长度的声明位置是反的）。 要访问第三个动态数组的第二个元素，你应该使用 x\[2][1]（数组下标是从 0 开始的，且访问数组时的下标顺序与声明时相反，也就是说，x[2] 是从右边减少了一级）。。

`bytes` 和 `string` 类型的变量是特殊的数组。 `bytes` 类似于 `byte[]`，但它在 calldata 中会被“紧打包”（译者注：将元素连续地存在一起，不会按每 32 字节一单元的方式来存放）。 `string` 与 `bytes` 相同，但（暂时）不允许用长度或索引来访问。

> 要访问以字节表示的字符串 `s`，请使用 `bytes(s).length` / `bytes(s)[7] = 'x';`。 注意这时你访问的是 UTF-8 形式的低级 bytes 类型，而不是单个的字符。

**内存数组**

可使用 `new` 关键字在内存中创建变长数组。 与 存储storage 数组相反的是，你 *不能* 通过修改成员变量 `.length` 改变 内存memory 数组的大小。

```js
contract C {
    function f(uint len) public pure {
        uint[] memory a = new uint[](7);
        bytes memory b = new bytes(len);
        // 这里我们有 a.length == 7 以及 b.length == len
        a[6] = 8;
    }
}
```

```js
contract C {
    function f() public pure {
        g([uint(1), 2, 3]);
    }
    function g(uint[3] _data) public pure {
        // ...
    }
}
```

`[1, 2, 3]` 的类型是 `uint8[3] memory`，因为其中的每个字面常数的类型都是 `uint8`。 正因为如此，有必要将上面这个例子中的第一个元素转换成 `uint` 类型。 目前需要注意的是，定长的 内存memory 数组并不能赋值给变长的 内存memory 数组，下面是个反例：

```js
contract C {
    function f() public {
        // 这一行引发了一个类型错误，因为 unint[3] memory
        // 不能转换成 uint[] memory。
        uint[] x = [uint(1), 3, 4];
    }
}
```

**length**

数组有 `length` 成员变量表示当前数组的长度。 动态数组可以在 存储storage （而不是 内存memory ）中通过改变成员变量 `.length` 改变数组大小。一经创建，内存memory 数组的大小就是固定的（但却是动态的，也就是说，它依赖于运行时的参数）。

**push**

变长的 存储storage 数组以及 `bytes` 类型（而不是 `string` 类型）都有一个叫做 `push` 的成员函数，它用来附加新的元素到数组末尾。 **这个函数将返回新的数组长度。**

注意在函数中使用结构体时，一个结构体是如何赋值给一个局部变量（默认存储位置是 存储storage ）的。 在这个过程中并没有拷贝这个结构体，而是保存一个引用，所以对局部变量成员的赋值实际上会被写入状态。

当然，你也可以直接访问结构体的成员而不用将其赋值给一个局部变量，就像这样， `campaigns[campaignID].amount = 0`。

**映射**

它们在实际的初始化过程中创建每个可能的 key， 并将其映射到字节形式全是零的值：一个类型的 [默认值](https://solidity-cn.readthedocs.io/zh/develop/control-structures.html#default-value)。然而下面是映射与哈希表不同的地方： **在映射中，实际上并不存储 key，而是存储它的 `keccak256` 哈希值，从而便于查询实际的值。**

也没有 key 的集合或 value 的集合的概念。

只有状态变量（或者在 internal 函数中的对于存储变量的引用）可以使用映射类型。

**删除**

`delete a` 的结果是将 `a` 的类型在初始化时的值赋值给 `a`。即对于整型变量来说，相当于 `a = 0`， 但 delete 也适用于数组，对于动态数组来说，是将数组的长度设为 0，而对于静态数组来说，是将数组中的所有元素重置。 如果对象是结构体，则将结构体中的所有属性重置。

`delete` 对**整个映射是无效的**（因为映射的键可以是任意的，通常也是未知的）。 因此在你删除一个结构体时，结果将重置所有的非映射属性，这个过程是递归进行的，除非它们是映射。 然而**，单个的键及其映射的值是可以被删除的。**

理解 `delete a` 的效果就像是给 `a` 赋值很重要，换句话说，这相当于在 `a` 中存储了一个新的对象。

```js
pragma solidity ^0.4.0;

contract DeleteExample {
    uint data;
    uint[] dataArray;

    function f() public {
        uint x = data;
        delete x; // 将 x 设为 0，并不影响数据
        delete data; // 将 data 设为 0，并不影响 x，因为它仍然有个副本
        uint[] storage y = dataArray;
        delete dataArray;
        // 将 dataArray.length 设为 0，但由于 uint[] 是一个复杂的对象，y 也将受到影响，
        // 因为它是一个存储位置是 storage 的对象的别名。
        // 另一方面："delete y" 是非法的，引用了 storage 对象的局部变量只能由已有的 storage 对象赋值。
         // 也就是必须只想一个storage对象  不能是空指针
    }
}
```



**隐式转换**

只要值类型之间的转换在语义上行得通，而且转换的过程中没有信息丢失，那么隐式转换基本都是可以实现的： `uint8` 可以转换成 `uint16`，`int128` 转换成 `int256`，但 `int8` 不能转换成 `uint256` （因为 `uint256` 不能涵盖某些值，例如，`-1`）。 更进一步来说，无符号整型可以转换成跟它大小相等或更大的字节类型，但反之不能。 任何可以转换成 `uint160` 的类型都可以转换成 `address` 类型

**显式转换**

```
int8 y = -3;
uint x = uint(y);
```

这段代码的最后，`x` 的值将是 `0xfffff..fd` （64 个 16 进制字符），因为这是 -3 的 256 位补码形式。

如果一个类型显式转换成更小的类型，相应的高位将被舍弃

```
uint32 a = 0x12345678;
uint16 b = uint16(a); // 此时 b 的值是 0x5678
```



**warning:**

类型只能从第一次赋值中推断出来，因此以下代码中的循环是无限的， 原因是``i`` 的类型是 `uint8`，而这个类型变量的最大值比 `2000` 小。 `for (var i = 0; i < 2000; i++) { ... }`



### 单位和全局变量

区块和交易属性

**block.blockhash(uint blockNumber) returns (bytes32)：指定区块的区块哈希——仅可用于最新的 256 个区块且不包括当前区块；而 blocks 从 0.4.22 版本开始已经不推荐使用，由 blockhash(uint blockNumber) 代替**
**block.coinbase (address): 挖出当前区块的矿工地址**
**block.difficulty (uint): 当前区块难度**
**block.gaslimit (uint): 当前区块 gas 限额**
**block.number (uint): 当前区块号**
**block.timestamp (uint): 自 unix epoch 起始当前区块以秒计的时间戳**
**gasleft() returns (uint256)：剩余的 gas**
**msg.data (bytes): 完整的 calldata**
**msg.gas (uint): 剩余 gas - 自 0.4.21 版本开始已经不推荐使用，由 gesleft() 代替**
**msg.sender (address): 消息发送者（当前调用）**
**msg.sig (bytes4): calldata 的前 4 字节（也就是函数标识符）**
**msg.value (uint): 随消息发送的 wei 的数量**
**now (uint): 目前区块时间戳（block.timestamp）**
**tx.gasprice (uint): 交易的 gas 价格**
**tx.origin (address): 交易发起者（完全的调用链）**

 **note** : 对于每一个**外部函数**调用，包括 msg.sender 和 msg.value 在内所有 msg 成员的值都会变化。这里包括对库函数的调用。

> 不要依赖 `block.timestamp`、 `now` 和 `blockhash` 产生随机数，除非你知道自己在做什么
>
> 时间戳和区块哈希在一定程度上都可能受到挖矿矿工影响。例如，挖矿社区中的恶意矿工可以用某个给定的哈希来运行赌场合约的 payout 函数，而如果他们没收到钱，还可以用一个不同的哈希重新尝试。



基于可扩展因素，区块哈希不是对所有区块都有效。你仅仅可以访问最近 256 个区块的哈希，其余的哈希均为零。

**错误处理**

>`assert(bool condition)`:
>
>如果条件不满足，则使当前交易没有效果 — 用于检查内部错误。
>
>`require(bool condition)`:
>
>如果条件不满足则撤销状态更改 - 用于检查由输入或者外部组件引起的错误。
>
>`require(bool condition, string message)`:
>
>如果条件不满足则撤销状态更改 - 用于检查由输入或者外部组件引起的错误，可以同时提供一个错误消息。
>
>`revert()`:
>
>终止运行并撤销状态更改。
>
>`revert(string reason)`:
>
>终止运行并撤销状态更改，可以同时提供一个解释性的字符串。

**地址相关**

`<address>.balance` (`uint256`):

以 Wei 为单位的 [地址类型](https://solidity-cn.readthedocs.io/zh/develop/types.html#address) 的余额。

`<address>.transfer(uint256 amount)`:

向 [地址类型](https://solidity-cn.readthedocs.io/zh/develop/types.html#address) 发送数量为 amount 的 Wei，失败时抛出异常，发送 2300 gas 的矿工费，不可调节。

`<address>.send(uint256 amount) returns (bool)`:

向 [地址类型](https://solidity-cn.readthedocs.io/zh/develop/types.html#address) 发送数量为 amount 的 Wei，失败时返回 `false`，发送 2300 gas 的矿工费用，不可调节。

`<address>.call(...) returns (bool)`:

发出低级函数 `CALL`，失败时返回 `false`，发送所有可用 gas，可调节。

`<address>.callcode(...) returns (bool)`：

发出低级函数 `CALLCODE`，失败时返回 `false`，发送所有可用 gas，可调节。

`<address>.delegatecall(...) returns (bool)`:

发出低级函数 `DELEGATECALL`，失败时返回 `false`，发送所有可用 gas，可调节。



>使用 send 有很多危险：如果调用栈深度已经达到 1024（这总是可以由调用者所强制指定），转账会失败；并且如果接收者用光了 gas，转账同样会失败。为了保证以太币转账安全，总是检查 `send` 的返回值，利用 `transfer` 或者下面更好的方式： 用这种接收者取回钱的模式。

>如果在通过低级函数 delegatecall 发起调用时需要访问存储中的变量，那么这两个合约的存储中的变量定义顺序需要一致，以便被调用的合约代码可以正确地通过变量名访问合约的存储变量。 这当然不是指像在高级的库函数调用时所传递的存储变量指针那样的情况。

**合约相关**

- `this` (current contract's type):

  当前合约，可以明确转换为 [地址类型](https://solidity-cn.readthedocs.io/zh/develop/types.html#address)。

- `selfdestruct(address recipient)`:

  销毁合约，并把余额发送到指定 [地址类型](https://solidity-cn.readthedocs.io/zh/develop/types.html#address)。

- `suicide(address recipient)`:

  与 selfdestruct 等价，但已不推荐使用。



### 表达式和控制结构

输出

```js
contract Simple {
    function arithmetics(uint _a, uint _b)
        public
        pure
        returns (uint o_sum, uint o_product)
    {
        o_sum = _a + _b;
        o_product = _a * _b;
    }
}
```

输出参数名可以被省略。输出值也可以使用 `return` 语句指定。 `return` 语句也可以返回多值，参阅：ref:multi-return。 返回的输出参数被初始化为 0；如果它们没有被显式赋值，它们就会一直为 0。

**内部函数调用**

当前合约中的函数可以直接（“从内部”）调用，也可以递归调用

**外部函数调用**

```js
如果想要调用其他合约的函数，需要外部调用。对于一个外部调用，所有的函数参数都需要被复制到内存。
当调用其他合约的函数时，随函数调用发送的 Wei 和 gas 的数量可以分别由特定选项 .value() 和 .gas() 指定:

pragma solidity ^0.4.0;

contract InfoFeed {
    function info() public payable returns (uint ret) { return 42; }
}

contract Consumer {
    InfoFeed feed;
    function setFeed(address addr) public { feed = InfoFeed(addr); }
    function callFeed() public { feed.info.value(10).gas(800)(); }  // .value()用于转账
}
```

`payable` 修饰符要用于修饰 `info`，否则，.value() 选项将不可用。

`feed.info.value(10).gas(800)` 只（局部地）设置了与函数调用一起发送的 Wei 值和 gas 的数量，只有最后的圆括号执行了真正的调用。如果被调函数所在合约不存在（也就是账户中不包含代码）或者被调用合约本身抛出异常或者 gas 用完等，函数调用会抛出异常。

通过 `new` **创建合约**

```js
pragma solidity ^0.4.0;

contract D {
    uint x;
    function D(uint a) public payable {
        x = a;
    }
}

contract C {
    D d = new D(4); // 将作为合约 C 构造函数的一部分执行

    function createD(uint arg) public {
        D newD = new D(arg);
    }

    function createAndEndowD(uint arg, uint amount) public payable {
                //随合约的创建发送 ether
        D newD = (new D).value(amount)(arg);
    }
}
```

如示例中所示，使用 `.value（）` 选项创建 `D` 的实例时可以转发 Ether，但是不可能限制 gas 的数量。如果创建失败（可能因为栈溢出，或没有足够的余额或其他问题），会引发异常。

**元组**

Solidity 内部允许元组 (tuple) 类型，也就是一个在编译时元素数量固定的对象列表，列表中的元素可以是不同类型的对象。这些元组可以用来同时返回多个数值，也可以用它们来同时给多个新声明的变量或者既存的变量（或通常的 LValues）：

**错误**

`revert` 函数可以用来标记错误并恢复当前的调用。 `revert` 调用中包含有关错误的详细信息是可能的，这个消息会被返回给调用者。

`assert` 函数只能用于测试内部错误，并检查非变量。 `require` 函数用于确认条件有效性，例如输入变量，或合约状态变量是否满足条件，或验证外部合约调用返回的值。



**warning:**

> 作为 EVM 设计的一部分，如果被调用合约帐户不存在，则低级函数 `call` ， `delegatecall` 和 `callcode` 将返回 success。因此如果需要使用低级函数时，必须在调用之前检查被调用合约是否存在。





## 合约

Solidity 合约类似于面向对象语言中的类。合约中有用于数据持久化的状态变量，和可以修改状态变量的函数。 调用另一个合约实例的函数时，会执行一个 EVM 函数调用，这个操作会切换执行时的上下文，这样，前一个合约的状态变量就不能访问了。

**创建合约**

```js
pragma solidity ^0.4.16;

contract OwnedToken {
    // TokenCreator 是如下定义的合约类型.
    // 不创建新合约的话，也可以引用它。
    TokenCreator creator;
    address owner;
    bytes32 name;

    // 这是注册 creator 和设置名称的构造函数。
    function OwnedToken(bytes32 _name) public {
        // 状态变量通过其名称访问，而不是通过例如 this.owner 的方式访问。
        // 这也适用于函数，特别是在构造函数中，你只能像这样（“内部地”）调用它们，
        // 因为合约本身还不存在。 不能直接使用this 指针
        owner = msg.sender;
        // 从 `address` 到 `TokenCreator` ，是做显式的类型转换
        // 并且假定调用合约的类型是 TokenCreator，没有真正的方法来检查这一点。
        creator = TokenCreator(msg.sender);
        name = _name;
    }

    function changeName(bytes32 newName) public {
        // 只有 creator （即创建当前合约的合约）能够更改名称 —— 因为合约是隐式转换为地址的，
        // 所以这里的比较是可行的。
        if (msg.sender == address(creator))
            name = newName;
    }

    function transfer(address newOwner) public {
        // 只有当前所有者才能发送 token。
        if (msg.sender != owner) return;
        // 我们也想询问 creator 是否可以发送。
        // 请注意，这里调用了一个下面定义的合约中的函数。
        // 如果调用失败（比如，由于 gas 不足），会立即停止执行。
        if (creator.isTokenTransferOK(owner, newOwner))
            owner = newOwner;
    }
}

contract TokenCreator {
    function createToken(bytes32 name)
       public
       returns (OwnedToken tokenAddress)
    {
        // 创建一个新的 Token 合约并且返回它的地址。
        // 从 JavaScript 方面来说，返回类型是简单的 `address` 类型，因为
        // 这是在 ABI 中可用的最接近的类型。
        return new OwnedToken(name);
    }

    function changeName(OwnedToken tokenAddress, bytes32 name)  public {
        // 同样，`tokenAddress` 的外部类型也是 `address` 。
        tokenAddress.changeName(name);
    }

    function isTokenTransferOK(address currentOwner, address newOwner)
        public
        view
        returns (bool ok)
    {
        // 检查一些任意的情况。
        address tokenAddress = msg.sender;
        return (keccak256(newOwner) & 0xff) == (bytes20(tokenAddress) & 0xff);
    }
}
```






















































