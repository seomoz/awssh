AWSSH Config
============

Perhaps you've encountered this because you're sick of checking the AWS console
to find the public DNS of the particular machine you're working with. Perhaps 
it's because you work with dozens or hundreds of machines on AWS and simply can't
keep track of them. Or perhaps it's out of shame from _remembering_ the actual
AWS-provided name for your instances.

It's the future, and we can use ssh config. So, where's my flying car?

Installation
============

	sudo python ./setup.py install

Configuration
=============

This package uses boto, which checks for a configuration file `~/.boto`. You can
add your access ID and secret key to that file such:

	[Credentials]
	aws_access_key_id = <your id here>
	aws_secret_access_key = <you get the picture>

If a remote instance uses keypair `production`, then this package assumes that your
keyfile resides locally at `~/.ssh/production`.

Running
=======

	# Easy-peasy
	awssh-config

What it is and does
===================

A quick way to get a list of all your instances by name, and automatically set up
your `~/.ssh/config` to enable you to log into your EC2 instances by name. A few
things to keep in mind:

1. It __will not clobber__ information in existing ssh config
2. Be that as it may, it __does not preserve order__
3. It does __preserves comments__
4. Saves a __backup copy__ at `~/.ssh/config.bak`
5. __Assumes__ key name `production` lives at `~/.ssh/production`
6. It is interruptable without corrupting `~/.ssh/config`

Roadmap
=======

1. Support for multiple AWS accounts
2. Read an optional 'User' tag to designate the username for each machine