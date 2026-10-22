+++
author = "Shaojia"
title = "QRT x C3 Hackathon: 9th Place in a 2-Hour Agentic Coding Sprint"
date = "2026-10-22T15:26:42+01:00"
tags = ["Hackathon", "Competitive Programming", "Algorithms", "AI", "Cambridge"]
description = "Yesterday evening I joined Reet, Artem and Vedant for the QRT x C3 Hackathon hosted by CUCaTS. We placed 9th in a fast-paced two-hour agentic coding sprint built around four open-ended optimisation challenges."
cover = "cover.png"
showFullContent = false
hideComments = false
+++

Yesterday evening I joined Reet, Artem and Vedant for the **QRT x C3 Hackathon** hosted by [CUCaTS](https://cucats.org/), and we finished **9th place**. The event was held at Christ's College, whose buildings made for a rather scenic setting.

{{< figure src="venue.jpeg" alt="Christ's College" position="center" caption="Christ's College" captionPosition="center" >}}

It was a two-hour **agentic coding sprint**: four challenges, one strict clock, and AI tools not just permitted but practically mandatory. Unlike a classic competitive-programming contest where you read stdin and print stdout, every challenge here was a small, open-ended optimisation problem. We split the four of them up based on our strengths and raced to squeeze as much score out of each one as possible before the timer ran out.

The problems were a lot of fun. One had us probing a black box to maximise its output: you only learn what the box does by feeding it queries. Another asked us to optimise a word-search grid on a wrap-around torus topology, which is exactly as cursed as it sounds. That one fell to Artem, who built the search-optimisation algorithm and landed the highest score on our team.

The problem I owned was deceptively simple and classically NP-hard: pack a bunch of axis-aligned squares of different side lengths into the smallest-area rectangle possible. I'd planned to let Google OR-Tools do the heavy lifting through the CP-SAT solver's `NoOverlap2D` constraint, but it turned out competition submissions weren't allowed to use third-party Python libraries: a real shame, since I'd already spent a while fiddling with OR-Tools' CP-SAT before finding out.

{{< figure src="coding.jpeg" alt="us coding at the venue" position="center" caption="Coding at the venue" captionPosition="center" >}}

The grader showed you your own output but kept the input hidden, so I ended up writing a script to reverse-engineer the input from my own output, then pulled the JSON packets straight out of the browser's F12 dev tools to batch-process the cases. It was a bit hacky and ate up a fair amount of time, and in the end my score on that problem still fell short of the top few teams.

{{< figure src="workspace.png" alt="VS Code and Codex" position="center" caption="My workspace during the contest: VS Code and the Codex window" captionPosition="center" >}}

With only two hours on the clock there was no room for a careful, read-everything-first approach. The workflow that actually won out was: skim a problem, spin up a quick script with heavy help from AI tools, throw it at the grader, and iterate. It felt less like problem solving and more like a pit stop.

{{< figure src="leaderboard.jpeg" alt="live leaderboard" position="center" caption="The live leaderboard: we're 9th, though our team name is partly hidden behind the people in front" captionPosition="center" >}}

A huge thanks to Qube Research & Technologies and the Cambridge University Computer Technology Society for organising such an engaging event, and a shout-out to my teammates Reet, Artem and Vedant: great work under pressure.

{{< figure src="swag.jpeg" alt="metal tumbler and cards" position="center" caption="The swag: a lidded metal tumbler and a deck of cards" captionPosition="center" >}}
