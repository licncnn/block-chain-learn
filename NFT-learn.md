# ERC-721 非同质化代币标准

非同质化代币（NFT）用于以唯一的方式标识某人或者某物。

 所有 NFTs 都有一个 `uint256` 变量，名为 `tokenId`，所以对于任何 ERC-721 合约，这对值`(contract address, tokenId)` 必须是全局唯一的。

ERC-721是一个在智能合约中实现代币 API 的非同质化代币标准。

它提供了一些功能，例如将代币从一个帐户转移到另一个帐户，获取帐户的当前代币余额，获取代币的所有者，以及整个网络的可用代币总供应量。 除此之外，它还具有其他功能，例如批准帐户中一定数量的代币可以被第三方帐户转移。

如果一个智能合约实现了下列方法和事件，它就可以被称为 ERC-721 非同质化代币合约。 一旦被部署，它将负责跟踪在以太坊上创建的代币。

```js
function balanceOf(address _owner) external view returns (uint256);
function ownerOf(uint256 _tokenId) external view returns (address);
function safeTransferFrom(address _from, address _to, uint256 _tokenId, bytes data) external payable;
function safeTransferFrom(address _from, address _to, uint256 _tokenId) external payable;
function transferFrom(address _from, address _to, uint256 _tokenId) external payable;
function approve(address _approved, uint256 _tokenId) external payable;
function setApprovalForAll(address _operator, bool _approved) external;
function getApproved(uint256 _tokenId) external view returns (address);
function isApprovedForAll(address _owner, address _operator) external view returns (bool);
```
事件

```java
event Transfer(address indexed _from, address indexed _to, uint256 indexed _tokenId);
event Approval(address indexed _owner, address indexed _approved, uint256 indexed _tokenId);
event ApprovalForAll(address indexed _owner, address indexed _operator, bool _approved);
```


**术语==== 有利于理解合约中的变量**

**Airdrop**

Airdrop就是空投，用来指代奖金或免费收藏品的术语。 这是一种推广新NFT或增加现有NFT受欢迎程度的方式。

因此，Airdrop是用于增加NFT收藏用户群的促销工具。 空投NFT也是对其持有者的忠诚度，或对项目在社交媒体上享有积极回响的一种奖励。

检查空投的来源很重要。 虽然来自知名项目的空投当然值得一试，但有些诈骗者使用这种方法窃取私人信息。 必须注意，若突然收到陌生电邮传来的不知名NFT，那很可能是一个骗局。

**Drop**

Drop 代表推出。 这个词不仅与NFT世界相关联，而且也越来越多地用于其他产品，例如音乐专辑和商品。

除非特别限制，否则在Drop时，收藏品可直接在市场上进行交易，并以底价（floor price）开始交易。

 **Flip**

当交易者快速买卖NFT时，该交易被称为Flip。 “快速转售”并不一定意味着在几小时内卖出； 也可以是购买后的几天。

Flip主要由那些想从NFT中迅速获利的人完成，一般看准NFT在短时间内仍然会保持高需求。 这类似股票市场交易，交易者在几天内买卖有前途的股票以获取利润，在此期间股票的价值仍会继续上涨。

**Floor Price**

Floor Price指NFT的底价。 当一个项目在NFT平台上架时，交易以底价出售。 这是每个想从收藏中获取代币的人所需支付的最低费用。

底价会随着时间不断变化。 如果是有名的系列，底价势必上涨。 目前购买BAYC代币的底价是101 ETH（以太币，相等于约33万美元）——这表明该系列中的每一只猿猴有多抢手。

**Gas**

Gas基本上是你在NFT平台上进行任何交易所需支付的费用，又称Gas费用。 在某些平台中，从铸币到NFT买卖的每一步都需要支付Gas。

Gas是通过加密货币支付的。 由于大多数NFT存在于以太坊区块链网络（Ethereum blockchain network）上，因此Gas的首选数字货币是以太币（Ether）。

**Minting**

Minting，既“铸造”的意思，是最值得注意的NFT术语之一，它是将数字文件（digital files）转换为用于NFT交易的数字资产（digital assets）的过程。 通过这种方式，任何人都可以从自己的文件中创建自己的NFT，以保存为独特的代币或在NFT平台上进行交易。

在OpenSea和Rarible等NFT交易平台的帮助下，铸造NFT变得相当容易。 你需要做的就是将加密钱包链接到平台，上传需要转换为NFT的文件并使用平台上的工具进行铸造。

**PFP**

PFP是 Profile Picture 的缩写，也就个人资料图片。 简单来说，当一个NFT代币看起来像一张头像时，它就可以称为PFP。 BAYC和CryptoPunks这两个创作，就是PFP的最佳例子。

LarvaLabs的CryptoPunks是第一个基于PFP类型的NFT 项目。 所有CryptoPunks都是像素化的角色，它们的持有者可以将其用作社交媒体上的个人资料图片。 BAYC和MAYC（Mutant Ape Yacht Club）也是如此。

**Rug Pull**

简单来说，Rug Pull是在NFT世界里的诈骗行为；很多案例都是容易上当的爱好者被引诱投资NFT。 NFT的价格被推高“时机”成熟时，诈骗者就会轻松拿走利润。 一旦发生这种情况，NFT的价值就会下降到零，这也意味着投资者将全部损失。

**Staking**

最重要的NFT术语之一是“质押”，即NFT持有者在一段时间内“锁定”他们的收藏，以获得更好的投资回报。

这有点像银行提供的定期存款。 在NFT世界里，资产被锁定在去中心化金融 平台（DeFi）中。 奖励是根据质押的NFT数量和年收益率（APY）产生的，年收益率大致定义为一年内、考虑到复利（compound interest）的投资的实际收益率。

这个投资策略允许持有者在不出售NFT的情况下从NFT中赚钱。





# Akutar合约漏洞导致34M美元资金被锁住 --案例

合约地址  https://etherscan.io/address/0xf42c318dbfbaab0eee040279c6a2588fa01a961d

发布交易的交易![1667899888610](.\assets\16678asdasfasf99888610.png)

分析一下这笔交易个各个参数

对于任意一个交易

<img src=".\assets\24719032-d44ea1031ac7d5d0.webp" alt="isg" style="zoom:50%;" />

Transaction Fee: 该交易需要的手续费，Transaction Fee = Gas Price * Gas Used，对应上面的数据就是：Transaction Fee = 82.768620951 * 46458 = 3845264.592141558 Gwei = 0.003845264592141558 ETH

Gas Price：该价格随时波动，Gas Price = Base + Max Priority，当前为：82.768620951 Gwei。

Gas Limit & Usage by Txn：Gas Limit 相对固定，为了防止部分智能合约存在漏洞，消耗完自己的代币。Gsage by Txn 取决于每个智能合约的复杂度，如果 Gas Limit < Gas Used，则会收取 Gas 费但是操作会失败。

Gas Fees：Base 是基础费，Max 是最高费，**Max Priority 是给矿工的小费**。Gas Price = Base + Max Priority。当 Max > Base + Max Priority 时，剩余部分返还给用户；当 Max < Base + Max Priority 时，不交易，等待 Base 下降（也就是手续费下降），直到 Max >= Base + Max Priority 才打包交易。这样可以为用户节约手续费，如表：

| 用户 | Max    | Base | Max Priority | Gas fees |                |
| ---- | ------ | ---- | ------------ | -------- | -------------- |
| A    | 50Gwei | 20   | 2            | 22       | 先于B执行      |
| B    | 50Gwei | 30   | 1            | 31       | A 执行后执行   |
| C    | 50Gwei | 60   | 1            | 61       | 等待 Base 下降 |

Burnt & Txn Savings Fees**：燃烧掉的 Gas，Burnt = Gas Base * Gas Used；Txn Savings Fees 是交易剩下的 Gas，退还给用户。Txn Savings Fees = (Gas Max  - Gas Base - Gas Max Priority) * Gas Used。

等于是手续费， 一部分烧掉了，一部分给了矿工，    最后返还给用户一部分了。







==**AkuAuction**==

它使用了一种比较独特的荷兰拍方式。
传统的拍卖方式是设置一个低价，然后大家向上叫价，最终出价最高者可购买，这是英式拍卖；
荷兰式拍卖则是先设置一个最高价，然后逐渐的降价，最终有人在某个价格点出手将其买下来，
荷兰拍更考验人性，因为每个人都想等最低价，但是都怕别人先于自己购买。



1.合约没有reanfi的保护   2.没有禁止合约之间的调用

3.是一个分发的代码  相当于是dauge auction的代码  不涉及任何的nft  mint合约与token合约是分开的

4.荷兰拍 ， 价格往下降的时候，如果是高价买入，则合约会自动补差价

```js
// File: workspaces/default_workspace/samuraisanta.sol
pragma solidity 0.8.13;
interface akuNFT {
    function airdropProgress() external view returns(uint256);
}

contract AkuAuction is Ownable {   // 继承
    using Strings for uint256;
address payable immutable project;

uint256 public maxNFTs = 15000;
uint256 public totalForAuction = 5495; //529 + 2527 + 6449

struct bids { // 结构体 bids
    address bidder;  //投标者
    uint80 price;   // 价格
    uint8 bidsPlaced;   
    uint8 finalProcess; //0: Not processed 未处理, 1: refunded 已退款, 2: withdrawn 撤销  
}

uint256 private constant DURATION = 126 minutes;  // 持续时间
uint256 public immutable startingPrice;  //起拍价格
uint256 public immutable startAt;       // 开始时间
uint256 public expiresAt;          // 过期时间
uint256 public immutable discountRate;  // 折扣率
mapping(address=>uint256) public mintPassOwner;  // 铸币者
uint256 public constant mintPassDiscount = 0.5 ether; // 铸币优惠0.5个
mapping(address => uint256) public personalBids; // 地址到int
mapping(uint256 => bids) public allBids;  // 
uint256 public bidIndex = 1; // 投标的索引
uint256 public totalBids;  //所有投标人总数
uint256 public totalBidValue; // 一共投标多少钱
uint256 public maxBids = 3; // 
uint256 public refundProgress = 1;

akuNFT public akuNFTs;

constructor(address _project,   // 构造函数
    uint256 startingTime,
    uint256 _startingPrice,
    uint256 _discountRate)
{
    project = payable(_project); // 可接受付款

    startingPrice = _startingPrice; //初始价格
    startAt = startingTime;     // 开始时间
    expiresAt = startAt + DURATION; // 结束时间
    discountRate = _discountRate; // 折扣
    // 折扣不能太低  否则出错
    require(_startingPrice >= _discountRate * (DURATION/6 minutes), "Starting price less than minimum");
}

function getPrice() public view returns (uint80) {
    uint256 currentTime = block.timestamp;
    if(currentTime > expiresAt) currentTime = expiresAt;
    uint256 timeElapsed = (currentTime - startAt) / 6 minutes;
    uint256 discount = discountRate * timeElapsed;
    return uint80(startingPrice - discount);
}

function bid(uint8 amount) external payable {  // 参与竞拍
    _bid(amount, msg.value);
}

receive() external payable {  
    revert("Please use the bid function");
}

function _bid(uint8 amount, uint256 value) internal {   // 参与竞拍 实际调用的函数
    require(block.timestamp > startAt, "Auction not started yet");
    require(block.timestamp < expiresAt, "Auction expired");
    uint80 price = getPrice();
    uint256 totalPrice = price * amount;
    if (value < totalPrice) {
        revert("Bid not high enough");
    }
    
    uint256 myBidIndex = personalBids[msg.sender];
    bids memory myBids;
    uint256 refund;

    if (myBidIndex > 0) {
        myBids = allBids[myBidIndex];
        refund = myBids.bidsPlaced * (myBids.price - price);
    }
    uint256 _totalBids = totalBids + amount;
    myBids.bidsPlaced += amount;

    if (myBids.bidsPlaced > maxBids) {
        revert("Bidding limits exceeded");
    }

    if(_totalBids > totalForAuction) {
        revert("Auction Full");
    } else if (_totalBids == totalForAuction) {
        expiresAt = block.timestamp; //Auction filled
    }

    myBids.price = price;

    if (myBidIndex > 0) {
        allBids[myBidIndex] = myBids;
    } else {
        myBids.bidder = msg.sender;
        personalBids[msg.sender] = bidIndex;
        allBids[bidIndex] = myBids;
        bidIndex++;
    }
    
    totalBids = _totalBids;
    totalBidValue += totalPrice;

    refund += value - totalPrice;
    if (refund > 0) {
        (bool sent, ) = msg.sender.call{value: refund}("");
        require(sent, "Failed to refund bidder");
    }
}
/// 
function loadMintPassOwners(address[] calldata owners, uint256[] calldata amounts) external onlyOwner {
    for (uint256 i = 0; i < owners.length; i++) {
        mintPassOwner[owners[i]] = amounts[i];
    }
}

function myBidCount(address user) public view returns(uint256) {
    return allBids[personalBids[user]].bidsPlaced;
}
function myBidData(address user) external view returns(bids memory) {
    return allBids[personalBids[user]];
}

function setNFTContract(address _contract) external onlyOwner {
    akuNFTs = akuNFT(_contract);
}

function emergencyWithdraw() external {
    require(block.timestamp > expiresAt + 3 days, "Please wait for airdrop period.");
    
    bids memory bidData = allBids[personalBids[msg.sender]];
    require(bidData.bidsPlaced > 0, "No bids placed");
    require(bidData.finalProcess == 0, "Refund already processed");

    allBids[personalBids[msg.sender]].finalProcess = 2;
    (bool sent, ) = bidData.bidder.call{value: bidData.price * bidData.bidsPlaced}("");
    require(sent, "Failed to refund bidder");
}

function processRefunds() external {  // 荷兰拍  大规模补差价的函数  external
  require(block.timestamp > expiresAt, "Auction still in progress");
  uint256 _refundProgress = refundProgress;
  uint256 _bidIndex = bidIndex;
  require(_refundProgress < _bidIndex, "Refunds already processed");
  
  uint256 gasUsed;
  uint256 gasLeft = gasleft();
  uint256 price = getPrice();
  
  for (uint256 i=_refundProgress; gasUsed < 5000000 && i < _bidIndex; i++) {
      bids memory bidData = allBids[i];
      if (bidData.finalProcess == 0) {
        uint256 refund = (bidData.price - price) * bidData.bidsPlaced;
        uint256 passes = mintPassOwner[bidData.bidder];
        if (passes > 0) {
            refund += mintPassDiscount * (bidData.bidsPlaced < passes ? bidData.bidsPlaced : passes);
        }
        allBids[i].finalProcess = 1;
        if (refund > 0) {
            // 谁都可以调用 并且涉及了金钱的转移    1.禁止合约call 合约  2.only owner call 3.金钱转移
            (bool sent, ) = bidData.bidder.call{value: refund}("");  //vulnable  call返回true of false 
            require(sent, "Failed to refund bidder");
        }
      }
      
      gasUsed += gasLeft - gasleft();
      gasLeft = gasleft();
      _refundProgress++;
  }

  refundProgress = _refundProgress;
}

function claimProjectFunds() external onlyOwner {
    require(block.timestamp > expiresAt, "Auction still in progress");  // 提款必须在所有的拍卖进程完成后进行。
    require(refundProgress >= totalBids, "Refunds not yet processed");  //  提款只能在所有用户都完成退款后才可以提款。
    require(akuNFTs.airdropProgress() >= totalBids, "Airdrop not complete"); // 空投全部完成后才可以提款

    (bool sent, ) = project.call{value: address(this).balance}("");
    require(sent, "Failed to withdraw");        
}

function getAuctionDetails(address user) external view returns(uint256 remainingNFTs, uint256 expires, uint256 currentPrice, uint256 userBids) {
    remainingNFTs =  totalForAuction - totalBids;
    expires = expiresAt;
    currentPrice = getPrice();
    if(user != address(0))
        userBids = allBids[personalBids[user]].bidsPlaced;
}
}
```






防护措施
1.使用tx.origin 防止本合约调用外部合约   https://blog.csdn.net/sooxin/article/details/124372249
2.
3.安全开发指南 https://github.com/ConsenSys/smart-contract-best-practices/blob/master/README-zh.md
4.
5.

















































































