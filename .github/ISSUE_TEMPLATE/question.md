---
name: Question
about: Ask a question
title: "[Question]"
labels: ''
assignees: ''

---

name: Question
description: Ask a question
title: "[Question] "
labels: [question]
body:
  - type: checkboxes
    attributes:
      label: Checklist
      description: >
        To help keep this issue tracker clean and focused, please make sure that you have
         tried *all* of the following resources before submitting your question.
      options:
        - label: I looked for [similar issues](https://github.com/nasa/ncompare/issues).
          required: true
        - label: I looked up my question/problem in a search engine.
          required: true
  - type: textarea
    attributes:
      label: Question
      description: Please ask your question
    validations:
      required: true
