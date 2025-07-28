import math
from langchain_core.tools import tool

@tool
def power(base: float, exponent: float) -> float:
    """计算 base 的 exponent 次方"""
    return math.pow(base, exponent)

@tool
def sqrt(x: float) -> float:
    """计算平方根"""
    if x < 0:
        raise ValueError("负数不能开平方根")
    return math.sqrt(x)

@tool
def log(x: float, base: float = math.e) -> float:
    """计算对数，默认以 e 为底"""
    if x <= 0:
        raise ValueError("对数的真数必须大于 0")
    return math.log(x, base)

@tool
def mod(a: float, b: float) -> float:
    """计算 a 对 b 的模（余数）"""
    if b == 0:
        raise ValueError("不能对 0 取模")
    return a % b

@tool
def exp(x: float) -> float:
    """计算 e 的 x 次方"""
    return math.exp(x)


# 定义四则运算工具
@tool
def add(a: float, b: float) -> float:
    """加法：返回两个数的和"""
    return a + b

@tool
def subtract(a: float, b: float) -> float:
    """减法：返回第一个数减去第二个数的结果"""
    return a - b

@tool
def multiply(a: float, b: float) -> float:
    """乘法：返回两个数的积"""
    return a * b

@tool
def divide(a: float, b: float) -> float:
    """除法：返回第一个数除以第二个数的结果

    参数：
        a (float): 被除数
        b (float): 除数

    返回：
        float: 商

    抛出：
        ValueError: 如果除数为0
    """
    if b == 0:
        raise ValueError('不能除以0')
    return a / b



if __name__ == "__main__":
    print(add.name)
    