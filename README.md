# Facebook Open Switching System packaged for Snappy Ubuntu Core.

## How to build

### Install the latest Snapcraft 2.x

    $ sudo apt update
    $ sudo apt install snapcraft


### Obtain the snap recipe

    $ git clone https://github.com/wililupy/fboss-snap.git


### Build the snap

    $ cd fboss-snap/
    $ snapcraft

That will pull any prerequisites and build fboss into a snap.


## Test the built snap

If you have a Snappy Ubuntu Core 16.04 machine ready, simply scp the new snap
to that machine and install it:

    $ sudo snap install fboss_0.2.0_amd64.snap --devmode


[1]: https://developer.ubuntu.com/en/snappy/
