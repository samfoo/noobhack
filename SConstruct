env = Environment()
env.SharedLibrary(target="setrandom", source=["native/random.c"])

# This builds the shared library. To load it, do something like...
# $ export DYLD_INSERT_LIBRARIES=`pwd`/libsetrandom.dylib
# $ export DYLD_FORCE_FLAT_NAMESPACE=1
# $ nethack
