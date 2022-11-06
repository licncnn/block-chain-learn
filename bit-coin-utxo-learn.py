
##################################################
# 以下是 区块链实现

class Pointer(tuple):  # 指向输出单元在区块链中的位置的    交易编号      sequence
    def __new__(cls, tx_id, n):
        return tuple.__new__(cls, (tx_id, n))

    @property
    def tx_id(self):  # 交易的哈希id
        return self[0]

    @property
    def n(self):  # 第x条输出单元
        return self[1]


class Vin(tuple):  # 输入单元      上一个交易的输出    张三的签名  代表却是是我想转账给你    当前发送公钥用于验证  sequence呢？utxo 中的Pointer，也就是to_spend参数中含有此序号
    def __new__(cls, to_spend, sig, pk):
        return tuple.__new__(cls, (to_spend, sig, pk))

    @property
    def to_spend(self):  # 指向输出单元
        return self[0]

    @property
    def sig(self):  # 签名
        return self[1]

    @property
    def pk(self):  # 公钥  是谁的公钥？
        return self[2]


class Vout(tuple):  # 输出单元     包括地址   金额
    def __new__(cls, to_addr, value):
        return tuple.__new__(cls, (to_addr, value))

    @property
    def to_addr(self):  # 地址
        return self[0]

    @property
    def value(self):  # 金额
        return self[1]


class Tx(tuple):  # 交易
    def __new__(cls, tx_in, tx_out, fee):
        return tuple.__new__(cls, (tx_in, tx_out, fee))

    @property
    def tx_in(self):  # 输入，输入单元Vin的集合
        return self[0]

    @property
    def tx_out(self):  # 输出，输出单元Vout的集合
        return self[1]

    @property
    def fee(self):  # 交易费
        return self[2]

    @property
    def tid(self):  # 交易的编号 是当前交易的哈希值
        s = self.to_string()
        return sha256(s.encode()).hexdigest()

    def to_string(self):
        return str(self)

    def is_coinbase(self):  # 标记是否为铸币交易
        return _is_coinbase(self)


class UTXO(tuple):  # 是对输出单元的重新封装
    def __new__(cls, pointer, vout, is_coinbase, unspent, confirmed):
        return tuple.__new__(cls, (pointer, vout, is_coinbase, unspent, confirmed))

    @property
    def pointer(self):  # 输出单元的位置
        return self[0]

    @property
    def vout(self):  # 输出单元
        return self[1]

    @property
    def is_coinbase(self):
        return self[2]

    @property
    def unspent(self):  # 是否被消费
        return self[3]

    @property
    def confirmed(self):  # 是否被确认
        return self[4]


utxo_set = {}  # utxo集合


def add_utxo_to_set(tx):  # 将交易中的输出单元封装成UTXO加入到UTXO_SET集合，一般是接受到的交易
    for i, vout in enumerate(tx.tx_out):
        # 对于铸币交易  交易哈希值  交易编号 0，为什么带上交易编号？ 因为一个交易中带多个输出 用数组保存
        pointer = Pointer(tx.tid, i)
        is_coinbase = tx.is_coinbase() # 是否为铸币交易
        utxo = UTXO(pointer, vout, is_coinbase, True, False) # unspent   unconfirmed
        utxo_set[pointer] = utxo  # 存入集合 key为 交易hash


def delele_utxo_from_set(tx):  # 将使用过的UTXO从UTXO_SET中移除
    for vin in tx.tx_in:
        pointer = vin.to_spend  # to_spend 指向上一个输出单元   使用完了可以删除
        del utxo_set[pointer]


def _is_coinbase(tx): # 铸币交易  没有输入  一条输出 即为转给当前挖到矿的账户
    return len(tx[0]) == 0 and len(tx[1]) == 1


def create_coinbase(to_addr, value):
    tx_in = []
    tx_out = [Vout(to_addr, value)] # 封装一条输出，写上地址和金额    这笔转账发给谁  多少钱
    fee = 0 # 无需手续费
    return Tx(tx_in, tx_out, fee)


def pubkey_to_addr(p_str):  # 公钥哈希转地址
    sha = sha256(p_str).digest()
    ripe = new('ripemd160', sha).digest()
    return b58encode_check(b'\x00' + ripe).decode()


def sk_to_bytes(number):  # 私钥编码函数
    return number_to_bytes(number, 32)


def pk_to_bytes(points):  # 公钥编码函数
    return number_to_bytes(points[0], 32) + number_to_bytes(points[1], 32)


def bytes_to_sk(sk_str):  # 私钥解码函数
    return bytes_to_number(sk_str)


def bytes_to_pk(pk_str):  # 公钥解码函数
    return bytes_to_number(pk_str[:32]), bytes_to_number(pk_str[32:])


##张三给李四转账100分
sk = 23023230202030230232454
pk = mult(G, sk, p, a, b)
sk_str = sk_to_bytes(sk)
pk_str = pk_to_bytes(pk)
addr = pubkey_to_addr(pk_str)  # 从公钥中生成地址

##李四也会有些个人信息
sk1 = 230232302020302302328238829382
pk1 = mult(G, sk1, p, a, b)
sk_str1 = sk_to_bytes(sk1)
pk_str1 = pk_to_bytes(pk1)
addr1 = pubkey_to_addr(pk_str1)

##创世区块中的创币交易
tx = create_coinbase(addr, 1000) #铸币交易  奖励挖到矿的节点 给1000个bitcoin
add_utxo_to_set(tx)

##张三查找自己的utxos
# 也就是转账给张三的钱   就是张三账户的余额
utxos = [utxo for utxo in utxo_set.values() if utxo.vout.to_addr == addr]  # 张三的UTXO集合

value = 100 # 转账金额
fee = 10 # 交易费
_value = value + fee
i, s = 0, 0
for utxo in utxos:
    s += utxo.vout.value # 当前的余额
    i += 1
    if s >= _value:  # 当前的余额 > 转账需要支付的费用
        break
spend = utxos[:i] # 获取前面几条输出    也就是取出一部分钱用于转账

##创建交易
tx_in = []
tx_out = []

##如果支付金额与需要消费的UTXO金额相等，则只有一个输出单元
if s == _value:
    vout = Vout(addr1, value)
    tx_out = [vout]

##否则应该有两个输出单元
vout1 = Vout(addr1, value)  # 李四的地址
vout2 = Vout(addr, s - _value)  # 张三的地址
tx_out = [vout1, vout2]  # 给李四转帐一部分  剩下的转给自己   或者是其他地址

for utxo in spend:# 需要添加
    ##要使用的utxo的指针
    pointer = utxo.pointer  # utxo引用
    message1 = (str(pointer)).encode()  # 签名明文
    sig = sign(message1, sk)  # 用私钥签名
    sig_str = pk_to_bytes(sig)  # 签名编码
    # 三个参数 1.上一个输出单元的位置，用自己的私钥对上一个输出单元做签名，提供自己的公钥以供验证
    vin = Vin(pointer, sig_str, pk_str)  # 输入单元
    tx_in.append(vin)  # 输入    ==需要修改  , 因为张三的交易为铸币交易 因此一个也够用了

# 封装为交易 tx_in 为本次交易需要花掉的utxo，tx_out为本次交易会产生的输出
tx1 = Tx(tx_in, tx_out, fee)  # 张三支付给李四的交易


flag1=False
flag2=False
# 转给李四的交易 还需要判断是否合法
for vin in tx1.tx_in:
    pointer = vin.to_spend  # 获取输入单元的指针，也就是要花费的utxo
    utxo = utxo_set[pointer]  # 通过指针在utxo_set集合中找到该utxo

    # 验证用户是否有资格来花费这个UTXO
    ppk_str = vin.pk  # 获取vin的公钥，编号后的
    addr2 = pubkey_to_addr(ppk_str)  # 将公钥转换为地址

    # 验证公钥和地址匹配
    flag1 = addr2 == utxo.vout.to_addr

    # 验证签名，验证地址和私钥匹配
    ssig_str = vin.sig  # 编码后的
    ssig = bytes_to_pk(ssig_str)  # 解码签名
    ppk = bytes_to_pk(ppk_str)  # 解码公钥
    message = (str(pointer)).encode()  # 规则

    # 验证公钥和签名是匹配的
    flag2 = verify(message, ppk, ssig)


if(flag1==True and flag2==True):
    print("张三->李四 交易验证合法")


    print("从utxo集合中删除已经使用掉的utxo")
    #..
    for vin in tx1.tx_in:
        pointer = vin.to_spend  # 获取输入单元的指针，也就是要花费的utxo
        del utxo_set[pointer]  # 删除已经用掉的utxo

    print("将 tx_out 中的输出封装为utxo 加入到utxo集合中")
    #..

    print("将输出 unspent标记位 False")
    #..

    print("发布到交易池，等到挖矿节点打包...")


else:
    print("交易不合法")



flag1=False
flag2=False

# 王五修改交易
addr2 = "1121212"
vout3 = Vout(addr2, value)  # 王五的地址
tx_out1 = [vout3, vout2]
# 同一比输入 想double spend ，
tx2 = Tx(tx1.tx_in, tx_out1, fee)  # 与tx1相比，仅仅是addr1改成了addr2

try:
    # 传播到了王五
    for vin in tx2.tx_in:
        pointer = vin.to_spend  # 获取输入单元的指针，也就是要花费的utxo
         # !!!! 此处会出错   因为utxo已经使用掉  可以防止double spend
        utxo = utxo_set[pointer]  # 通过指针在utxo_set集合中找到该utxo

        # 验证用户是否有资格来花费这个UTXO
        ppk_str1 = vin.pk  # 获取vin的公钥，编号后的
        addr3 = pubkey_to_addr(ppk_str1)  # 将公钥转换为地址

        # 验证公钥和地址匹配
        flag1 = addr3 == utxo.vout.to_addr

        # 验证签名，验证地址和私钥匹配
        ssig_str1 = vin.sig  # 编码后的
        ssig1 = bytes_to_pk(ssig_str1)  # 解码签名
        ppk1 = bytes_to_pk(ppk_str1)  # 解码公钥
        message2 = (str(pointer)).encode()  # 规则

        # 验证公钥和私钥是匹配的
        flag2 = verify(message2, ppk1, ssig1)
except:
    print("张三->王五 交易失败  不合法!!!")

if (flag1 == True and flag2 == True):
    print("张三->王五 交易验证合法")

    print("从utxo集合中删除已经使用掉的utxo")
    # ..

    print("将 tx_out 中的输出封装为utxo 加入到utxo集合中")
    # ..

    print("将输出 unspent标记位 False")
    # ..

    print("发布到交易池，等到挖矿节点打包...")


else:
    print("交易不合法")



#===========================================================
# 以下为其他内容 等待补充
# 明文攻击，就是签名函数中需要用到明文，如果明文的选择和交易的输出无关
# 当你的交易发送到网络中，其他人都可以随意的修改交易的输出中的地址，意味着能盗用你的UTXO

class Block(tuple):  # 区块类型

    def __new__(cls,
                version,
                prev_block_hash,
                timestamp,
                bits,
                nonce,
                txs):
        return tuple.__new__(cls, (version,
                                   prev_block_hash,
                                   timestamp,
                                   bits,
                                   nonce,
                                   txs))

    @property
    def version(self):
        return self[0]

    @property
    def prev_block_hash(self):
        return self[1]

    @property
    def timestamp(self):
        return self[2]

    @property
    def bits(self):
        return self[3]

    @property
    def nonce(self):
        return self[4]

    @property
    def txs(self):
        return self[5]

    @property
    def merkle_root_hash(self):
        level = [tx.tid for tx in self[5]]
        return get_root_hash(level)

    def header(self, nonce=None, merkle_root_hash=None):
        if merkle_root_hash is None:
            merkle_root_hash = self.merkle_root_hash

        return "{0}{1}{2}{3}{4}{5}".format(self[0],
                                           self[1],
                                           self[2],
                                           self[3],
                                           merkle_root_hash,
                                           nonce or self[4],
                                           )

    def hash(self):
        return sha256d(self.header())


def sha256d(string):
    if not isinstance(string, bytes):
        string = string.encode()

    return sha256(sha256(string).digest()).hexdigest()


version = "1.0"
pre_block_hash = None
timestamp = 20191001
bits = 8
nonce = 0
txs = [tx, tx1]

b0 = Block(version,
           pre_block_hash,
           timestamp,
           bits,
           nonce,
           txs)


# 挖矿函数
def mine(block):
    y = 1 << (256 - block.bits)
    nonce = 0
    while int(sha256d(block.header(nonce)), 16) >= y:
        print(block.header(nonce))
        nonce += 1
    return nonce


# 根据交易编号列表 计算交易的梅克尔树根哈希函数
def get_root_hash(level):
    while len(level) != 1:
        odd = None
        if len(level) % 2 == 1:
            odd = level.pop()
        level = [sha256d(i1 + i2) for i1, i2 in pair_node(level)]

        if odd is not None:
            level.append(odd)

    return level[0]


def pair_node(l):
    return [l[i:i + 2] for i in range(0, len(l), 2)]


# 梅克尔树节点对象
class Node:

    def __init__(self, data, flag=False):
        if flag:
            self.val = data
        else:
            self.val = sha256d(data)

        self.parent = None
        self.bro = None
        self.side = None
        self.left_child = None
        self.right_child = None

    def __repr__(self):
        return "Node(%r)" % self.val


# 梅克尔树对象
class MerkleTree:
    def __init__(self, leaves=[]):
        self.leaves = [Node(leaf, True) for leaf in leaves]
        self.root = None

    # 计算根哈希
    def get_root(self):
        level = self.leaves[::]
        while len(level) != 1:
            level = self.build_new_level(level)
        self.root = level[0]
        return self.root.val

    # 通过下层更新上层
    def build_new_level(self, level):
        new = []
        odd = None
        if len(level) % 2 == 1:
            odd = level.pop()

        for i in range(0, len(level), 2):
            newnode = Node(level[i].val + level[i + 1].val)
            newnode.left_child, newnode.right_child = level[i], level[i + 1]
            level[i].parent, level[i + 1].parent = newnode, newnode
            level[i].bro, level[i + 1].bro = level[i + 1], level[i]
            level[i].side, level[i + 1].side = "LEFT", "RIGHT"
            new.append(newnode)
        if odd:
            new.append(odd)
        return new

    # 获取交易的梅克尔树路径
    def get_path(self, index):
        path = []
        this = self.leaves[index]
        path.append((this.val, "SELF"))
        while this.parent:
            path.append((this.bro.val, this.bro.side))
            this = this.parent

        path.append((this.val, "ROOT"))
        return path




def inv_mod(p, b):  # 求逆元函数,p模数,b是要求逆元的数
    if b < 0 or p <= b:
        b = b % p
    c, d = b, p
    uc, vc, ud, vd, temp = 1, 0, 0, 1, 0
    while c != 0:
        temp = c
        q = d // c
        c = d % c
        d = temp
        uc, vc, ud, vd = ud - q * uc, vd - q * vc, uc, vc

    assert d == 1
    if ud > 0:
        return ud
    return ud + p


def show_points(p, a, b):
    return [(x, y) for x in range(p) for y in range(p)
            if (y * y - (x * x * x + a * x + b)) % p == 0]


def double(P, p, a, b):  # 椭圆曲线上点的双倍,P是椭圆曲线是上的点
    # p是模数,a,b是椭圆曲线的参数
    x, y = P
    l = ((3 * x * x + a) * inv_mod(p, 2 * y)) % p
    x3 = (l * l - 2 * x) % p
    y3 = (l * (x - x3) - y) % p
    return x3, y3


def add(P, Q, p, a, b):  # 椭圆曲线上点P和Q之和
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and y1 == y2:
        return double(P, p, a, b)
    l = ((y2 - y1) * inv_mod(p, x2 - x1)) % p
    x3 = (l * l - x1 - x2) % p
    y3 = (l * (x1 - x3) - y1) % p
    return x3, y3


def mult(P, n, p, a, b):  # 椭圆曲线上n倍的点P
    s = bin(n)
    s = s.replace("0b", "")
    acc_p = P
    product = 0
    for char in s[::-1]:
        if char == "1":
            if product == 0:
                product = acc_p
            else:
                product = add(product, acc_p, p, a, b)
        acc_p = double(acc_p, p, a, b)

    return product


# secp256k1 椭圆曲线的参数
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
a, b = 0, 7

# secp256k1椭圆曲线的基点
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)

# secp256k1椭圆曲线的基点的阶
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

from simchain.ecc import number_to_bytes, bytes_to_number
from hashlib import new, sha256
from base58 import b58encode_check


# 创建明文的函数
def build_message(string):
    return sha256(string).digest()


import random

# 用私钥签名的函数
def sign(message, k):
    message = build_message(message)
    h = bytes_to_number(message)
    r, s = 0, 0
    while r == 0 or s == 0:
        rk = random.randint(1, n)
        rG = mult(G, rk, p, a, b)
        r = rG[0]
        s = (((h + k * r) % n) * inv_mod(n, rk)) % n
    return r, s


# def sign1(message, k):
#     message = build_message(message)
#     h = bytes_to_number(message)
#     rk = fix(number)
#     rG = mult(G, rk, p, a, b)
#     r = rG[0]
#     s = (((h + k * r) % n) * inv_mod(n, rk)) % n
#     return r, s


# 用公钥验证签名的函数
def verify(message, K, sig):
    r, s = sig
    message = build_message(message)
    h = bytes_to_number(message)
    u = (h * inv_mod(n, s)) % n  # h/s
    v = (r * inv_mod(n, s)) % n  # r/s
    Q = mult(G, u, p, a, b)  # h/s*G
    R = mult(K, v, p, a, b)  # r/s*K
    P = add(Q, R, p, a, b)  # h/s*G + r/s*K
    return r == P[0] % n


k1 = 323232
message = b'aeaeae'
message2 = b'1121212'
K = mult(G,k1,p,a,b)
K1 = mult(G,k1,p,a,b)
sig = sign(message,k1)
flag = verify(message,K,sig)


import random
def generate_random_keys(m):
   for _ in range(m):
       k = random.randint(1,n)
       K = mult(G,k,p,a,b)
       print(k,K)


import hmac
from hashlib import sha512,sha256

import os
seed = os.urandom(32)

d = hmac.new(key = b'blockchain',msg = seed,digestmod = sha512).digest()
master_k_bytes = d[:32]
master_k = bytes_to_number(master_k_bytes)
master_K = mult(G,master_k,p,a,b)
master_K_bytes = number_to_bytes(master_K[0],32) + number_to_bytes(master_K[1],32)

master_code = d[32:]
idx = 32
idx = number_to_bytes(idx,32)
key = master_k_bytes + idx
msg = master_code
child32 = hmac.new(key = key,msg = msg,digestmod = sha512).digest()

child32_k_bytes = child32[:32]
child32_code = child32[:32]
child32_idx = 23
child32_idx = number_to_bytes(child32_idx,32)

key = child32_k_bytes + child32_idx
msg = child32_code
grandson23 = hmac.new(key = key,msg = msg,digestmod = sha512).digest()


# 是随机数攻击函数
def crack_by_same_rk(sig1, sig2, m1, m2, K):
    m1 = build_message(m1)
    h1 = bytes_to_number(m1)
    m2 = build_message(m2)
    h2 = bytes_to_number(m2)
    r1, s1 = sig1
    r2, s2 = sig2
    assert r1 == r2

    rk1 = ((h1 - h2) % n * inv_mod(n, s1 - s2)) % n
    rk2 = ((h1 - h2) % n * inv_mod(n, s1 + s2)) % n
    rk3 = ((h1 - h2) % n * inv_mod(n, -s1 - s2)) % n
    rk4 = ((h1 - h2) % n * inv_mod(n, -s1 + s2)) % n

    for rk in (rk1, rk2, rk3, rk4):
        k = (((s1 * rk) % n - h1) % n * inv_mod(n, r1)) % n
        if mult(G, k, p, a, b) == K:
            print(k)
        print('not found')

