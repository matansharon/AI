import os

with open('req.txt', 'r') as f:
    lines=f.readlines()
    for line in lines:
        l=line.strip().split(' ')
        r=[]
        for i in l:
            if i=='':
                continue
            else:
                r.append(i)
        t=''
        for i in r:
            t+=i[0]+'\n'
        with open('req1.txt', 'w') as f:
            f.write(t)