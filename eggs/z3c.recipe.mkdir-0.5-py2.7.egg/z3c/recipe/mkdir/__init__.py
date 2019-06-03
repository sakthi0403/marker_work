import logging
import os
import zc.buildout

class Recipe:
    def __init__(self, buildout, name, options):
        self.buildout=buildout
        self.name=name
        self.options=options
        self.logger=logging.getLogger(self.name)
        self.remove_on_update = string_to_bool(
            options.get('remove-on-update', 'no'))
        self.create_intermediate = string_to_bool(
            options.get('create-intermediate', 'yes'))

        if 'path' in options.keys():
            self.logger.warn(
                "Use of 'path' option is deprectated. Use 'paths' instead.")

        paths = options.get(
            'paths', options.get('path', os.path.join(
                buildout['buildout']['parts-directory'], name)))
        self.paths = []
        for path in paths.split('\n'):
            path = path.strip()
            if not path:
                # don't consider empty dirs
                continue
            self.paths.append(os.path.normpath(os.path.abspath(path)))
        self.paths = sorted(self.paths)

        self.mode = options.get('mode', None)
        if self.mode is not None:
            try:
                self.mode = int(self.mode, 8)
            except ValueError:
                raise zc.buildout.UserError(
                    "'mode' must be an octal number: " % self.mode)

        # determine user id
        self.user = options.get('user', None)
        self.uid = -1
        if self.user:
            try:
                import pwd
                self.uid = pwd.getpwnam(options['user'])[2]
            except ImportError:
                self.logger.warn(
                    "System does not support `pwd`. Using default user")

        # determine group id
        self.group = options.get('group', None)
        self.gid = -1
        if self.group:
            try:
                import grp
                self.gid = grp.getgrnam(options['group'])[2]
            except ImportError:
                self.logger.warn(
                    "System does not support `grp`. Using default group")

        # Update options to be referencable...
        options['path'] = options['paths'] = '\n'.join(self.paths)
        options['create-intermediate'] = '%s' % self.create_intermediate
        options['remove-on-update'] = '%s' % self.remove_on_update
        if self.mode:
            options['mode'] = oct(self.mode)
        if self.user:
            options['user'] = self.user
        if self.group:
            options['group'] = self.group

    def install(self):
        for path in self.paths:
            self.createIntermediatePaths(path)
        return self.options.created()

    def update(self):
        return self.install()

    def createIntermediatePaths(self, path):
        parent = os.path.dirname(path)
        if self.create_intermediate is False:
            if path in self.paths and not os.path.isdir(parent):
                raise zc.buildout.UserError(
                    "Cannot create: %s\n"
                    "       Parent does not exist or not a directory." % path)
        if os.path.exists(path) and not os.path.isdir(path):
            raise zc.buildout.UserError(
                "Cannot create directory: %s. It's a file." % path)
        if parent == path or os.path.exists(path):
            if path in self.paths:
                self.logger.info('set permissions for %s' % path)
                self.setPermissions(path)
            return
        if not os.path.isdir(parent):
            self.createIntermediatePaths(parent)
        os.mkdir(path)
        self.logger.info('created path: %s' % path)
        self.setPermissions(path)
        if self.remove_on_update:
            self.options.created(path)

    def setPermissions(self, path):
        additional_msgs = []
        if self.mode is not None:
            os.chmod(path, self.mode)
            additional_msgs.append('mode 0%o' % self.mode)
        if self.uid != -1 or self.gid != -1:
            os.chown(path, self.uid, self.gid)
            if self.uid != -1:
                additional_msgs.append("user %r" % self.user)
            if self.gid != -1:
                additional_msgs.append("group %r" % self.group)
        if additional_msgs:
            self.logger.info('  ' + ', '.join(additional_msgs))


def string_to_bool(value):
    if value is True or value is False:
        return value
    value = value.lower()
    return value in ['yes', 'on', 'true', '1']
