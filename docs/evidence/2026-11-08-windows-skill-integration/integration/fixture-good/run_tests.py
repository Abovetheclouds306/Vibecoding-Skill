import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
suite=unittest.defaultTestLoader.discover(str(pathlib.Path(__file__).parent),pattern="test_*.py")
result=unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
