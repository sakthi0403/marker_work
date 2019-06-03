import sys, subprocess

class Dependencies(object):

    def __init__(self, buildout, name, options):
        
        self.name, self.options = name, options

        # check required executables
        for system_package, checker in [
                line.split(':') for line in options['deps'].split('\n')]:
            sys.stdout.write('Checking ' + system_package + ': ')
            try:
                assert(not subprocess.call(checker, shell=True, stdout=subprocess.PIPE))
                print('ok')
            except AssertionError:
                raise EnvironmentError(
                    'Your system is missing the following dependency: %s' % system_package)

    def install(self):
        return []

    def update(self):
        pass
