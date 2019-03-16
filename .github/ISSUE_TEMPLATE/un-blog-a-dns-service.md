---
name: UN-Blog a DNS Service
about: To get a DNS server unblocked you should be as luckyas wimming all loteries
  out there, if first added, it almost certain that it stays
title: UN-Block DNS Servers
labels: ''
assignees: spirillen

---

**Short Description**
A clear and concise description of what you expected to happen.

**Warning this requires more than one safe domain**

```
example.org.rpz-nsdname  CNAME   rpz-passthru.
*.example.org.rpz-nsdname  CNAME   rpz-passthru.
```
(Replace `example.org` with the real domain name of the server you think we should be blocking

### All Submissions:

* [ ] Have you followed the guidelines in our Contributing document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

<!-- You can erase any parts of this template not applicable to your Pull Request. -->

### New Domain Submissions:

1. [ ] Does your submission pass tests?
1. [ ] Have you lint your code locally prior to submission?
1. [ ] Added ScreenDump for profe of False Positive

### Changes to Core Features:

* [ ] Have you added an explanation of what your submission do and why you'd like us to include them?
* [ ] Have you successfully ran tests with your changes locally?

### Check list For Team members only!!!!
* [ ] DNS RPZ
* [ ] Bind RPZ
