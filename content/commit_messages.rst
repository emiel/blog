On Commit Messages
##################

:date: 2021-03-19 17:00
:tags: vcs, scm, git, svn, cvs
:category: tech
:status: published
:authors: Emiel van de Laar

Most if not all version control systems allow for annotating a change with a
descriptive message. On many occasions, I've needed to convince others that
this is a fantastic feature that should be taken advantage of. Here's my take
on the matter.

Why write messages at all?
--------------------------

Here's why:

- **Context**: A well-written commit message is the best way to communicate
  valuable context about a change to other project contributors, and indeed, to
  your future self. By first reading the commit message the reader should have
  enough of an introduction and/or understanding to be able to grasp the code
  changes that follow.

- **Collaboration**: Without any kind of introduction to the change, other
  contributors need to track you down to retrieve it. We should be considerate
  and spare them the effort. If more in-depth details are required they will
  track you down anyway. ;) Besides you're collaborating here and this is a
  great opportunity to share some knowledge.

- **History**: Any kind of "real world" project will accumulate a fair amount
  of history via other contributors. For anyone joining the project at a later
  time, the commit history can tell a valuable story if decent commit messages
  have been written. There can be real value here. "Uhm, why was it done like
  that? (git log) Ah, I see!"

So go ahead and take a few minutes to compose a message. Your readers
(including yourself) will be better off. ;) If you need more convincing, "`My
favourite Git commit`_", is one of my favorite posts on this subject.

.. _`My favourite Git commit`: https://dhwthompson.com/2019/my-favourite-git-commit

What should I write?
--------------------

What you should write depends on the change you are introducing. You should
judge for yourself how much detail to include; just keep your reader in mind.

- Write at the very least a decent subject line. Messages like "WIP" (work in
  progress) are fine for your topic branches but should be updated before the
  change lands in the "main/master" branch.

- Go ahead and summarize the change made so the reader knows what they are
  looking at. If you find your message is getting a bit long it may be a sign
  you need to break up the change into smaller chunks, i.e. multiple commits.

Let's go ahead and cover some common changes:

- **Functional change**: Provide motivation for the change and convey intent.
  Why are these changes needed? What issue does it solve? What is the added
  value? This is especially important in production code. Also, a reference to
  a related discussion, i.e. issue tracking system, will be appreciated.

- **Hairy bug fix**: You spent an insane amount of time tracking down a nasty
  bug. Go ahead and document the funky behavior in the change as a comment
  instead of including your full war-story in the commit message. When
  revisiting the code the adjacent comment will likely be spotted but the
  commit message won't.

- **Spelling correction**: A single line subject will suffice. Don't go
  overboard.
