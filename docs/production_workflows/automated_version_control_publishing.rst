Automated Version Control (VCS) Publishing (TODO)
------------------------------------------
If your project configuration specifies a version control system (``git``, ``svn``, or ``perforce``):

1. OpenPypeline Studio automatically invokes the corresponding VCS handler upon saving a **Master**.
2. The file is staged/reconciled, committed with the **Master** comment, and submitted to the server automatically.
3. If publishing encounters a network or conflict error, OPS alerts you in Maya's Script Editor log while preserving the local Master on disk.
