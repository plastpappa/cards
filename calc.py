import functools
from functools import reduce
import itertools
import operator
from math import floor, ceil
from scipy.special import binom
import timeit
from random import randint
import matplotlib.pyplot as plt
import numpy as np


def weakcomps(n, k):
    if k == 0:
        return [n*[0]]
    if n == 0:
        return []
    xs = []
    for i in range(k+1):
        for ys in weakcomps(n-1, k-i):
            xs.append([i] + ys)
    return xs

def partitions(k, n):
    if n == 0:
        return [[]]
    if k == 0:
        return []
    xs = []
    for i in range(n):
        for ys in partitions(k-1, i):
            xs.append([n-i] + ys)
    return xs

def split_partition(xs, k):
    if k == 0:
        return [len(xs)*(0,)]
    if len(xs) == 0:
        return []
    x = xs[0]
    rs = []
    for y in range(x+1):
        for ys in split_partition(xs[1:], k-y):
                rs.append((y,) + ys)
    return sorted(rs, reverse = True)

def split_partition2(alpha, k):
    if k == 0:
        return [ (1, (), tuple(alpha)) ]
    if len(alpha) == 0:
        return []
    a  = alpha[0]
    rs = []
    for b in range(a+1):
        c = a - b
        for (m, beta_, gamma_) in split_partition2(alpha[1:], k - b):
            beta   =  beta_  if b == 0 else tuple(sorted((b,) + beta_,  reverse = True))
            gamma  =  gamma_ if c == 0 else tuple(sorted((c,) + gamma_, reverse = True))
            try:
                n, i = next((n, i) for i, (n, bETA, gAMMA) in enumerate(rs) if beta == bETA and gamma == gAMMA)
                rs[i] = (n + m, beta, gamma)
            except StopIteration:
                rs.append((m, beta, gamma))
    return sorted(rs, reverse = True)

def divisions(w,h,f=None):
    if f is None:
        f = floor(w*h)/2
    return [ y for y in weakcomps(h+1, w) if sum([ i*x for i, x in enumerate(y) ]) == f ]


def qmult(xs, ys):
    rs = []
    for x in xs:
        for y in ys:
            rs = qadd1(rs, (x[0]*y[0], sorted(x[1] + y[1], reverse = True)))
    return rs

def qadd(xs, ys):
    return reduce(qadd1, xs, ys)

def qadd1(xs, x):
    try:
        i, y = next((i, y) for i, y in enumerate(xs) if y[1:] == x[1:])
        xs[i] = (x[0] + y[0],) + x[1:]
    except StopIteration:
        xs.append(x)
    return xs


def f(w,h,q=None):
    xs = divisions(w,h,q)
    def f(i,Ni):
        n  = floor(binom(h, i))
        ps = partitions(n, Ni)
        return [ (binom(n, len(p)), p) for p in ps ]
    ys = [ [ f(i,Ni) for i, Ni in enumerate(Ns) ] for Ns in xs ]
    zs = [ reduce(qmult, Ns, [(1,[])]) for Ns in ys ]
    ns = reduce(qadd, zs, [])
    ns.sort(key = lambda x: tuple(x[1]), reverse = True)
    return ns


def possible_pairings(xs):
    rs = set()
    fst = None
    i = 0
    while i < len(xs):
        x = xs[i]
        if x > 0:
            if fst is None:
                fst = i
                xs[i] -= 1
                continue
            else:
                ys = xs[:]
                ys[i] -= 1
                pair = (fst, i)
                for r in possible_pairings(ys):
                    q = tuple(sorted((pair,) + r))
                    rs.add(q)
        i += 1
    if len(rs) == 0:
        return set([ () ])
    return sorted(rs)

def possible_pairings2(xs):
    rs = set()
    fst = None
    snd = None
    i = 0
    while i < len(xs) and fst == None:
        x = xs[i]
        if x > 0:
            fst = i
            xs[i] -= 1
        i += 1
    while i < len(xs) and snd == None:
        x = xs[i]
        if x > 0:
            snd = x
            
            ys = xs[:]
            ys[i] -= 1
            pair = (fst, i)
            for r in possible_pairings(ys):
                q = tuple(sorted((pair,) + r))
                rs.add(q)
        i += 1
    if len(rs) == 0:
        return set([ () ])
    return sorted(rs)
        

def map2(f, xs, ys):
    return [ f(x,y) for (x,y) in zip(xs, ys) ]

"""def split(ns, m):
    def cleanup(ps):
        return sorted([ p for p in ps if p != 0 ], reverse = True)
    return qadd([
        (n, cleanup(ps1), cleanup(map2(operator.sub, ps, ps1))) 
            for (n, ps) in ns
            for ps1 in split_partition(ps, m)
    ], [])"""

def cleanup(ps):
    return sorted([ p for p in ps if p != 0 ], reverse = True)



def F(w, h, q, p):
    ns = f(w, h, q)
    # print(ns)
    ms = qadd([
        (n, ps1, ps2)
        for (n, ps) in ns
        for (ps1, ps2) in [
            (tuple(cleanup(ps1)), tuple(cleanup(map2(operator.sub, ps, ps1))))
            for ps1 in split_partition(ps, 2*p)
        ]
    ], [])
    ks = [ (n, len(possible_pairings(list(ps1))), len(possible_pairings(list(ps2)))) for (n, ps1, ps2) in ms ]
    return sum(reduce(operator.mul, x, 1) for x in ks)


def G(p, h, f):
    return sum([ F(2*p, h, f - q, q) for q in range(p+1) if f >= q ])
    
def Gsum(p, h):
    rs = [
        G(p, h, x) for x in range(2*p*h + p + 1)
    ]
    return (rs, sum(rs))
        

def x(h, w):
    if w == 0:
        return set([ () ])
    games = set()
    for i in range(2**h):
        for j in range(2**h):
            for k in range(2):
                pair = (k, tuple(sorted([i, j])))
                for xs in x(h, w - 1):
                    games.add(tuple(sorted((pair,) + xs)))
    return sorted(games)
    
def X(t):
    return sum([ n + sum(ns) for (n, ns) in t ])

    """games = set()
    for x in range(w):
        pairs = []
        for i in range(2**h):
            for j in range(2**h):
                pair = tuple(sorted([i, j]))
                pairs.append(pair)
        pairs.sort()
        games.add(tuple(pairs))
    return games"""
    
    """pair = set()
    for _ in range(2):
            pair.add(i)"""



def kmap(f, xs):
    return [ (f(n), ps) for (n, ps) in xs ]

def table(rs):
    rs = sorted(rs, key = lambda r: r[0])
    ns = [ n for (n, _) in rs ]
    N  = sum(ns)
    qs = kmap(lambda n: (n, round(100*n/N, 5)), rs) 
    res = ""
    for ((n, r), ps) in qs:
        res += "$" + ", ".join([ str(p) for p in ps ]) + "$"
        res += " & "
        res += f"\\numprint{{{str(floor(n))}}}"
        res += " & "
        res += f"\\numprint{{{r:.5f}}}"
        res += "\\\\ \\hline \n"
    res += f"\\textbf{{Summa}} & \\textbf{{ \\numprint{{{floor(N)}}}}} & \\textbf{{ \\numprint{{{100.00000}}}}} \\\\ \\hline"
    return res


def plot(ax, p, h):
    plt.ion()
    rs = Gsum(p, h)
    N = p*(2*h + 1)
    x = np.linspace(-0.5, 0.5, N + 1)
    ys = rs[0]
    max_y = max(ys)
    y = [ t / max_y for t in ys ]
    ax.plot(x, y, marker='o')

fig, ax = plt.subplots()
plot(ax, 1, 5)
plot(ax, 2, 5)
plot(ax, 3, 5)
plot(ax, 4, 5)
plot(ax, 5, 5)