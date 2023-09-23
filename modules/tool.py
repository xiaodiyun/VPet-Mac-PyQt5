import os
def LpsReader(path:str)->map:
    #读取原作自己创造的lps格式，转换成map。不了解详细规则，转个大概就行
    with open(path) as f:
        line=f.readline()
        ss=line.split(":|")
        key=ss[0]


