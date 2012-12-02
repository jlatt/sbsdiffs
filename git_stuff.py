import pygit2
repo = pygit2.Repository('/Users/jlatt/Projects/vb/apartmentlist/.git')

    from_commit = repo.revparse_single(from_commit_name)
    to_commit = repo.revparse_single(to_commit_name)
    diff = from_commit.tree.diff(to_commit.tree)
