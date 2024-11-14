from unittest import TestLoader

import xmlrunner

loader = TestLoader()
suite = loader.discover("tests")
xmlrunner.XMLTestRunner(verbosity=2).run(suite)
