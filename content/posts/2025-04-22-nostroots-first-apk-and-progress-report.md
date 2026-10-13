---
title: "nostroots: first apk and progress report"
date: "2025-04-22T11:11:30+02:00"
url: "/2025/04/22/nostroots-first-apk-and-progress-report/"
author: "Trustroots"
draft: false
---

tl;dr:

[apk at github](https://github.com/Trustroots/nostroots/releases/)

We set up a

[Nostroots home page](https://team.trustroots.org/nostr.html)

, with the most important information for normal users. For devs there's https://github.com/trustroots/nostroots

And here's (most of) the progress report that we wrote for November 2024 till April 2025.

### Project updates

At November's hackathon week we decided to go for expo.dev with react native. This has worked out well now. The alpha version of our Android app is ready for testing. If you're feeling adventurous, grab the APK and see what we've built so far. You can post notes on a map, and also see geographic notes from other sources.

App flow and onboarding was a challenge. Giving non-tech users the benefits of decentralized tech without overwhelming them. We aim to strike a balance between usability and tech elitism.

Our focus on Android for now

[due to some Expo map component issues on iOS](https://github.com/trustroots/nostroots/issues/92)

lets us move forward with testing while we work through cross-platform challenges. This week's first Android APK

[release](https://github.com/Trustroots/nostroots/releases/)

is an important step for hallway testing, although the app still is, in parts, a bug fest.

In terms of code, a lot has been going straight to the main branch so far, which makes it a bit harder to give you many nice links here.

### Team

We are happy to have onboarded a new front end developer (awongh) who has

[been committing](https://github.com/Trustroots/nostroots/commits/main/?author=awongh)

great work on the frontend. With chmac, guaka, shuesken and zrthstr we are 5 committed to putting trustroots on nostr.

### Connecting with other orgs and apps

We gauged the possibility of connecting over nostr with similar organizations and met up in person with people from couchers.org, but it's hard to convince them that nostr is the way.

Likewise guaka as well as tillwenke met up in person with the main person behind hitchmap (bopjesvla) but we weren't able to convince him to make nostr a core part of the application.

There is ongoing positive communication with triphopping and time safari but there is no clear path forward.

But now that we have an apk out it, it's easier to show the potential of nostr.

### Current state of the nostroots code and app

Mostly monorepo now, app as well as server code are in one place https://github.com/Trustroots/nostroots/issues?q=is%3Aissue%20state%3Aclosed%20label%3Anr-common

- Onboarding: private key and mnemonic are created, user is guided to adding the npub to their trustroots profile, which is then NIP-05 verified
- User can add notes on the map by long pressing, these are NIP-05 verified by the validation server https://github.com/Trustroots/nostroots/tree/main/nr-server/src
- A dev switch, off by default, can show work in progress (e.g. the NIP-46 login tab)
- User can decide to show several additional map layers:
  - unverified, if third parties would follow [our format](https://github.com/Trustroots/nostroots/blob/main/docs/Events.md), or if there's a problem with the validation server
  - 1000+ nostr notes with useful real world information for hitchhikers
    - hitchwiki notes coming from https://github.com/Hitchwiki/hwpybot
    - hitchmap notes coming from https://github.com/Hitchwiki/nostrhitch
  - the dev switch enables additional layers: triphopping and time safari

### Work in progress

#### Improving UI/UX

Next steps:
- Make it more pluscode-y, showing grid, make it clear that a note is related to a specific pluscode, currently there's a pluscode switch after you toggle the dev switch
- Optionally add one of the 20+ trustroots circles to notes when adding new notes https://github.com/Trustroots/nostroots/issues/96
- hitchmap/hitchwiki in the hitchhiker circle?
- select drop down instead of radio buttons
- iframe that can be added to legacy trustroots.org pages, e.g. circle pages, as part of the nostr adoption funnel

#### Push notifications

Push notifications are essential for our app’s functionality due to limitations in modern mobile ecosystems, where background fetch capabilities are restricted.

We are close to implementing privacy-preserving push notifications, which is a key requirement.

The concept is that users can subscribe to specific Plus Code areas (or types, or any kind of Nostr filters) and receive push notifications when relevant events occur within those areas or meet those criteria. To ensure encryption while adhering to decentralized principles, the push notifications serve as a trigger, nudging the app to open. Once opened, the app can fetch data via the regular WebSocket, using Nostr's encryption features.

The notification, filter matching and push sending is implemented here https://github.com/trustroots/notification-daemon

#### MediaWiki nostr auth

The

[MediaWiki Nostr Auth](https://github.com/Trustroots/mediawiki-nostr-auth)

extension is currently NIP-07 based and quite usable for signing up and logging back in with a NIP-05 trustroots profile on nomadwiki.org and trashwiki.org.

The Nostroots app is capable of NIP-46 logins. https://github.com/Trustroots/nostroots/issues/47

Next steps:
- add nostr login to hitchwiki.org
- add NIP-46 for a much nicer process that doesn't rely on a desktop only browser extension, allowing nostroots app users to log in
- reach out to the developer of the

[WordPress Nostr NIP-07](https://wordpress.org/plugins/nostr-login/)

plugin to also support NIP-46

### Future

Most of the activity takes place around our hackathons. https://github.com/trustroots/nostroots/graphs/commit-activity
So we will keep doing these regularly, at least quarterly.

Now that we have an app we're ready to add some nostr stats to our grafana: number of trustroots users with an npub as well as the number of geo notes posted. https://github.com/trustroots/nostroots/issues/95

#### Outreach

https://github.com/trustroots/nostroots/issues/57

- Promote on hitchwiki.org and the active hitchwiki matrix/signal group (700+ members) after a bit more hallway testing and minor improvements.
- Promote on the nostr social media sphere, and vice versa when nos.social releases an android app (culture fits with our user base)
- Start integrating trustroots.org (e.g. iframe maps) when we have more notes coming from the nostroots app
- Email, e.g. send out mailinglist email to 28k subscribers, add to standard trustroots.org email template
