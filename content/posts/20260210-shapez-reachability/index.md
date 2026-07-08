+++
author = "Shaojia"
title = "Which Shapes Are Reachable in Shapez?"
date = "2026-02-10T17:22:38+08:00"
tags = []
cover = ""
description = "After going through a series of random attempts, I put this project on hold for over a year. Now, it's time to finish what we started but left unfinished before."
showFullContent = false
hideComments = false
Toc = true
+++

# Intro

<!-- 
<div style="float: right; margin: 0 0 10px 15px;">
<iframe width="250" height="100" scrolling="no" frameborder="no" allow="autoplay" src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/soundcloud%253Atracks%253A891432268&color=%23e8c45c&auto_play=false&hide_related=true&show_comments=false&show_user=false&show_reposts=false&show_teaser=false"></iframe>
</div>
-->

Ever since Christmas 2024, when I was still preparing for the <abbr title="National Olympiad in Informatics ">NOI</abbr> Provincial Team Selection Competition (which I would later fail), I had already completed the game Shapez<cite>[^1]</cite> and built a working Everything Machine. Well, accurately speaking, not *every* shape can be made from it. It’s designed for random 4-layer full shapes, the kind you get in freeplay<cite>[^2]</cite> (so e.g., [rocket shape](https://shapezio.fandom.com/wiki/Level_26) is excluded). Since then, I've been fixated on creating a genuine Everything Machine that supports any layer count and handles all configurations with internal voids. So the first thing I needed to do was figure out which shapes could actually be built using stackers, rotators, and cutters. I even had a dream back then: if I could fully solve the reachability problem (preferably with an efficient algorithm), I could turn it into an OI problem.

[^1]: Shapez Demo <https://shapez.io/> <br/> Steam Webpage <https://store.steampowered.com/app/1318690/Shapez/>

[^2]: Freeplay refers to levels 27 and above. All levels before this have a specific shape requirement. From level 27 onward the shape requirements are randomly generated shapes starting with 2 layers and going up to 4 layers at the most.

After going through a series of random attempts, I put this project on hold for over a year. Now, it's time to finish what we started but left unfinished before.

> If you are looking for test data, pieces of code, or my trail of tortuous exploration, please visit [the repo](https://github.com/zhangshaojia07/shapez-reachability).

# Abstraction

Firstly, the shape and colour of each piece in every shape don't matter with the reachability. So every slot has the information of a Boolean variable, representing whether there is a piece. Thus, a shape is a Boolean 2D-array of shape (4,n), where n is the height of the shape.

# Decomposition

Speaking of methodology, I made a list of methods to implement after random scribbling:

1. Write some code: data generator, reference implementation, comparator, and code under test. Keep amending the attempt code from simple rules to niche cases.
2. Find large-amount, obviously reachable cases. Prove the others by reduction or induction.
3. Straight-forward. Categorize without omission or duplication.
4. Find partial relations among shapes to solve a finite number of sub-problems.
5. Make use of symmetry.
6. Ask AI.
7. Find pre-written heuristic searching libraries.

Here are corresponding drawbacks:

1. Too intuitive. Risk of overfitting. Hard to produce a mathematical proof.
2. Some cases are tricky.
3. Deal with a huge amount of branches.
4. Hard to prove a shape is losing.
5. Very few symmetry properties aside from rotation and mirror.
6. The AI has got no idea.
7. Didn't find anything fit.

Then, what method did I choose? Hybrid.

Below, we only consider shapes whose bottom layer consists of one or more pieces. In other words, we exclude the empty shape and let shapes fall until they touch the ground prior to reachability checking.

We identify several direct reachability conditions (DRCs). If any DRC-i holds for a shape S, then S is reachable.

**DRC-1:**
There are two adjacent columns that are both empty.

> **Proof.**
> You can place any filler pieces within the two empty columns. Every piece required can be stacked in place using a 1-layer semi-circle. Finally, cut off the two empty columns.

DRC-1 is truly fundamental. For any shape that doesn't satisfy DRC-1, the final step in its construction cannot be a "cut" operation. Thus, we can eliminate the "cut" operation entirely and construct all shapes starting from those that satisfy DRC-1.

Now, excluding "rotate", we are left with only one type of operation: "stack". This simplification always gives me the strong impression that we are just one step away from success. However "stack" operation is not associative! A typical example is shown<cite>[^3]</cite> below:
```text
A   B C D    E
100 1 1 1011 1101
001 0 1 0011 0011
000 0 0 0000 0000
000 0 0 0000 0000

(C  stack  B) stack  A  = D
 C  stack (B  stack  A) = E
```

[^3]: How to interpret the example: 0 represents void and 1 represents an occupied cell (piece); the four lines correspond to the four columns, with the left side indicating the bottom and the right side indicating the top of the shape.

Notice that "stack" as a binary operator always means "stacks on".

This property foreshadowed the utilization of **binary component tree**.

Let's explore the DRCs in more depth.

**DRC-2:**
Bottom layer consists two or more pieces.

> **Proof.**
> There's always a way to cut the shape into two semi-cylinders that DRC-1 holds for both parts.

**Definition-1:**
A '=' is a pair of adjacent pieces in the same column. Its row index is that of the **upper** piece.

To make the explanations easier, we define a operation called **"mirror"**. It swaps 1st and 3rd columns of a shape (columns are always **0-indexed**). It's obvious that the reachability isn't changed by this operation.

We are going to use "xxxx" (where x is 0/1) to indicate a shape that is empty in the 0-columns and non-empty in the 1-columns.

**DRC-3:**
Two adjacent columns both contain '='.

> **Proof.**
> Assume that DRC-2 failed. We rotate the shape so that there's a piece at [0,0]<cite>[^4]</cite>.
> 
> * If the columns are 0th and 1st, then do: ("0110" and "1001") stack "1100". The case of 0th and 3rd is similar. 
> * If the columns are 1th and 2nd, then do: "0011" stack "0110" stack "1100". The case of 2nd and 3rd is similar. 

[^4]: Using `numpy` subscript format.

Don't panic. There won't be DRC-4. However, a transitional reachability condition (TRC) needs to appear here.

**TRC-1:**
Shape Y is one piece more than shape X. If the extra piece is not the bottom piece in its column in shape Y, the reachability of shape X implies that of shape Y. 

> **Proof.**
> Denote the extra piece p and the next piece below q. Retrace the piece q in the binary component tree. Whether q is included in the "upper" or "lower" shape in a stack operation, p can stick with q. Eventually, we construct p above q before the cut operation in the very beginning.

Now, let's set some narrowing-down rules to make caseworking possible. These rules should be proven not to make any reachable shapes irreachable. Every Rule-i is based on each Rule-j, where j < i .

**Rule-1:**
Shape X stacks on shape Y. The index set of non-empty columns in X is \(X\) and Y is \(Y\). Then \(|X\cap Y|\le 1\). 

> **Proof.**
> Assume \(i,j\in |X\cap Y|\) are different column indices, that X and Y "touch" each other in column j.
>
> If there's no '=' in column i in X, re-allocating the whole column i to Y is also validable and obeys Rule-1. The "lower" is due to TRC-1, and the column i in "upper" was not load-bearing.
>
> Otherwise, find an arbitrary '=' in column i in X, say at row r. Re-allocate [i,:r] to Y. The "lower" is guaranteed by TRC-1. The "upper" is separated into two semi-cylinders with one touch to "lower" each. The construction is similar to that of proof of DRC-2.
>
> Because the adjustment can only make shape Y bigger, so it must have an end obeying Rule-1.

**Rule-2:**
Shape X stacks on shape Y. There must be two or more non-empty columns in X.

> **Proof.**
> If the occupied columns don't intersect, it must hold DRC-2. Otherwise, it is directly from TRC-1.

Due to Rule-1 and Rule-2, we naturally rank the shapes by the number of non-empty columns. If a shape of rank \(x_1\) doesn't meet DRC-1 nor DRC-2, it must be constructed directly from: a shape of rank \(x_2\) stacks on a shape of rank \(x_3\), where \(x_2+x_3=x_1,x_2\in[2,x_1],x_3\in[1,x_1-1]\). From now on, we use abbreviations like "2-on-1", "2-on-3", and "4-on-1", showing the ranks of the stacking shapes.

# Casework

We categorize all shapes by their "xxxx" form, with equivalence of rotation.

## 1000 & 1100

DRC-2 holds for both cases.

## 1010

**Definition-2:**
A segment bottom (seg_bot) is a piece that either is the bottom piece in its column, or forms a '=' with a lower piece.

### By DRC-2

Condition: if each of the columns has the piece in the bottom layer.

### By 2-on-1

At least one of them holds:
1. The "2" in "2-on-1" is DRC-2-holding.
2. The "2" in "2-on-1" is in "2-on-1" form (which makes a recursion)
3. The stack result is DRC-2-holding.

Nevertheless, the exit of the recursion can only be DRC-2. So,

Condition: if the two columns have a seg_bot at the same height.

### Summary

You may have noticed that the "DRC-2" case is completely included in "2-on-1", as the base case of the recursion.

So, the shape is reachable iff **the two columns have a seg_bot at the same height**.

In the following cases, every "DRC-2" is merged into the corresponding "k-on-1". 

## 1110

We index the three non-empty columns 0,1,2.

### By 0110 on 1100

Easy. Iff at least one '=' exists in the column 1.

### By 1010 on (1100 or 0110)

Iff column 0 and 2 have seg_bots at the same height, and not both of them are the bottom pieces in their columns.

**Definition-3:**
If the column is non-empty, the definition of high_eq is the row index of the highest '=' in the column. If the column doesn't contain any '=', then high_eq is the row index of its bottom piece.

### By 3-on-1

It must be a DRC-2-holding shape repetitively stacking on "1"s and touching them one-by-one (If not, it results in a new DRC-2-holding shape which we can start from).

For the starting DRC-2-holding shape, two columns have the bottom pieces and the other column has the bottom pieces not lower than them.

Hence, the condition is: a row is not higher than the minimum of high_eqs of the three columns, and at least two columns have seg_bots in the row.

### By (1100 or 0110) on 1010

This case is either included in "1010 on (1100 or 0110)" or DRC-2, which is included in "3-on-1".

### Summary

1. column 1 has '='.
2. column 0 and 2 have seg_bots at the same height, and not both of them are the bottom pieces in their columns.
3. a row is not higher than the minimum of high_eqs of the three columns, and at least two columns have seg_bots in the row.

## 1111

### By 4-on-1

Condition: a row is not higher than the minimum of high_eqs of the four columns, and at least two columns have seg_bots in the row.

### 

# Outro