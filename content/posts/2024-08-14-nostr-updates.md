---
title: "Nostr updates"
date: "2024-08-14T10:58:17+02:00"
url: "/2024/08/14/nostr-updates/"
author: "Trustroots"
draft: false
tags: []
categories: ["nostr", "Technical", "Trustroots", "Volunteering"]
---

We recently held a weekend hackathon to make notes.trustroots.org even better!

A lot of our work focused on making sure that the notes we display on our map are trustworthy. We want to avoid showing any spam or invalid content, so we’ve set up a system to verify that notes come from real Trustroots users. Our solution involves running a server that checks the source of each note and reposts it with extra information. When you add a note to the map, it creates an event, but only notes from verified users will be shown.

If anyone wants to create their own version of this, they can set up their own server to check notes in different ways.

We also completed an important update called NIP-05 on [trustroots.org](https://www.trustroots.org/profile/edit/networks). This means you can now verify your Trustroots username in other Nostr applications. You can see how it works at our [Nostroots profile on Satellite](https://satellite.earth/@npub1lt6a968lk4h6yqduqnxcha628cudulgy8xk607c4xyxn6d6w6kcsmgp8hj).

Additionally, we’ve added [server-side code](https://github.com/Trustroots/nostroots-server) that checks if notes are coming from actual Trustroots users. While this does centralize some processes, it helps us move towards a more decentralized future for Nostroots.

We now offer temporary notes that last for 5 minutes, but you can still choose to keep notes indefinitely if you prefer.

The platform is more reliable now, with clearer error messages in the JavaScript console to help with troubleshooting.

Lastly, we connected with Trent Larson, who is working on [Lives of Giving](https://livesofgiving.org/), and checked in with Kenny, who is making progress on adding Nostr features to [triphopping.com](https://triphopping.com/).

## Funding

We’re excited to share that we are receiving [funding](https://opensats.org/blog/nostr-grants-august-2024) to help us move Trustroots to Nostr. This will also help more people learn about what we’re doing:

> *"Really excited about @Nostroots !*
> *I’ve been saying for a while now that someone should make couchsurfing on nostr…Couchsurfing around 2010 was like the greatest thing ever, and it was such a tragedy when the admins sold out and rugged everyone who had built up connections. Building it on nostr is a great use case showing how we can preserve social capital."* — [Stuart Bowman](https://satellite.earth/thread/1a81f4dfbf7eebf0fda3284657b1f71038590782f01346fc5a36e174854b8213)

## Wanna help?

We’re always looking for enthusiastic individuals to join us in this exciting journey! We're specifically interested in people who want to help with communication. If you know a little about nostr and are interested in helping us bring this idea to the community, please [reach out on nostr](https://satellite.earth/@npub1lt6a968lk4h6yqduqnxcha628cudulgy8xk607c4xyxn6d6w6kcsmgp8hj). Together, we can build a stronger community!
