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

## Intro

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

## Abstraction

Firstly, the shape and colour of each piece in every shape don't matter with the reachability. So every slot has the information of a Boolean variable, representing whether there is a piece. Thus, a shape is a Boolean 2D-array of shape (4,n), where n is the height of the shape.

## Decomposition

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

DRC-1 is truely fundamental. For any shape that doesn't satisfy DRC-1, the final step in its construction cannot be a "cut" operation. Thus, we can eliminate the "cut" operation entirely and construct all shapes starting from those that satisfy DRC-1.

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
> There's always a way to cut the shape into two semi-cylinders. DRC-1 holds for both parts.

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

Don't panic. There won't be DRC-4. Now, let's set some narrowing-down rules to make caseworking possible. These rules should be proven not to make any reachable shapes irreachable. Every Rule-i is based on each Rule-j, where j < i .

**Rule-1:**
Shape X stacks on shape Y. The index set of non-empty columns in X is \(X\) and Y is \(Y\). Then \(|X\cap Y|\le 1\). 

> **Proof.**
> TBD

**Rule-2:**
Shape X stacks on shape Y. There must be two or more non-empty columns in X.

> **Proof.**
> TBD

Due to Rule-1 and Rule-2, we naturally rank the shapes by the number of non-empty columns. If a shape of rank \(x_1\) doesn't meet DRC-1 nor DRC-2, it must be constructed directly from: a shape of rank \(x_2\) stacks on a shape of rank \(x_3\), where \(x_2+x_3=x_1,x_2\in[2,x_1],x_3\in[1,x_1-1]\). From now on, we use abbreviations like "2on1", "2on3", and "4on1", showing the ranks of the stacking shapes.

## Casework

We categorize all shapes by their "xxxx" form, with equivalence of rotation.

### 1000 & 1100

DRC-2 holds for both cases.

### 1010

**Definition-2:**
A segment bottom (seg_bot) is a piece that either is the bottom piece in its column, or forms a '=' with a lower piece.

#### DRC-2

Condition: if both of the columns have a piece in the bottom layer.

#### 2on1

The "2" in "2on1" is either DRC-2-holding or in "2on1" form (which makes a recursion). The exit of the recursion can only be DRC-2. So,

Condition: if the two columns have a seg_bot at the same height (excluding the bottom layer).

#### Summary

The exclusion in "2on1" is exactly the condition in "DRC-2".

So, the shape is reachable iff **the two columns have a seg_bot at the same height**.

You might have noticed some relations between "DRC-2" and "2on1". In the following cases, every "DRC-2" is merged into the corresponding "Kon1". 

### 1110

#### 2on2

##### 1010 on 1100

#### 3on1

### 1111

## Outro