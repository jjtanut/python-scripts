# Unit Testing Misc Notes

## Nose
Use nose to run all tests in a dir:

* `pip install nose`
* `nosetests`

## Individual tests
Can run as a normal python file: `python mytest_test.py`

## Mock in Python 2.x vs 3.x
In Python 3, MagicMock is part of unittest. However, in Python 2 you need to
install and import mock as a separate module.
