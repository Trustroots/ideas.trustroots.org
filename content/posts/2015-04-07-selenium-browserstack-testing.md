---
title: "We're now testing with Browserstack"
date: "2015-04-07T12:05:29+02:00"
url: "/2015/04/07/selenium-browserstack-testing/"
author: "guaka"
draft: false
---

[Test driven development](https://en.wikipedia.org/wiki/Test-driven_development)

is great. Before you create new features or fix a bug you first write a test case that covers the specific issue. In the long run this means that you're avoiding unforeseen side effects and that the entire code base is a lot more stable.

[Selenium](http://www.seleniumhq.org/)

testing is great in that you're testing your web project in an actual browser. It's a pain to run 38 different browsers on 7 different platforms though. Fortunately there's a service that can handle that for you:

[Browserstack](https://www.browserstack.com/)

.

[![Browserstack](/images/2015/04/browserstack-logo-300x65.png)](https://www.browserstack.com/)

Yesterday I started writing some Selenium

[tests](https://github.com/Trustroots/trustroots/issues/225)

for Trustroots. So the next step was to apply for Browserstack's free program for open source projects. And within less than 12 hours we have a free Trustroots automate account. This will make the entire experience a lot more smooth in the long run, both for developers and users.

Ideally we'll have a

[CI-ish](https://github.com/Trustroots/trustroots/issues/228)

setup (through

[Ansible](https://github.com/Trustroots/trustroots/issues/221)

) at some point, where when new code is pushed to the repository, this code will be pulled on our dev site, the tests will be run and new GitHub issues (with screenshots) will appear automatically. We're not there yet but the first steps have been made.

[Contact](/contact/)

us if you want to help with all these things, or even better, jump in

[directly on GitHub](https://github.com/Trustroots/trustroots/wiki/Volunteering)

!
