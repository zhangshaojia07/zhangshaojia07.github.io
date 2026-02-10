+++
author = "Shaojia"
title = "Which Shapes Are Reachable in Shapez?"
date = "2026-02-10T17:22:38+08:00"
tags = []
cover = ""
description = "After going through a series of random attempts, I put this project on hold for over a year. Now, it's time to finish what we started but left unfinished before."
showFullContent = false
hideComments = false
+++

<div style="float: right; margin: 0 0 10px 15px;">
<iframe width="250" height="100" scrolling="no" frameborder="no" allow="autoplay" src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/soundcloud%253Atracks%253A891432268&color=%23e8c45c&auto_play=false&hide_related=true&show_comments=false&show_user=false&show_reposts=false&show_teaser=false"></iframe>
</div>

Ever since Christmas 2024, when I was still preparing for the <abbr title="National Olympiad in Informatics ">NOI</abbr> Provincial Team Selection Competition (which I would later fail), I had already completed the game Shapez<cite>[^1]</cite> and built a working Everything Machine. Well, accurately speaking, not *every* shape can be made from it. It’s designed for random 4-layer full shapes, the kind you get in freeplay<cite>[^2]</cite> (so e.g., [rocket shape](https://shapezio.fandom.com/wiki/Level_26) is excluded). Since then, I've been fixated on making a genuine Everything Machine that supports any layer count and fills in the void spaces inside shapes. So the first thing I needed to do was figure out which shapes could actually be built using stackers, rotators, and cutters. I even had a dream back then: if I could fully solve the reachability problem (preferably with an efficient algorithm), I could turn it into an OI problem.

[^1]: Shapez Demo <https://shapez.io/> <br/> Steam Webpage <https://store.steampowered.com/app/1318690/Shapez/>

[^2]: Freeplay refers to levels 27 and above. All levels before this have a specific shape requirement. From level 27 onward the shape requirements are randomly generated shapes starting with 2 layers and going up to 4 layers at the most.

After going through a series of random attempts, I put this project on hold for over a year. Now, it's time to finish what we started but left unfinished before.