---
tags: [design]
max_turns: 80
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Design and build the main screen of Rootstock, a web app for small wholesale plant nurseries. The nursery manager opens it every morning to see: which orders must be picked and loaded today (customer, number of trays, bay location, van and departure time), which stock is running low or has been held too long on the benches, and what is arriving from propagation this week. Typical nursery: about 400 plant lines, 30 to 60 orders a day in spring, two vans. Staff use it on a desktop in the potting shed office and on a tablet out on the benches. Make the Today screen with realistic sample data (real plant names in the usual Latin plus cultivar form, pot sizes like 9cm and 2L, tray counts, bay codes), responsive down to tablet and phone.

About us: it is used all day by the manager and two or three staff, often with wet or gloved hands on the tablet, in bright daylight. No logo, colours or fonts yet. It should feel practical, legible and unfussy, never like a tech startup dashboard. We like printed plant labels, picking lists on a clipboard and the delivery board by the loading bay. Plain HTML and CSS, WCAG AA, free fonts only. I cannot answer questions right now, so decide what you need to and tell me your assumptions. Put the screen in index.html.
