---
name: False Positive
about: The right form to report False Positives (Domain should NOT have been blocked)
title: 'False Positive: '
labels: False Positive
assignees: spirillen

---

**Short Description**
A clear and concise description of what you expected to happen.

```
example.org  CNAME   rpz-passthru.
*.example.org  CNAME   rpz-passthru.
```
(Replace example.org with actual domain to un-block)

### All Submissions:

* [ ] Have you followed the guidelines in our Contributing document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

<!-- You can erase any parts of this template not applicable to your Pull Request. -->

### New Domain Submissions:

1. [ ] Does your submission pass tests?
1. [ ] Have you lint your code locally prior to submission?
1. [ ] Added ScreenDump for prove of False Positive

### Changes to Core Features:

* [ ] Have you added an explanation of what your submission do and why you'd like us to include them?
* [ ] Have you successfully ran tests with your changes locally?

### Check List For Team members only!!!!
* [ ] DNS RPZ
* [ ] Whitelisted domain
* [ ] Bind RPZ
