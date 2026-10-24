+++
author = "Shaojia"
title = "CUCaTS Code Golf 2026"
date = "2026-10-24T15:07:30+01:00"
tags = ["Code Golf", "Python", "Competitive Programming", "Cambridge"]
description = ""
cover = "solution-line.png"
showFullContent = false
hideComments = false
+++

Happy 1024 Festival, guys!

Yesterday afternoon I took part in [CUCaTS](https://cucats.org/)'s second code golf contest: two hours, six small Python problems, and a scoreboard where your score is the number of bytes in your source. I have done a fair amount of competitive programming, but almost all of it in C++. Code golf is a different sport, and I am not good at it. It was a genuinely new experience, and I learnt a lot.

The problems were friendly. None of them needs a clever algorithm; the difficulty lies in saying what you mean in as few symbols as possible. In a normal contest, an accepted solution is the end. Here, it is only the start, and I kept resubmitting, shaving off a byte or two each time. Sometimes dozens, though.

Along the way I found a side of Python I had never needed before: lambdas that call themselves, the walrus operator `:=`, a single comma to build a one-element tuple (`a+=x,` appends to a list), `__import__` to import inside an expression, booleans as integers, and bit tricks like `-~n` for `n+1` and `~-n` for `n-1`; those finally made sense after reading [this thread](https://codegolf.stackexchange.com/questions/54/tips-for-golfing-in-python).

{{< figure src="problem-d.png" alt="The Kangaroo problem next to an 81-byte solution" position="center" caption="Problem D, Kangaroo. My entire 81-byte solution is the single line in the editor at the bottom." captionPosition="center" >}}

My 81-byte Kangaroo solution is a single expression:

```python
f=lambda x:max(-1,(g:=lambda y=0:0 if y>=len(x)else(1+g(y+x[y])if x[y]else-9))())
```

`:=` names the inner helper `g`, which calls itself, and the default `y=0` seeds the recursion. I would never have written anything like this in ordinary code.

{{< figure src="code-golf-tricks.png" alt="Python golfing tips about bitwise operators" position="center" caption="The ~-n and -~n trick, from the Code Golf Stack Exchange thread on Python golfing." captionPosition="center" >}}

The gap between a working solution and a short one is huge, and reading shorter submissions taught me more than any tutorial. The scoreboard awards each problem's winner a Jack's Gelato token, but even those entries are far from the shortest possible, which Opus 5.5 generates in one shot. There is always another byte. That is the appeal.

Huge thanks to CUCaTS for organising it. I will be back for the next one with a shorter toolbox.
