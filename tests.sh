# python setup.py build_ext --inplace
# --buffer captures output unless a test fails
# tests is the folder where our tests are
python -m unittest discover --buffer --verbose tests
