# Facebook Open Switching System packaged for Snappy Ubuntu Core.

**Note:** This has only been tested built on Ubuntu 14.04 (with Snapcraft
1.1.0), and run on [Snappy Ubuntu Core][1] 15.04.


## How to build

### Install the latest Snapcraft 1.x

Snapcraft isn't in the archives until Xenial (16.04), so use the
snappy-dev/tools PPA:

    $ sudo add-apt-repository ppa:snappy-dev/tools
    $ sudo apt-get update
    $ sudo apt-get install snapcraft


### Obtain the snap recipe

    $ git clone https://github.com/kyrofa/fboss-snap.git


### Build the snap

    $ cd fboss-snap/
    $ snapcraft

That will pull any prerequisites and build fboss into a snap.


## Test the built snap

If you have a Snappy Ubuntu Core 15.04 machine ready, simply scp the new snap
to that machine and install it:

    $ sudo snappy install fboss_0.1.0_amd64.snap --allow-unauthenticated


[1]: https://developer.ubuntu.com/en/snappy/
