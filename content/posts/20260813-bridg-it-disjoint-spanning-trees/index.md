+++
author = "Shaojia"
title = "Bridg-it - Disjoint Spanning Trees"
date = "2026-08-13T14:56:26+08:00"
tags = []
description = ""
showFullContent = false
hideComments = false
+++

I recently reviewed _Introduction to Graph Theory_ by Douglas B. West, which is a fantastic book for beginners.

In Section 2.1 Tree and Distance - Basic Properties, I was attracted by the subsection Disjoint Spanning Trees (optional) when I first read it. The subsection is about a game called _Bridg-it_, whose rules can be found [here](https://www.hexwiki.net/index.php/Bridg-It). You can also play [here](https://mglaezer.github.io/bridgit/) against a robot.

Proposition: If $T,T'$ are spanning trees of a connected graph $G$ and $e\in E(T)- E(T')$, then there is an edge $e'\in E(T')- E(T)$ such that $T-e+e'$ is a spanning tree of $G$.

This proposition is obviously true: Let $U$ and $U'$ be the two components of $T-e$. Since $T'$ is connected, $T'$ has an edge $e'$ with endpoints in $U$ and $U'$. Now $T-e+e'$ is connected, has $n(G)-1$ edges, and is a spanning tree of $G$.

If we contract points that are linked with $E(T)\cap E(T')$, then the new spanning trees $T,T'$ satisfy $E(T)\cap E(T')=\emptyset$. Hence we can regard the overlapped edges as contractions.

Back to the _Bridg-it_ game. Player 1 (who plays first and connects solid points) has an explicit winning strategy by maintaining two spanning trees $T,T'$, shown in Fig 1 in solid and dot lines respectively. Unlike _bridg-it_, [hex game](https://en.wikipedia.org/wiki/Hex_(board_game)) has no explicit winning strategy for the first player, although the first player is guaranteed to win.

{{< figure src="fig1.png" alt="Fig 1" position="center" caption="Fig 1" captionPosition="center" >}}

Then it is easy to feel that $E(T)\cap E(T')$ edges represent bridges built by Player 1, since the proposition cannot guarantee what would happen if Player 2 destroys an edge in $E(T)\cap E(T')$.

We pretend Player 2 goes first and takes the auxiliary edge (the only curved edge in Fig 1). After Player 2 removes an edge from $T$, $T−e$ splits into two components. By the proposition, Player 1 can choose an edge $e'\in T'$ crossing these two components. Adding $e'$ to $T$ restores a spanning tree, and the new overlap edge $e'\in E(T)\cap E(T')$ is now occupied by Player 1 and cannot be destroyed by Player 2.

{{< figure src="fig2.png" alt="Fig 2" position="center" caption="Fig 2" captionPosition="center" >}}

Whenever an edge is broken by Player 2, Player 1 can find an edge in the other spanning tree and add it into that spanning tree. The game will end when $E(T)=E(T')$ or earlier. If they keep playing until $E(T)=E(T')$, then Player 1 can even guarantee to connect all solid points.

If the grid is not very small, it seems hard for Player 1 to maintain two spanning trees in their mind without a computer or paper and pen. Moreover, in fact, we have a simpler way to prove that Player 1 is certain to win (otherwise Player 2 has winning strategy, but Player 1 can steal the strategy first). This explicit winning strategy seems to be only useful for computers.