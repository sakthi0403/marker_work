Detailed Description
********************

.. contents::


Recipe Options
==============

``z3c.recipe.mkdir`` provides the following options:

* ``paths``
    Contains the path(s) of directories created in normalized,
    absolute form. I.e.::

      mydir/../foo/bar

    becomes::

      /path/to/buildout-dir/foo/bar

* ``remove-on-update``
     Default: ``no``

     By default, created directories are not removed
     on updates of buildout configuration. This is a security measure
     as created directories might contain valuable data.

     You can, however, enforce automatic removing on updates by
     setting this option to ``on``, ``yes`` or ``true``.

* ``user``
     Default: system-dependent

     You can optionally set a username that should own created
     directories. The username must be valid name (not an uid) and the
     system must support setting a user ownership for files. Of
     course, the running process must have the permission to set the
     requested user.

* ``group``
     Default: system-dependent

     You can optionally set a usergroup that should own created
     directories.The group name must be a valid name (not a gid) and
     the system must support setting a group ownership for files. Of
     course, the running process must have the permission to set the
     requested group.

* ``mode``
     Default: system-dependent

     You can optionally set file permissions for created directories
     as octal numbers as usually used on Unix systems. These file
     permissions will be set for each created directory if the running
     process is allowed to do so.

     Normally, a value of ``0700`` will give rwx permissions to the
     owner and no permissions to group members or others.

     If you don't specify a mode, the system default will be used.

* ``create-intermediate``
     Default: ``yes``

     If set to `no`, the parent directory of the path to create _must_
     already exist when running the recipe (and an error occurs if not).

     If set to `yes`, any missing intermediate directories will be
     created. E.g. if creating a relative dir

     ``a/b/c/``

     with ``create-intermediate`` set to ``no``, the relative path
     ``a/b/`` must exist already.


Simple creation of directories via buildout
===========================================

Lets create a minimal `buildout.cfg` file:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... ''')

Now we can run buildout:

  >>> print system(join('bin', 'buildout')),
  Installing mydir.
  mydir: created path: /sample-buildout/parts/mydir

The directory was indeed created in the ``parts`` directory:

  >>> ls('parts')
  d  buildout
  d  mydir


As we did not specify a special path, the name of the created
directory is like the section name ``mydir``.


Creating a directory in a given path
====================================

Lets create a minimal `buildout.cfg` file. This time the directory
has a name different from section name and we have to tell explicitly,
that we want it to be created in the ``parts/`` directory. We set the
``paths`` option to do so:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = ${buildout:parts-directory}/myotherdir
  ... ''')

Now we can run buildout:

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/parts/myotherdir

The directory was indeed created:

  >>> ls('parts')
  d  buildout
  d  mydir
  d  myotherdir


Creating directories that are removed on updates
================================================

We can tell the recipe that a directory should be removed on updates by using
the ``remove-on-update`` option:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... remove-on-update = true
  ... paths = newdir
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/newdir

The ``newdir/`` directory was created:

  >>> ls('.')
  -  .installed.cfg
  d  bin
  -  buildout.cfg
  d  develop-eggs
  d  eggs
  d  newdir
  d  parts

We rewrite `buildout.cfg` and set a different path:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... remove-on-update = true
  ... paths = newdir2
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/newdir2

Now ``newdir/`` has vanished and ``newdir2`` exists:

  >>> ls('.')
  -  .installed.cfg
  d  bin
  -  buildout.cfg
  d  develop-eggs
  d  eggs
  d  newdir2
  d  parts

Note, that the created directory will be removed on next modification
of `buildout.cfg`.

Setting User, Group, and Permissions
====================================

You can optionally set ``user``, ``group``, or ``mode`` option for the
dirs to be created.

While ``user`` and ``group`` give the user/group that should own the
created directory (and all not existing intermediate directories),
``mode`` is expected to be an octal number to represent the directory
permissions in Unix style.

Of course, setting all these permissions and ownerships only works if
the system supports it and the running user has the permissions to do
so.

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = my/new/dir
  ... mode = 700
  ... user = %s
  ... group = %s
  ... ''' % (user, group))

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/my
  mydir:   mode 0700, user 'USER', group 'GROUP'
  mydir: created path: /sample-buildout/my/new
  mydir:   mode 0700, user 'USER', group 'GROUP'
  mydir: created path: /sample-buildout/my/new/dir
  mydir:   mode 0700, user 'USER', group 'GROUP'

  >>> lls('my')
  drwx------ USER GROUP my/new

  >>> lls('my/new')
  drwx------ USER GROUP my/new/dir


These options are optional, so you can leave any of them out and the system
defaults will be used instead.

.. note:: Please note, that the permissions will only be set on newly
          created directories. On updates only the permissions of the
          leaf directory will be updated, not any intermediate
          directories (except you set remove-on-update, which will
          recreate also intermediate paths and set permissions
          accordingly).

On updates only the leaf directories are changed
permission-wise. E.g. if we change the mode from the original buildout
from ``0700`` to ``0750``:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = my/new/dir
  ... remove-on-update = true
  ... mode = 750
  ... user = %s
  ... group = %s
  ... ''' % (user, group))

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: set permissions for /sample-buildout/my/new/dir
  mydir:   mode 0750, user 'USER', group 'GROUP'

the permissions of the leaf directory were updated:

  >>> lls('my/new')
  drwxr-x--- USER GROUP my/new/dir

while its parent's permissions are the same as before:

  >>> lls('my')
  drwx------ USER GROUP my/new


Clean up:

  >>> import shutil
  >>> shutil.rmtree('my')

Creating relative paths
=======================

If we specify a relative path, this path will be created relative to the
buildout directory:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = myrootdir
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/myrootdir


  >>> ls('.')
  -  .installed.cfg
  d  bin
  -  buildout.cfg
  d  develop-eggs
  d  eggs
  d  myrootdir
  d  parts

  The old directories will **not** vanish:

  >>> ls('parts')
  d  buildout
  d  mydir
  d  myotherdir


Creating intermediate paths
===========================

If we specify several levels of directories, the intermediate parts
will be created for us as well by default:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = myrootdir/other/dir/finaldir
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/myrootdir/other
  mydir: created path: /sample-buildout/myrootdir/other/dir
  mydir: created path: /sample-buildout/myrootdir/other/dir/finaldir

  >>> ls('myrootdir', 'other', 'dir')
  d  finaldir

If we set the ``create-intermediate`` option to ``no`` (default is
``yes``), the resulting dir will only be created if the parent
directory exists already:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = leaf/dir/without/existing/parent
  ... create-intermediate = no
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  While:
    Installing mydir.
  Error: Cannot create: /sample-buildout/leaf/dir/without/existing/parent
         Parent does not exist or not a directory.

If you want to be explicit about the paths to be created (and which
not), you can set ``create-intermediate`` to ``no`` and simply list
each part of the path in ``paths`` option. This has the nice
sideeffect of setting permissions correctly also for intermediate
paths:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = mydir
  ...         mydir/with
  ...         mydir/with/existing
  ...         mydir/with/existing/parent
  ... create-intermediate = no
  ... mode = 750
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Installing mydir.
  mydir: created path: /sample-buildout/mydir
  mydir:   mode 0750
  mydir: created path: /sample-buildout/mydir/with
  mydir:   mode 0750
  mydir: created path: /sample-buildout/mydir/with/existing
  mydir:   mode 0750
  mydir: created path: /sample-buildout/mydir/with/existing/parent
  mydir:   mode 0750

This is more to write down, but you can be sure that only explicitly
named dirs are created and permissions set accordingly.


Paths are normalized
====================

If we specify a non-normalized path (i.e. one that contains references
to parent directories or similar), the path will be normalized before
creating it:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = myroot/foo/../dir1/../bar/.
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/myroot
  mydir: created path: /sample-buildout/myroot/bar

Only ``bar/`` will be created:

  >>> ls('myroot')
  d  bar


Creating multiple paths in a row
================================

We can create multiple paths in one buildout section:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = myroot/dir1
  ...         myroot/dir2
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/myroot/dir1
  mydir: created path: /sample-buildout/myroot/dir2


  >>> ls('myroot')
  d  bar
  d  dir1
  d  dir2

Note, that in this case you cannot easily reference the set path from
other recipes or templates. If, for example in a template you
reference::

  root_dir = ${mydir:path}

the result will become::

  root_dir = /path/to/buildout/dir1
  path/to/buildout/dir2

If you specify only one path, however, the second line will not appear.

Use several sections using `z3c.recipe.mkdir` if you want to reference
different created paths from templates or similar.


Trailing slashes do not matter
==============================

It doesn't matter, whether you specify the paths with trailing slash
or without:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = myroot/dir3/
  ...         myroot/dir4
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/myroot/dir3
  mydir: created path: /sample-buildout/myroot/dir4

  >>> ls('myroot')
  d  bar
  d  dir1
  d  dir2
  d  dir3
  d  dir4

Things to be aware of
=====================

If you change the setting of some path, the old directory and all its
contents will **not** be deleted (as you might expect from a buildout
recipe):

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = path1
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/path1

  >>> write(join('path1', 'myfile'), 'blah\n')
  >>> ls('path1')
  -  myfile

Now we switch the setting of mydir to ``path2``:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = path2
  ... ''')

  >>> print system(join('bin', 'buildout'))
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/path2
  <BLANKLINE>

The file we created above is still alive:

  >>> ls('path1')
  -  myfile


Things, one should not do
=========================

Trying to create directories that exist and are files
-----------------------------------------------------

If a part of a given path already exists and is a file, an error is
raised:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = rootdir2/somefile/foo
  ... ''')

Now we create the first part of the path beforehand:

  >>> import os
  >>> os.mkdir('rootdir2')

And make the second part of the path a file:

  >>> write(join('rootdir2', 'somefile'),
  ... '''
  ... blah
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  While:
    Installing mydir.
  Error: Cannot create directory: /.../rootdir2/somefile. It's a file.


Don't use ``path`` option
-------------------------

.. note:: ``path`` is deprectated!

Starting with version 0.3 the ``path`` option is deprecated. Use
``paths`` instead:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... path = myrootdir
  ... remove-on-update = yes
  ... ''')

  >>> print system(join('bin', 'buildout')),
  mydir: Use of 'path' option is deprectated. Use 'paths' instead.
  Installing mydir.
  mydir: set permissions for /sample-buildout/myrootdir

The ``path`` option will be supported only for a limited time!


Referencing options
===================

From other buildout recipe components you can reference the options of
`z3c.recipe.mkdir` like this::

  ${<sectionname>:paths}

where ``<sectionname>`` is the name of the `buildout.cfg` section
wherein you set the paths.

Options `mode`, `user`, and `group` are only referencable if they are
explicitly set.

Referencing without giving a path
---------------------------------

You can reference also, if no path was given explicitly in
`buildout.cfg`:

  >>> import z3c.recipe.mkdir
  >>> buildout = dict(
  ...   buildout = {
  ...     'directory': '/buildout',
  ...     'parts-directory' : '/buildout/parts',
  ...   },
  ...   somedir = {},
  ... )

  >>> recipe = z3c.recipe.mkdir.Recipe(
  ...   buildout, 'somedir', buildout['somedir'])

  >>> print buildout['somedir']['paths']
  /buildout/parts/somedir

This means that if you have a `buildout.cfg` like this::

  [buildout]
  parts = somedir ...

  [somedir]
  recipe = z3c.recipe.mkdir

  ...

then for instance in a template you can write::

  mydir = ${somedir:paths}

which will turn into::

  mydir = /buildout/parts/somedir


Referencing with single path set
--------------------------------

If you reference a single path, you will get this back in references:

  >>> buildout = dict(
  ...   buildout = {
  ...     'directory': '/buildout',
  ...     'parts-directory' : '/buildout/parts',
  ...   },
  ...   somedir = {
  ...     'paths' : 'otherdir',
  ...   },
  ... )

  >>> recipe = z3c.recipe.mkdir.Recipe(
  ...   buildout, 'somedir', buildout['somedir'])

  >>> print buildout['somedir']['paths']
  /sample-buildout/otherdir

Referencing with multiple paths set
-----------------------------------

If you set several paths in `buildout.cfg`, you will get several lines
of output when referencing:

  >>> buildout = dict(
  ...   buildout = {
  ...     'directory': '/buildout',
  ...     'parts-directory' : '/buildout/parts',
  ...   },
  ...   somedir = {
  ...     'paths' : 'dir1  \n  dir2',
  ...   },
  ... )

  >>> recipe = z3c.recipe.mkdir.Recipe(
  ...   buildout, 'somedir', buildout['somedir'])

  >>> print buildout['somedir']['paths']
  /sample-buildout/dir1
  /sample-buildout/dir2
