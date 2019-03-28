# CFFI
**Do all this in the vagrant VM**
- Clone kubos repo
- In the apis/isis-imtq-api directory, need to change module.json so that it doesn't use a nonexistant copy of ccan-json (I just googled and made a new module)
- In ~/.kubos/kubos/target/target-{kubos-gcc,x86-linux-native}/CMake/toolchain.cmake , you need to add -fPIC to the C and CXX compiler args
- Run `yotta target` to show target, use `yotta target kubos-linux-beaglebone` or `yotta target x86-linux-native` to switch between compiler targets
- To build shared library:
	- Go to build dir (build/$target)
	- Collect list of object files: `find ym source -name *.o > objfiles`
	- You might have to remove a few files from that list (like GPIO) if something complains
	- Compile everything into a shared lib: 
		- *arm*: < `objfiles xargs arm-none-eabi-gcc -mfloat-abi=hard -marm -shared -o imtq-api.so`
		- *native*: < `objfiles xargs gcc -shared -o imtq-api.so`
